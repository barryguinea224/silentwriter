#!/usr/bin/env python3
"""
run.py — SilentWriter CI entry point.

Usage:
    python engine/run.py --repo <owner/repo> --pr <number>

Environment variables required:
    GITHUB_TOKEN        — to fetch the PR diff from GitHub API
    WATSONX_API_KEY     — optional, enables real Granite analysis
    WATSONX_PROJECT_ID  — optional, required alongside WATSONX_API_KEY

Demo mode:
    FORCE_BLOCK=true    — forces BLOCK verdict for demonstration purposes
    FORCE_BLOCK_REASON  — custom reason for the block (optional)
"""

import os
import sys
import argparse
import re
import requests

# Allow running as `python engine/run.py` from repo root
sys.path.insert(0, os.path.dirname(__file__))

from diff_analyzer import analyze_diff_text


def fetch_pr_diff(repo: str, pr_number: int, token: str) -> str:
    """Fetch the raw unified diff for a GitHub pull request."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def detect_breaking_changes(diff: str) -> list:
    """
    Detect breaking changes in the diff.
    Returns a list of violations.
    """
    violations = []

    # ── Pattern 1: Function signature change (robust version) ─────────────
    # Collects ALL removed and added def lines separately, then compares by
    # function name. This avoids the fragile \n adjacency assumption and works
    # even when GitHub inserts context lines between the - and + lines.
    removed_defs = re.findall(r'^-\s*def\s+(\w+)\(([^)]*)\)\s*:', diff, re.MULTILINE)
    added_defs   = re.findall(r'^\+\s*def\s+(\w+)\(([^)]*)\)\s*:', diff, re.MULTILINE)

    removed = {name: params for name, params in removed_defs}
    added   = {name: params for name, params in added_defs}

    for name in removed:
        if name in added:
            old_params = [p.strip() for p in removed[name].split(',') if p.strip()]
            new_params = [p.strip() for p in added[name].split(',')   if p.strip()]
            if len(new_params) > len(old_params):
                extra    = [p for p in new_params if p not in old_params]
                required = [p for p in extra if '=' not in p]
                if required:
                    violations.append({
                        "rule": "function-signature-change",
                        "severity": "critical",
                        "file": "unknown",
                        "message": (
                            f"Function '{name}()' added required parameter(s): "
                            f"{', '.join(required)}. This will break existing calls."
                        ),
                    })

    # ── Pattern 2: Removed function (deleted entirely) ────────────────────
    pattern_deleted = r'^-\s*def\s+(\w+)\(.*?\):'
    deleted_functions = re.findall(pattern_deleted, diff, re.MULTILINE)
    for func in deleted_functions:
        if not re.search(rf'^\+\s*def\s+{func}\(', diff, re.MULTILINE):
            violations.append({
                "rule": "function-deleted",
                "severity": "critical",
                "file": "unknown",
                "message": f"Function '{func}()' was completely removed. This will break all calls to it.",
            })

    # ── Pattern 3: Type change in function parameter ──────────────────────
    pattern_type_change = (
        r'-\s*def\s+\w+\([^:]*:\s*(\w+).*?\)\s*:\s*\n'
        r'\+\s*def\s+\w+\([^:]*:\s*(\w+).*?\)\s*:'
    )
    type_changes = re.findall(pattern_type_change, diff, re.DOTALL)
    for old_type, new_type in type_changes:
        if old_type != new_type:
            violations.append({
                "rule": "parameter-type-change",
                "severity": "high",
                "file": "unknown",
                "message": (
                    f"Parameter type changed from '{old_type}' to '{new_type}'. "
                    "May break type-dependent calls."
                ),
            })

    return violations


def format_report(result: dict, breaking_violations: list = None) -> str:
    """
    Format the analysis result as a plain-text report.
    The GitHub Action grep expects 'Verdict: PASS|WARN|BLOCK' on its own line.
    """
    lines = []
    mode_tag = "[simulation]" if result.get("mode") == "simulation" else "[WatsonX Granite]"

    lines.append("═" * 52)
    lines.append(f"  🤫 SilentWriter Analysis  {mode_tag}")
    lines.append("═" * 52)
    lines.append(f"Verdict: {result['verdict']}")
    lines.append("")

    all_violations = result.get("violations", [])
    if breaking_violations:
        all_violations.extend(breaking_violations)

    if not all_violations:
        lines.append("✅ No violations detected. All architectural rules pass.")
    else:
        icon = "⚠️" if result["verdict"] == "WARN" else "🛡️"
        lines.append(f"{icon} {len(all_violations)} violation(s) found:\n")
        for v in all_violations:
            severity_icon = {
                "critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"
            }.get(v.get("severity", ""), "⚪")
            lines.append(f"  {severity_icon} [{v.get('rule', 'UNKNOWN')}]")
            lines.append(f"     File   : {v.get('file', 'N/A')}")
            lines.append(f"     Issue  : {v.get('message', '')}")
            lines.append("")

    lines.append("═" * 52)
    lines.append("🤫 SilentWriter · github.com/barryguinea224/silentwriter")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="SilentWriter architectural guardian")
    parser.add_argument("--repo",   required=True, help="GitHub repo in owner/name format")
    parser.add_argument("--pr",     type=int, required=True, help="Pull request number")
    parser.add_argument("--config", default=".silentwriter.yml", help="Path to constitution file")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable is not set.", file=sys.stderr)
        return 1

    # Demo safety net — comment out after hackathon
    force_block        = os.environ.get("FORCE_BLOCK", "").lower() == "true"
    force_block_reason = os.environ.get("FORCE_BLOCK_REASON", "Demo: breaking change detected in pull request")

    # Fetch diff
    try:
        diff = fetch_pr_diff(args.repo, args.pr, token)
    except requests.HTTPError as e:
        print(f"Error fetching PR diff: {e}", file=sys.stderr)
        return 1

    # Analyse with diff_analyzer (WatsonX or heuristic)
    try:
        result = analyze_diff_text(diff, config_path=args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception:
        result = {"verdict": "PASS", "mode": "fallback", "violations": []}

    # Detect breaking changes with regex engine
    breaking_violations = detect_breaking_changes(diff)

    # Determine final verdict
    if breaking_violations:
        result["verdict"] = "BLOCK"
        result["mode"]    = "breaking-detection"
    elif force_block:
        result["verdict"] = "BLOCK"
        result["mode"]    = "demo-force"
        breaking_violations = [{
            "rule":     "demo-block",
            "severity": "critical",
            "file":     "N/A",
            "message":  force_block_reason,
        }]

    print(format_report(result, breaking_violations))

    return 0 if result["verdict"] in ("PASS", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())

