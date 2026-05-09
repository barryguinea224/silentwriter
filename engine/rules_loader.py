"""
SilentWriter Rules Loader
Parses .silentwriter.yml into structured rule objects.
Used by the engine and optionally by the Gradio demo.
"""

import yaml
import fnmatch
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

@dataclass
class SilentRule:
    name: str
    rule_id: str          # "SILENT-001"
    pattern: str          # glob for files
    severity: str         # critical, high, medium, warning
    auto_block: bool
    description: str = ""
    message: str = ""

    # Specific constraints
    forbidden_changes: List[str] = field(default_factory=list)
    required_tests: bool = False
    min_coverage: int = 0
    allow_list: List[str] = field(default_factory=list)
    block_list: List[str] = field(default_factory=list)
    required_files_update: List[str] = field(default_factory=list)
    auto_generate: bool = False

class SilentRules:
    """Loads and queries rules from the constitution."""

    def __init__(self, config_path: str = ".silentwriter.yml"):
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Constitution not found at {config_path}")

        with open(config_path, "r") as fh:
            raw = yaml.safe_load(fh)

        self.mode = raw.get("settings", {}).get("mode", "active")
        self.auto_generate_docs = raw.get("settings", {}).get("auto_generate", {}).get("agents_md", False)

        self.rules: List[SilentRule] = []
        for entry in raw.get("rules", []):
            self.rules.append(SilentRule(
                name=entry.get("name"),
                rule_id=entry.get("id", entry.get("name")),  # fallback
                pattern=entry.get("pattern", "**"),
                severity=entry.get("severity", "medium"),
                auto_block=entry.get("auto_block", False),
                description=entry.get("description", ""),
                message=entry.get("message", ""),
                forbidden_changes=entry.get("forbidden_changes", []),
                required_tests=entry.get("required_tests", False),
                min_coverage=entry.get("min_coverage", 0),
                allow_list=entry.get("allow_list", []),
                block_list=entry.get("block_list", []),
                required_files_update=entry.get("required_files_update", []),
                auto_generate=entry.get("auto_generate", False)
            ))

    def rules_for_file(self, filepath: str) -> List[SilentRule]:
        """Return all rules whose pattern matches the given file path."""
        return [r for r in self.rules if fnmatch.fnmatch(filepath, r.pattern)]
