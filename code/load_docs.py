import logging
import re
from pathlib import Path
from pypdf import PdfReader

# Warnungen zu beschädigten Objektverweisen in den PDFs ausblenden
logging.getLogger("pypdf").setLevel(logging.ERROR)

# Hauptverzeichnis ist der Ordner über code/
ROOT = Path(__file__).parent.parent
DOCS_DIR = ROOT / "docs"

# Wiederkehrende Elemente der Folienvorlage, die keinen Inhalt tragen
NOISE_PATTERNS = [
    re.compile(r"(Hochschule\s*f[üu]r\s*Technik\s*Stuttgart\s*)+"),  # Kopfzeile
    re.compile(r"Vorlesung\s+Künstliche\s+Intelligenz\s*Ulrike\s+Pado"),  # Titelfolien-Zusatz
    re.compile(r"(?m)^[ \t]*[!?]+[ \t]*$\n?"),                        # Zeilen, die nur aus ! oder ? bestehen
    re.compile(r"(?m)^.*(?:[A-Za-zÄÖÜäöüß]%|%[A-Za-zÄÖÜäöüß]).*$\n?"),  # Text aus Grafiken mit Kodierfehler
    re.compile(r"(?m)^[ \t]*%+[ \t]*$\n?"),                             # Zeilen, die nur aus % bestehen
]

def clean_text(text):
    """Entfernt wiederkehrende Vorlagen-Elemente und überflüssige Leerzeilen."""
    for pattern in NOISE_PATTERNS:
        text = pattern.sub("", text)
    return re.sub(r"\n{2,}", "\n", text).strip()

def load_pdf(path):
    """Liest alle Seiten eines PDFs und markiert jede Seite mit ihrer Nummer."""
    reader = PdfReader(path)
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        # Seiten ohne Text (z. B. reine Bilder) ergeben einen leeren String
        text = clean_text(page.extract_text() or "")
        pages.append(f"[Seite {number}]\n{text}")
    return "\n".join(pages)

def load_docs():
    """Gibt eine Liste aus (Dateiname, Text) für alle PDF- und TXT-Dateien zurück."""
    docs = []
    for path in sorted(DOCS_DIR.iterdir()):
        if path.suffix.lower() == ".pdf":
            text = load_pdf(path)
        elif path.suffix.lower() == ".txt":
            text = path.read_text(encoding="utf-8")
        else:
            # Alle anderen Dateitypen werden übersprungen
            continue
        docs.append((path.name, text))
    return docs


if __name__ == "__main__":
    out_path = ROOT / "data" / "loaded_docs.txt"
    out_path.parent.mkdir(exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for name, text in load_docs():
            print(f"{name}: {len(text)} Zeichen")
            f.write(f"===== {name} =====\n{text}\n\n")
    print(f"Gesamttext gespeichert: {out_path}")