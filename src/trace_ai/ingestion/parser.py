# src/trace_ai/ingestion/parser.py

from pathlib import Path
from typing import Dict
import pdfplumber

def parse_document(path: Path) -> Dict:
    if path.suffix == ".txt":
        text = path.read_text(encoding="utf-8", errors="ignore")

    elif path.suffix == ".pdf":
        pages = []
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages):
                pages.append({
                    "page": i + 1,
                    "text": page.extract_text() or ""
                })
        text = "\n".join(p["text"] for p in pages)

    else:
        raise ValueError(f"Unsupported format: {path.suffix}")

    return {
        "doc_id": path.stem,
        "source_path": str(path),
        "text": text
    }
