from assistant.retrieval import chunk_text


def test_chunk_text_splits_long_text():
    text = "\n\n".join("a paragraph of several words here " * 8 for _ in range(6))
    assert len(chunk_text(text, chunk_size=300, overlap=0)) > 1


def test_chunk_text_keeps_short_text_in_one_chunk():
    assert chunk_text("short text", chunk_size=600, overlap=50) == ["short text"]
