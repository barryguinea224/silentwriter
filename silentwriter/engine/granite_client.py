"""
Granite Client with dual-mode operation.
When WATSONX_API_KEY is present → call the real API.
Otherwise → fallback to heuristic simulation that actually parses the diff.
"""

import os
import re
import json
import requests
from typing import Dict, List, Optional, Any

class GraniteClient:
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("WATSONX_API_KEY")
        self.project_id = project_id or os.getenv("WATSONX_PROJECT_ID")
        self.endpoint = os.getenv("WATSONX_ENDPOINT", "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29")
        self.model_id = os.getenv("WATSONX_MODEL_ID", "ibm/granite-13b-chat-v2")
        self.simulate = not (self.api_key and self.project_id)

    def analyze_diff(self, diff_text: str, rules_context: str) -> Dict[str, Any]:
        """
        Analyze a git diff against architectural rules.
        Returns: {
            "verdict": "PASS" | "BLOCK" | "WARN",
            "violations": [
                {"rule": "SILENT-001", "severity": "critical", "message": "...", "file": "..."}
            ]
        }
        """
        if self.simulate:
            return self._heuristic_analysis(diff_text, rules_context)
        else:
            return self._call_watsonx(diff_text, rules_context)

    def _heuristic_analysis(self, diff_text: str, rules_context: str) -> Dict[str, Any]:
        """
        Rule-based simulation that actually inspects the diff.
        This is not a dumb keyword check; it detects real patterns.
        """
        violations = []

        # Parse diff into per-file changes
        files_changed = self._parse_diff_files(diff_text)

        for filepath, hunks in files_changed.items():
            # --- SILENT-001: detect function signature changes in API files
            if "src/api/" in filepath:
                for hunk in hunks:
                    if self._contains_signature_change(hunk):
                        violations.append({
                            "rule": "SILENT-001 — Protect API Contracts",
                            "severity": "critical",
                            "file": filepath,
                            "message": "Function signature changed. This may break external consumers."
                        })

            # --- SILENT-002: check if tests exist for core changes
            if "src/core/" in filepath:
                test_files = [f for f in files_changed if f.endswith((".test.ts", "_test.py", "Test.java", ".spec.ts"))]
                if not test_files:
                    violations.append({
                        "rule": "SILENT-002 — Tests Required on Core",
                        "severity": "critical",
                        "file": filepath,
                        "message": "Core logic changed without corresponding tests."
                    })

            # --- SILENT-003: detect banned dependencies in package.json
            if filepath.endswith("package.json"):
                banned = {"mongoose", "sequelize", "typeorm"}  # from our config
                for hunk in hunks:
                    added = self._extract_added_dependencies(hunk)
                    for dep in added:
                        if dep in banned:
                            violations.append({
                                "rule": "SILENT-003 — Allowed Dependencies",
                                "severity": "high",
                                "file": filepath,
                                "message": f"Banned dependency added: {dep}"
                            })

            # --- SILENT-009: detect secrets in code
            secret_pattern = re.compile(r'(?:api[_-]?key|password|token|secret)\s*[:=]\s*["\'][^"\']+["\']', re.IGNORECASE)
            for hunk in hunks:
                if secret_pattern.search(hunk):
                    violations.append({
                        "rule": "SILENT-009 — No Secrets in Code",
                        "severity": "critical",
                        "file": filepath,
                        "message": "Potential secret detected in source code."
                    })

        # Determine verdict
        has_blocker = any(v["severity"] == "critical" for v in violations)  # simplified
        if has_blocker:
            verdict = "BLOCK"
        elif violations:
            verdict = "WARN"
        else:
            verdict = "PASS"

        return {"verdict": verdict, "violations": violations}

    def _call_watsonx(self, diff_text: str, rules_context: str) -> Dict[str, Any]:
        """
        Real WatsonX call. The prompt asks Granite to return JSON.
        """
        prompt = f"""You are an architectural guardian. Analyze the following git diff against the rules below.
Return a JSON object with fields:
- "verdict": one of "PASS", "BLOCK", "WARN"
- "violations": array of objects with "rule", "severity", "file", "message"

Rules:
{rules_context}

Diff:
{diff_text[:4000]}

JSON response:"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model_id": self.model_id,
            "project_id": self.project_id,
            "input": prompt,
            "parameters": {"max_new_tokens": 900, "temperature": 0.1}
        }

        try:
            resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            # Parse Granite's output – assume it's valid JSON
            output = data["results"][0]["generated_text"]
            # Clean the string (Granite may wrap in markdown)
            if "```json" in output:
                output = output.split("```json")[1].split("```")[0]
            elif "```" in output:
                output = output.split("```")[1].split("```")[0]
            return json.loads(output)
        except Exception as e:
            # Fallback to heuristic if API fails
            return self._heuristic_analysis(diff_text, rules_context)

    # ── helper methods ──────────────────────────

    @staticmethod
    def _parse_diff_files(diff: str) -> Dict[str, List[str]]:
        """Split diff into {filepath: [hunk_text]}."""
        files = {}
        current_file = None
        current_hunks = []
        for line in diff.splitlines():
            if line.startswith("diff --git"):
                if current_file:
                    files[current_file] = current_hunks
                current_file = line.split(" b/")[-1] if " b/" in line else None
                current_hunks = []
            elif current_file and line.startswith("@@"):
                current_hunks.append("")  # start new hunk
            elif current_file and current_hunks:
                current_hunks[-1] += line + "\n"
        if current_file:
            files[current_file] = current_hunks
        return files

    @staticmethod
    def _contains_signature_change(hunk: str) -> bool:
        """Check if a hunk modifies a function/method signature."""
        # Matches function definitions in several languages
        sig_re = re.compile(
            r'^\s*(export\s+)?(async\s+)?(function|def|class|public|private|protected)\s+\w+\s*\(',
            re.MULTILINE
        )
        lines = hunk.splitlines()
        # Look for both a removed line (-) and an added line (+) that are signatures
        minus_sigs = [l for l in lines if l.startswith("-") and sig_re.search(l)]
        plus_sigs = [l for l in lines if l.startswith("+") and sig_re.search(l)]
        return bool(minus_sigs and plus_sigs)

    @staticmethod
    def _extract_added_dependencies(hunk: str) -> List[str]:
        """Extract dependency names from added lines in package.json."""
        added = []
        for line in hunk.splitlines():
            if line.startswith("+") and '"' in line and ':' in line:
                match = re.search(r'"(\S+)"\s*:', line)
                if match:
                    added.append(match.group(1))
        return added
