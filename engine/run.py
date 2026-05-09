#!/usr/bin/env python3
"""
run.py — SilentWriter CI entry point.

Usage:
    python engine/run.py --repo <owner/repo> --pr <number>

Environment variables required:
    GITHUB_TOKEN        — to fetch the PR diff from GitHub API
    WATSONX_API_KEY     — optional, enables real Granite analysis
    WATSONX_PROJECT_ID  — optional, required alongside WATSONX_API_KEY
"""

import os
import sys
import argparse
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


def format_report(result: dict) -> str:
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

    violations = result.get("violations", [])
    if not violations:
        lines.append("✅ No violations detected. All architectural rules pass.")
    else:
        lines.append(f"{'⚠️' if result['verdict'] == 'WARN' else '🛡️'} {len(violations)} violation(s) found:\n")
        for v in violations:
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(v.get("severity", ""), "⚪")
            lines.append(f"  {severity_icon} [{v.get('rule', 'UNKNOWN')}]")
            lines.append(f"     File   : {v.get('file', 'N/A')}")
            lines.append(f"     Issue  : {v.get('message', '')}")
            lines.append("")

    lines.append("═" * 52)
    lines.append("🤫 SilentWriter · github.com/barryguinea224/silentwriter")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="SilentWriter architectural guardian")
    parser.add_argument("--repo", required=True, help="GitHub repo in owner/name format")
    parser.add_argument("--pr", type=int, required=True, help="Pull request number")
    parser.add_argument("--config", default=".silentwriter.yml", help="Path to constitution file")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable is not set.", file=sys.stderr)
        return 1

    # Fetch diff
    try:
        diff = fetch_pr_diff(args.repo, args.pr, token)
    except requests.HTTPError as e:
        print(f"Error fetching PR diff: {e}", file=sys.stderr)
        return 1

    
 
    # Analyse
    try:
        result = analyze_diff_text(diff, config_path=args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Print report (captured by GitHub Action into verdict.txt)
    print(format_report(result))

    # Exit code drives the workflow's Block merge step
    return 0 if result["verdict"] in ("PASS", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
