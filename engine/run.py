#!/usr/bin/env python3
"""
SilentWriter CI entry point.
Usage: python run.py --pr <number> --repo <owner/name>
Requires GITHUB_TOKEN env var to call GitHub API.
"""

import os
import sys
import requests
from diff_analyzer import analyze_diff_text

def fetch_pr_diff(repo: str, pr_number: int, token: str) -> str:
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr", type=int, required=True)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    diff = fetch_pr_diff(args.repo, args.pr, token)
    result = analyze_diff_text(diff)

    print(f"Verdict: {result['verdict']}")
    for v in result.get("violations", []):
        print(f"- {v['rule']}: {v['message']}")

    sys.exit(0 if result["verdict"] == "PASS" else 1)
