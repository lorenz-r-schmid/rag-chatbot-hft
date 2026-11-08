RAG-Chatbot zur Vorlesung Künstliche Intelligenz



Chatbot, der Fragen zu drei Foliensätzen (Maschinelles Lernen, neuronale Netze) beantwortet. Er sucht passende Folien und lässt das Sprachmodell Gemini daraus die Antwort formulieren (RAG).



Hinweis: Diese README wurde mit KI-Unterstützung erstellt.



Ordner

code/: Python-Skripte und Prompt

docs/: Foliensätze als PDF

data/: gespeicherter Index

logs/: Protokolle der Dialoge

Einrichtung



1\. Voraussetzungen: Python 3.10 oder neuer, Git, VS Code (empfohlen).



2\. Repository holen und Pakete installieren:



git clone <URL-DES-REPOSITORYS>

cd rag-chatbot

pip install -r requirements.txt



3\. API-Key besorgen: Benötigt wird ein Gemini-API-Key von Google (kostenlos, keine Zahlungsdaten). Er wird für Chat- und Embedding-Modell verwendet, weitere Keys sind nicht nötig.



Auf https://aistudio.google.com/apikey mit einem Google-Konto anmelden.

Create API key wählen und den Key kopieren.



Jede Person nutzt einen eigenen Key, weil die Limits pro Projekt gelten.



4\. API-Key eintragen: Die Skripte lesen den Key aus der Umgebungsvariable GEMINI\_API\_KEY. Unter Windows:



setx GEMINI\_API\_KEY "DEIN\_KEY"



Danach VS Code vollständig schließen und neu starten. Der Key darf nicht in Dateien stehen, die ins Repository gelangen.



Benutzung



Im Ordner code/:



python chat.py



Eine leere Eingabe beendet das Programm. Das Protokoll liegt danach in logs/. Der Index in data/ liegt bereits vor. Nur wenn sich die Dokumente oder das Chunking ändern, muss er mit python embeddings.py neu aufgebaut werden (dauert einige Minuten).



Häufige Probleme

KeyError: 'GEMINI\_API\_KEY': Nach setx VS Code neu starten.

404 bei einem Modell: Modell ist nicht verfügbar. Mit python modelle.py die verfügbaren Modelle anzeigen und den Namen in chat.py bzw. embeddings.py anpassen.

Fehler 429: Limit des kostenlosen Zugangs erreicht, kurz warten.

