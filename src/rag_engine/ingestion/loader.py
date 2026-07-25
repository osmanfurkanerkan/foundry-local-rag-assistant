from pathlib import Path


def load_raw_documents(raw_dir: Path) -> list[tuple[str, str]]:
    """`raw_dir` altindaki her .md dosyasini (kaynak_adi, ham_metin) olarak okur."""
    documents = []
    for file_path in sorted(raw_dir.glob("*.md")):
        text = file_path.read_text(encoding="utf-8")
        documents.append((file_path.stem, text))
    return documents
