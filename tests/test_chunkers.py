from rag_engine.ingestion.fixed_size_chunker import FixedSizeChunker
from rag_engine.ingestion.markdown_chunker import MarkdownChunker


def test_fixed_size_chunker_returns_empty_list_for_empty_text():
    assert FixedSizeChunker().chunk("doc-a", "") == []


def test_fixed_size_chunker_splits_by_word_count_with_overlap():
    text = " ".join(f"kelime{i}" for i in range(10))
    chunker = FixedSizeChunker(chunk_size=4, overlap=1)

    chunks = chunker.chunk("doc-a", text)

    assert len(chunks) > 1
    assert all(chunk.source == "doc-a" for chunk in chunks)
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))
    # Ardisik chunk'lar overlap kadar kelimeyi paylasmali.
    first_words = chunks[0].text.split()
    second_words = chunks[1].text.split()
    assert first_words[-1] == second_words[0]


def test_fixed_size_chunker_rejects_overlap_greater_or_equal_to_chunk_size():
    import pytest

    with pytest.raises(ValueError):
        FixedSizeChunker(chunk_size=10, overlap=10)


def test_markdown_chunker_splits_on_headers():
    text = "# Baslik Bir\n\nBirinci bolum metni.\n\n# Baslik Iki\n\nIkinci bolum metni."

    chunks = MarkdownChunker(chunk_size=1000, overlap=0).chunk("doc-a", text)

    sources = {chunk.source for chunk in chunks}
    assert sources == {"doc-a"}
    assert len(chunks) >= 2
    joined = " ".join(chunk.text for chunk in chunks)
    assert "Birinci bolum metni." in joined
    assert "Ikinci bolum metni." in joined
