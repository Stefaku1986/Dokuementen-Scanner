# Super einfache Anleitung: Dokumenten-Scanner einrichten

Diese Schritte sind so erklärt, dass auch ein 10-Jähriger sie nacheinander erledigen kann. Folge jedem Punkt genau und frage einen Erwachsenen, wenn du etwas nicht verstehst.

## 1. Was du brauchst
- Einen Computer mit Windows 10/11 **oder** einen Raspberry Pi mit Raspberry Pi OS.
- Internet, damit du Programme herunterladen kannst.
- Eine Maus und Tastatur.
- Einen Scanner, der Dateien (PDF oder Bilder) in einen Ordner speichern kann.

## 2. Ordner anlegen
1. Öffne den Datei-Explorer (Windows) oder den Datei-Manager (Raspberry Pi).
2. Lege diese Ordner an (alle in deinem Benutzerordner, zum Beispiel `C:\Users\DEINNAME`):
   - `scanner-hotfolder` (hier legt der Scanner die neuen Dateien ab)
   - `scanner-processed` (fertige Dateien landen hier)
   - `scanner-failed` (hierhin kommen Dateien mit Fehlern)
3. Merke dir die Pfade, du schreibst sie gleich in die Einstellungen.

## 3. Programme installieren
### 3.1 Python 3.11 installieren
- Windows: Gehe auf https://www.python.org/downloads/ und wähle "Download Python 3.11". Klicke beim Installieren auf "Add Python to PATH".
- Raspberry Pi: Öffne ein Terminal und tippe `sudo apt update && sudo apt install -y python3.11 python3.11-venv python3.11-dev`.

### 3.2 Git installieren
- Windows: Lade Git von https://git-scm.com/downloads und klicke dich durch die Installation.
- Raspberry Pi: Im Terminal `sudo apt install -y git`.

### 3.3 Tesseract OCR installieren (für Texte aus Bildern)
- Windows: Lade die Setup-Datei von https://github.com/UB-Mannheim/tesseract/wiki und installiere. Merke dir den Pfad, zum Beispiel `C:\Program Files\Tesseract-OCR\tesseract.exe`.
- Raspberry Pi: Im Terminal `sudo apt install -y tesseract-ocr`.

## 4. Projekt herunterladen
1. Öffne ein Terminal (Windows: "Eingabeaufforderung" oder "PowerShell").
2. Wechsle in deinen Benutzerordner (`cd %USERPROFILE%` auf Windows, `cd ~` auf Raspberry Pi).
3. Lade das Projekt herunter: `git clone https://github.com/dein-nutzername/Dokuementen-Scanner.git`.
4. Öffne den neuen Ordner: `cd Dokuementen-Scanner`.

## 5. Virtuelle Umgebung erstellen und Pakete installieren
1. Erstelle eine neue Umgebung: `python3.11 -m venv .venv`.
2. Aktiviere sie:
   - Windows: `.\.venv\Scripts\activate`
   - Raspberry Pi: `source .venv/bin/activate`
3. Installiere die Pakete: `pip install -U pip` und danach `pip install -e .`.

## 6. Geheime Schlüssel eintragen (.env)
1. Erstelle eine Datei `.env` im Projektordner.
2. Schreibe diese Zeilen hinein (ersetze die Platzhalter in Großbuchstaben):
   ```
   OPENAI_API_KEY=DEIN_OPENAI_SCHLUESSEL
   # Die nächsten Zeilen brauchst du nur, wenn du OneDrive/Kalender nutzen willst.
   GRAPH_CLIENT_ID=DEINE_GRAPH_CLIENT_ID
   GRAPH_TENANT_ID=DEINE_TENANT_ID
   ```
3. Speichere die Datei. Wenn du Graph nicht nutzen willst, lass die letzten beiden Zeilen weg.

## 7. Einstellungen ausfüllen (config.yaml)
1. Kopiere die Beispiel-Datei: `cp config/config.example.yaml config/config.yaml`.
2. Öffne `config/config.yaml` in einem Texteditor.
3. Trage deine Ordnerpfade ein:
   - `input_dir`: Pfad zu `scanner-hotfolder`
   - `processed_dir`: Pfad zu `scanner-processed`
   - `failed_dir`: Pfad zu `scanner-failed`
4. Setze `tesseract_path` (nur Windows) auf den richtigen Installationspfad.
5. Wenn du keine OneDrive- oder Kalender-Anbindung willst, stelle `graph.enabled` auf `false`.
6. Speichere die Datei.

## 8. Prüfen, ob alles funktioniert
1. Stelle sicher, dass die virtuelle Umgebung aktiv ist (du siehst `(.venv)` im Terminal).
2. Starte den kurzen Test: `pytest -q`. Wenn überall "passed" steht, ist alles gut.

## 9. Den Scanner-Dienst starten
- Im Terminal (mit aktivierter Umgebung): `python -m document_scanner.cli config/config.yaml`.
- Lass das Fenster offen. Die App beobachtet jetzt den Hotfolder.

## 10. Ausprobieren
1. Lege eine Beispiel-PDF in `scanner-hotfolder`.
2. Warte einen Moment (maximal 1 Minute).
3. Schau in `scanner-processed`: Dort sollte eine neue PDF mit einem klugen Namen liegen.
4. Öffne die PDF: Die erste Seite ist ein Bericht, dahinter folgt das Original.

## 11. Häufige Fragen
- **Nichts passiert?** Prüfe, ob der Dienst im Terminal läuft und ob der Hotfolder-Pfad richtig ist.
- **Fehler?** Schau in `scanner-failed`. Dort findest du eine Text- oder JSON-Datei mit Hinweisen.
- **OCR langsam?** Große Bilder brauchen länger. Warte etwas oder nutze kleinere Scans.
- **OneDrive oder Kalender verwenden?** Lass einen Erwachsenen helfen, die Microsoft-Anmeldung zu machen (Device Code Flow). Danach kannst du `graph.enabled` auf `true` setzen.

## 12. Service automatisch starten (optional)
- **Windows:** Suche nach "Aufgabenplanung" und erstelle eine Aufgabe, die beim Anmelden `python -m document_scanner.cli C:\\Pfad\\zu\\config.yaml` ausführt (mit aktiviertem `.venv`).
- **Raspberry Pi:** Erstelle eine `systemd`-Service-Datei, die beim Booten denselben Befehl startet. Bitte einen Erwachsenen um Hilfe.

Fertig! Jetzt verarbeitet die App automatisch neue Scans und erstellt Berichte.
