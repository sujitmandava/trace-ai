# src/trace_ai/checklists/loader.py

import yaml
from pathlib import Path
from typing import Dict


def load_checklist(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(path)

    with open(path, "r") as f:
        checklist = yaml.safe_load(f)

    required_fields = ["checklist_id", "doc_type", "version", "items"]
    for field in required_fields:
        if field not in checklist:
            raise ValueError(f"Missing field in checklist: {field}")

    return checklist
