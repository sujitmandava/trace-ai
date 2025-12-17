# src/trace_ai/observability/logger.py

import json
from pathlib import Path
from datetime import datetime
from typing import Dict


class AuditLogger:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, record: Dict):
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            **record
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(record) + "\n")
