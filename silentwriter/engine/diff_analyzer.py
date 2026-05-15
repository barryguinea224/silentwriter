"""
diff_analyzer.py — Orchestrates rules loading, Granite call, and report formatting.
Part of the SilentWriter engine.

Used by:
  - run.py        (GitHub Action CI)
  - app.py        (Hugging Face demo)
"""

from rules_loader import SilentRules, SilentRule
from granite_client import GraniteClient
from typing import Dict, List


def build_rules_context(rules: List[SilentRule]) -> str:
    """
    Format active rules into a human-readable block for the Granite prompt.
    Each rule gets its ID, severity, description, and key constraints.
    """
    lines = []
    for r in rules:
        lines.append(f"[{r.rule_id}] {r.name} (severity: {r.severity})")
        if r.description:
            lines.append(f"  Description: {r.description}")
        if r.forbidden_changes:
            lines.append(f"  Forbidden changes: {', '.join(r.forbidden_changes)}")
        if r.block_list:
            lines.append(f"  Blocked values: {', '.join(r.block_list)}")
        if r.required_tests:
            lines.append(f"  Requires tests (min coverage: {r.min_coverage}%)")
        if r.required_files_update:
            lines.append(f"  Must also update: {', '.join(r.required_files_update)}")
        lines.append("")
    return "\n".join(lines)


def analyze_diff_text(
    diff_text: str,
    config_path: str = ".silentwriter.yml",
) -> Dict:
    """
    Main entry point: given a raw git diff string, return verdict + violations.

    Returns:
        {
            "verdict": "PASS" | "WARN" | "BLOCK",
            "violations": [
                {"rule": "SILENT-001", "severity": "critical", "file": "...", "message": "..."}
            ],
            "mode": "simulation" | "watsonx"
        }
    """
    # Load constitution
    rules_engine = SilentRules(config_path)

    # Build rules context for Granite
    rules_context = build_rules_context(rules_engine.rules)

    # Call Granite (real or simulated)
    client = GraniteClient()
    result = client.analyze_diff(diff_text, rules_context)

    # Tag the mode so the caller knows which path was taken
    result["mode"] = "simulation" if client.simulate else "watsonx"

    return result
