# Dokumenten-Scanner

Python-Service, der einen Hotfolder überwacht, neue Scans ausliest, klassifiziert, ein Report-PDF erzeugt, optional einen Zahlungstermin im Kalender erstellt und das Ergebnis nach OneDrive verschiebt.

## Features
- Watchdog-basierter File-Watcher für Hotfolder (Write-Stabilität berücksichtigt).
- Text-Extraktion via `pdfplumber` oder OCR mit Tesseract (für Bilder/gescannte PDFs).
- LLM-Extraktion via OpenAI API (JSON-Schema-Validierung) mit konfigurierbarem Local-only-Fallback.
- Report-PDF mit Deckblatt + Originalanhang.
- Intelligente, deterministische Dateinamen inkl. Fälligkeits- und Steuer-Flags.
- OneDrive-Upload und optionaler Outlook/Office 365 Kalendertermin über Microsoft Graph (Device Code Flow).
- Logging, Fehlerpfad, Archivpfad.

## Setup
1. **Python**: 3.11+ installieren.
2. **Dependencies**: `pip install -e .[dev]`
3. **Tesseract**
   - Windows: Installer von https://github.com/UB-Mannheim/tesseract/wiki (Pfad in `ocr.tesseract_cmd` setzen, z.B. `C:\\Program Files\\Tesseract-OCR\\tesseract.exe`).
   - Raspberry Pi OS: `sudo apt-get update && sudo apt-get install tesseract-ocr tesseract-ocr-deu`.
4. **.env** (Beispiel):
   ```env
   OPENAI_API_KEY=sk-...
   GRAPH_CLIENT_ID=<Azure-App-ID>
   GRAPH_TENANT_ID=<Tenant-ID>
   ```
5. **config.yaml**: Von `config/config.example.yaml` kopieren und Pfade anpassen.
6. **Hotfolder**: Ordner aus `config` anlegen (`incoming`, `processed`, `failed`, `archive`).
7. **Microsoft Graph Registrieren**
   - App mit Rechte `Files.ReadWrite.All` und `Calendars.ReadWrite` (Delegated) anlegen.
   - Device Code Flow ist in `graph.py` implementiert; beim ersten Start wird ein Code ausgegeben, der auf https://microsoft.com/devicelogin bestätigt wird.

## Starten
- Interaktiv: `python -m document_scanner.cli config/config.example.yaml`
- **Windows-Dienst** (Kurzfassung):
  - NSSM installieren (`nssm install DocumentScanner "python" "-m" "document_scanner.cli" "C:\\Pfad\\config.yaml"`).
  - Dienst starten, Logfile-Pfade im Dienst konfigurieren.
- **systemd (Pi/ Linux)**: Beispielservice `/etc/systemd/system/document-scanner.service`
  ```ini
  [Unit]
  Description=Dokumenten-Scanner
  After=network.target

  [Service]
  ExecStart=/usr/bin/python -m document_scanner.cli /opt/document-scanner/config.yaml
  WorkingDirectory=/opt/document-scanner
  EnvironmentFile=/opt/document-scanner/.env
  Restart=on-failure

  [Install]
  WantedBy=multi-user.target
  ```
  Danach `sudo systemctl daemon-reload && sudo systemctl enable --now document-scanner`.

## Pipeline
1. Watcher erkennt neue Datei, wartet bis die Größe stabil bleibt.
2. Text-Extraktion (PDF/Text oder OCR).
3. LLM-Extraktion mit JSON-Schema (`config/llm_schema.json`), wahlweise deaktivierbar.
4. Report-PDF wird erzeugt und mit Original gemerged.
5. Dateiname via Schema `YYYY-MM-DD__<DocType>__<Sender>__<Amount>__faellig_<YYYY-MM-DD>__tax_<Y/N>.pdf` (bei Kollision `__vN`).
6. Upload nach OneDrive `/Dokumente/<DocType>/<YYYY>/<MM>/`.
7. Falls Fälligkeitsdatum + Betrag vorhanden: Kalendertermin um 09:00 Uhr lokaler Zeit mit IBAN/Referenz/Link.
8. Original wandert nach `archive`, Fehler nach `failed`.

## Tests
- `pytest`

## Datenschutz
- LLM kann über `llm.enabled: false` abgeschaltet werden (nur OCR/Text, keine API Calls).
- IBAN/Referenzen werden nicht geloggt.

## Demo
- Legen Sie ein Sample-PDF nach `hotfolder/incoming`. Innerhalb von ~60s entsteht ein Report im `processed`-Ordner, Upload/Termin erfolgen sofern Graph konfiguriert ist.
