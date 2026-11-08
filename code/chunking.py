import re

from load_docs import load_docs

# Folien mit weniger Zeichen werden mit der nächsten Folie zusammengelegt
MIN_CHARS = 100

PAGE_PATTERN = re.compile(r"\[Seite (\d+)\]\n")


def split_pages(text):
    """Zerlegt einen Dokumenttext in eine Liste aus (Seitennummer, Seitentext)."""
    # split() liefert: ['', '1', 'Text 1', '2', 'Text 2', ...]
    parts = PAGE_PATTERN.split(text)
    return [(int(parts[i]), parts[i + 1].strip()) for i in range(1, len(parts), 2)]


def chunk_doc(source, text):
    """Bildet pro Folie einen Chunk und legt sehr kurze Folien zusammen."""
    chunks = []
    buffer = []  # gesammelte (Seitennummer, Text) der noch zu kurzen Folien

    for number, page_text in split_pages(text):
        buffer.append((number, page_text))
        length = sum(len(t) for _, t in buffer)
        if length >= MIN_CHARS:
            chunks.append(make_chunk(source, buffer))
            buffer = []

    # Reste am Ende an den letzten Chunk hängen (oder eigener Chunk, falls keiner existiert)
    if buffer:
        if chunks:
            last = chunks.pop()
            chunks.append(make_chunk(source, last["pages"] + buffer))
        else:
            chunks.append(make_chunk(source, buffer))
    return chunks


def make_chunk(source, pages):
    """Baut aus einer Liste von Seiten einen Chunk mit Quelle und Seitenmarkern."""
    text = "\n".join(f"[Seite {number}]\n{t}" for number, t in pages)
    return {"source": source, "pages": pages, "text": text}


def chunk_all():
    """Erzeugt die Chunks aller Dokumente."""
    chunks = []
    for source, text in load_docs():
        chunks.extend(chunk_doc(source, text))
    return chunks


if __name__ == "__main__":
    chunks = chunk_all()
    print(f"{len(chunks)} Chunks")
    for i, chunk in enumerate(chunks):
        first, last = chunk["pages"][0][0], chunk["pages"][-1][0]
        print(f"--- Chunk {i}: {chunk['source']}, Seite {first}-{last}, {len(chunk['text'])} Zeichen")
        print(chunk["text"])