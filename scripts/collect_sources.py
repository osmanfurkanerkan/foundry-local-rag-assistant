"""Faz 1.1: Bilgi tabani icin Microsoft Learn sayfalarini toplama.

Amac: Asagidaki URL listesindeki her sayfayi indirip, sadece asil icerik
kismini (menu/navigasyon olmadan) markdown olarak data/raw/ altina kaydetmek.

Kullanim: .venv/Scripts/python.exe scripts/collect_sources.py
"""
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

SOURCES = [
    "https://learn.microsoft.com/en-us/azure/foundry-local/what-is-foundry-local",
    "https://learn.microsoft.com/en-us/azure/foundry-local/get-started",
    "https://learn.microsoft.com/en-us/azure/foundry-local/concepts/foundry-local-architecture",
    "https://learn.microsoft.com/en-us/azure/foundry-local/reference/reference-cli",
    "https://learn.microsoft.com/en-us/azure/foundry/concepts/retrieval-augmented-generation",
    "https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview",
    "https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-solution-design-and-evaluation-guide",
    "https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/understand-embeddings",
    "https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/embeddings",
    "https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-generate-embeddings",
]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; RAG-project-collector/1.0)"}


def slugify(url: str) -> str:
    tail = url.rstrip("/").split("/")[-1]
    return re.sub(r"[^a-z0-9\-]", "", tail.lower())


def extract_main_content(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Untitled"

    # Sayfada birden fazla `div.content` olabiliyor (ör. bos bir baslik kutusu +
    # asil govde); metni en uzun olani gercek makale govdesidir.
    candidates = soup.find_all("div", class_="content")
    if not candidates:
        main = soup.find(attrs={"data-bi-name": "content"}) or soup.find("main") or soup.find("article")
        candidates = [main] if main else []
    if not candidates:
        raise ValueError("Ana icerik alani bulunamadi")
    content = max(candidates, key=lambda tag: len(tag.get_text()))

    for junk in content.select("nav, script, style, [hidden]"):
        junk.decompose()

    markdown_text = markdownify(str(content), heading_style="ATX")
    markdown_text = re.sub(r"\n{3,}", "\n\n", markdown_text).strip()
    return title, markdown_text


def fetch_and_save(url: str) -> None:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    response.encoding = "utf-8"

    title, markdown_text = extract_main_content(response.text)

    filename = f"{slugify(url)}.md"
    file_path = RAW_DIR / filename
    file_content = f"# {title}\n\nKaynak: {url}\n\n{markdown_text}\n"
    file_path.write_text(file_content, encoding="utf-8")

    print(f"  kaydedildi: {filename} ({len(markdown_text)} karakter)")


if __name__ == "__main__":
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"{len(SOURCES)} sayfa indirilecek -> {RAW_DIR}\n")

    for url in SOURCES:
        print(f"indiriliyor: {url}")
        try:
            fetch_and_save(url)
        except Exception as exc:
            print(f"  HATA: {exc}")
        time.sleep(1)

    print("\nTamamlandi.")
