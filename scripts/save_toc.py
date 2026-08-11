#!/usr/bin/env python3
"""Generate .toc.json sidecar for an already-ingested PDF.
Run: python3 scripts/save_toc.py raw/sources/AIP_17july2026.pdf"""
import json
import sys
from pathlib import Path


def save_toc(pdf_path: str):
    path = Path(pdf_path)
    if not path.exists():
        print(f"Error: {pdf_path} not found")
        return

    import fitz
    doc = fitz.open(str(path))
    raw_toc = doc.get_toc(simple=False)
    page_count = doc.page_count

    toc_entries = []
    for entry in raw_toc:
        toc_entries.append({
            "level": entry[0],
            "title": entry[1].strip(),
            "page": entry[2],
        })

    doc.close()

    toc_data = {
        "source": path.name,
        "total_pages": page_count,
        "entries": toc_entries,
    }

    toc_path = path.with_suffix(".toc.json")
    toc_path.write_text(json.dumps(toc_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(toc_entries)} TOC entries to {toc_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/save_toc.py <path/to/file.pdf>")
        sys.exit(1)
    save_toc(sys.argv[1])
