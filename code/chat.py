import sys
import time
from datetime import datetime
from pathlib import Path

from google.genai import types

from embeddings import client
from retrieval import load_index, retrieve

CHAT_MODEL = "gemini-3.5-flash-lite"
TOP_K = 4
MIN_SCORE = 0.0      # 0 = kein Schwellwert
TEMPERATURE = 0.0    # reproduzierbare Antworten für die Evaluation
MAX_HISTORY = 6      # Anzahl früherer Frage-Antwort-Paare im Gespräch
NO_ANSWER = "Dazu enthalten die Unterlagen keine Information."

CODE_DIR = Path(__file__).parent
PROMPT_FILE = CODE_DIR / "prompt_v1.txt"
LOG_DIR = CODE_DIR.parent / "logs"


def format_pages(pages):
    first, last = pages[0], pages[-1]
    return f"Seite {first}" if first == last else f"Seite {first}-{last}"


def build_message(question, hits):
    # Abgerufene Chunks als Kontext vor die Frage stellen
    parts = []
    for i, hit in enumerate(hits, start=1):
        parts.append(f"[Auszug {i}: {hit['source']}, {format_pages(hit['pages'])}]\n{hit['text']}")
    context = "\n\n".join(parts)
    return f"Auszüge aus den Vorlesungsfolien:\n\n{context}\n\nFrage: {question}"


def generate(system_prompt, history, message, retries=3):
    # Frühere Fragen und Antworten (ohne Kontext) plus die aktuelle Nachricht senden
    contents = []
    for question, answer in history[-MAX_HISTORY:]:
        contents.append(types.Content(role="user", parts=[types.Part(text=question)]))
        contents.append(types.Content(role="model", parts=[types.Part(text=answer)]))
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))
    config = types.GenerateContentConfig(system_instruction=system_prompt, temperature=TEMPERATURE)
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=CHAT_MODEL, contents=contents, config=config)
            return response.text or "(keine Antwort erhalten)"
        except Exception as error:
            wait = 5 * 2 ** attempt
            print(f"Fehler: {error} - neuer Versuch in {wait} s")
            time.sleep(wait)
    raise RuntimeError("Antwort fehlgeschlagen")


def answer_question(question, vectors, chunks, history, system_prompt):
    hits = retrieve(question, vectors, chunks, top_k=TOP_K)
    used = [hit for hit in hits if hit["score"] >= MIN_SCORE]
    if not used:
        return NO_ANSWER, hits
    answer = generate(system_prompt, history, build_message(question, used))
    return answer, hits


def open_log(label):
    # Protokolldatei mit den Einstellungen im Kopf anlegen
    LOG_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = LOG_DIR / f"{stamp}_{label}.md"
    header = [
        f"# Dialogprotokoll: {label}",
        "",
        f"- Datum: {datetime.now():%d.%m.%Y %H:%M}",
        f"- Chat-Modell: {CHAT_MODEL}",
        f"- Prompt-Datei: {PROMPT_FILE.name}",
        f"- Top-K: {TOP_K}",
        f"- Mindest-Score: {MIN_SCORE}",
        f"- Temperatur: {TEMPERATURE}",
        "",
        "",
    ]
    path.write_text("\n".join(header), encoding="utf-8")
    return path


def log_turn(path, number, question, hits, answer):
    # Nach jeder Frage anhängen, damit bei einem Abbruch nichts verloren geht
    lines = [f"## Frage {number}", "", question, "", "Abgerufene Chunks:"]
    for hit in hits:
        status = "" if hit["score"] >= MIN_SCORE else " (unter Mindest-Score)"
        lines.append(f"- {hit['score']:.3f} {hit['source']}, {format_pages(hit['pages'])}{status}")
    lines += ["", "Antwort:", "", answer, "", ""]
    with path.open("a", encoding="utf-8") as file:
        file.write("\n".join(lines))


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "dialog"
    system_prompt = PROMPT_FILE.read_text(encoding="utf-8").strip()
    vectors, chunks = load_index()
    log_path = open_log(label)
    history = []
    print(f"Protokoll: {log_path.name}")
    while True:
        question = input("\nFrage (leer = Ende): ").strip()
        if not question:
            break
        answer, hits = answer_question(question, vectors, chunks, history, system_prompt)
        print(f"\n{answer}")
        history.append((question, answer))
        log_turn(log_path, len(history), question, hits, answer)


if __name__ == "__main__":
    main()