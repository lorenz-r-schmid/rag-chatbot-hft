import json
from pathlib import Path

import numpy as np

from embeddings import embed_query

DATA_DIR = Path(__file__).parent.parent / "data"
TOP_K = 4


def load_index():
    # Vektoren und zugehörige Chunk-Texte aus data/ laden
    vectors = np.load(DATA_DIR / "vectors.npy")
    chunks = json.loads((DATA_DIR / "chunks.json").read_text(encoding="utf-8"))
    return vectors, chunks


def retrieve(question, vectors, chunks, top_k=TOP_K):
    # Ähnlichkeit zu allen Chunks berechnen und die besten top_k zurückgeben
    query = embed_query(question)
    scores = vectors @ query
    best = np.argsort(scores)[::-1][:top_k]
    return [{"score": float(scores[i]), **chunks[i]} for i in best]


if __name__ == "__main__":
    vectors, chunks = load_index()
    while True:
        question = input("Frage (leer = Ende): ").strip()
        if not question:
            break
        for hit in retrieve(question, vectors, chunks):
            print(f"\n{hit['score']:.3f}  {hit['source']}, Seite {hit['pages'][0]}-{hit['pages'][-1]}")
            print(hit["text"][:200].replace("\n", " "))
        print()