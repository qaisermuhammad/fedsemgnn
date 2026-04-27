from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    for page_index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        parts.append(f"\n\n===== PAGE {page_index + 1} / {len(reader.pages)} =====\n")
        parts.append(text)
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=str, help="Path to PDF")
    parser.add_argument("--out", type=str, required=True, help="Output text file path")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    text = extract_text(pdf_path)
    out_path.write_text(text, encoding="utf-8", errors="replace")

    print(f"Extracted {len(text):,} characters from: {pdf_path}")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
