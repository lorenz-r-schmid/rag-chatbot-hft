import json
import os
import time
from pathlib import Path

import numpy as np
from google import genai
from google.genai import types

from chunking import chunk_all

EMBED_MODEL = "gemini-embedding-2"
BATCH_SIZE = 10
DATA_DIR = Path(__file__).parent.parent / "data"

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(timeout=30000),
)


def normalize(vectors):
    # Jeden Vektor auf Länge 1 skalieren
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def embed_text(text, retries=3):
    # Einen einzelnen Text einbetten, mit Wiederholung bei Fehlern
    for attempt in range(retries):
        try:
            response = client.models.embed_content(model=EMBED_MODEL, contents=text)
            return np.array(response.embeddings[0].values)
        except Exception as error:
            wait = 5 * 2 ** attempt
            print(f"Fehler: {error} - neuer Versuch in {wait} s")
            time.sleep(wait)
    raise RuntimeError("Embedding fehlgeschlagen")


def embed_documents(chunks):
    # Dokument-Präfix laut Vorgabe des Embedding-Modells
    vectors = []
    for i, chunk in enumerate(chunks, start=1):
        vectors.append(embed_text(f"title: none | text: {chunk['text']}"))
        print(f"{i}/{len(chunks)} eingebettet")
        time.sleep(4)  # Rate-Limit (15 Anfragen pro Minute) einhalten
    return normalize(np.vstack(vectors))


def embed_query(question):
    # Query-Präfix: Fragen werden anders eingebettet als Dokumente
    vector = embed_text(f"task: search result | query: {question}")
    return vector / np.linalg.norm(vector)


def build_index():
    chunks = chunk_all()
    vectors = embed_documents(chunks)
    DATA_DIR.mkdir(exist_ok=True)
    np.save(DATA_DIR / "vectors.npy", vectors)
    # Seitenlisten als Zahlenpaare speichern, damit JSON sie lesen kann
    meta = [{"source": c["source"], "pages": [p for p, _ in c["pages"]], "text": c["text"]} for c in chunks]
    (DATA_DIR / "chunks.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Index gespeichert:", vectors.shape)


if __name__ == "__main__":
    build_index()