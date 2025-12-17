# src/trace_ai/ingestion/loader.py

from pathlib import Path
from typing import List

def load_documents(path: Path) -> List[Path]:
    if not path.exists():
        raise FileNotFoundError(path)

    docs = []
    for ext in ("*.pdf", "*.txt"):
        docs.extend(path.rglob(ext))

    return docs
