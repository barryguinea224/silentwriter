"""
Diff Analyzer: orchestrates loading rules, calling Granite,
and formatting a report.
"""

from .rules_loader import SilentRules
from .granite_client import GraniteClient
from typing import Dict, Optional

def analyze_diff_text(diff_text: str, config_path: str = ".silentwriter.yml") -> Dict:
    """
    Main entry point: given a git diff, return verdict + violations.
    Used by run.py (GitHub Action) and by app.py (Hugging Face demo).
    """
    rules_engine = SilentRules(config_path)
    # Build a summary of rules for the client
    rules_summary = "\n".join([
        f"- {r.rule_id}: {r.name} (severity {r.severity})" for r in rules_engine.rules
    ])

    client = GraniteClient()
    result = client.analyze_diff(diff_text, rules_summary)

    return result
