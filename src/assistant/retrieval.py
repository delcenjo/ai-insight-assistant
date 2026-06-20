import json
from functools import lru_cache

import numpy as np

from .config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DOCS_DIR,
    EMBEDDING_MODEL,
    INDEX_PATH,
    META_PATH,
    TOP_K,
)


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBEDDING_MODEL)


def embed(texts):
    vectors = _model().encode(list(texts), normalize_embeddings=True, convert_to_numpy=True)
    return np.asarray(vectors, dtype=np.float32)


def load_documents(docs_dir=DOCS_DIR):
    return [
        {"source": path.name, "text": path.read_text(encoding="utf-8")}
        for path in sorted(docs_dir.glob("*.md"))
    ]


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current = [], ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 1 > chunk_size:
            chunks.append(current)
            current = (current[-overlap:] + " " + paragraph) if overlap else paragraph
        else:
            current = f"{current}\n{paragraph}".strip() if current else paragraph
    if current:
        chunks.append(current)
    return chunks


def build_index(docs_dir=DOCS_DIR):
    chunks = []
    for document in load_documents(docs_dir):
        for i, text in enumerate(chunk_text(document["text"])):
            chunks.append({"id": f"{document['source']}#{i}", "source": document["source"], "text": text})
    vectors = embed([chunk["text"] for chunk in chunks])
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(INDEX_PATH, vectors=vectors)
    META_PATH.write_text(json.dumps(chunks, indent=2))
    return len(chunks)


class Retriever:
    def __init__(self):
        self.vectors = np.load(INDEX_PATH)["vectors"]
        self.chunks = json.loads(META_PATH.read_text())

    def search(self, query, top_k=TOP_K):
        scores = self.vectors @ embed([query])[0]
        order = np.argsort(scores)[::-1][:top_k]
        return [
            {"source": self.chunks[i]["source"], "text": self.chunks[i]["text"], "score": float(scores[i])}
            for i in order
        ]
