# LaTeX Gerüst zur Doku des Delivery Moduls
## How
Die Doku liegt als LaTeX in `docs/`:
- `main.tex` -> Layout, Deckblatt (Namen, Matr.-Nr., Semester oben bei den Metadaten), Verzeichnisse, Literatur
- `kapitel/` -> ein File pro Kapitel, gegliedert nach `Inhalt_Dokumentation.txt`
- `abbildungen/` -> Bilder hier ablegen

Diagramme (Zustandsautomat, Topologie, Zeitverläufe) sind direkt in TikZ gezeichnet, also kein extra Tool nötig.  

Das `compile` Skript baut daraus `docs/main.pdf`:  
ist LaTeX lokal installiert (`latexmk`/`pdflatex`), wird das genommen. Sonst läuft der Build in einem Docker Container (Image `texlive/texlive`).

## Usage (Linux/ MacOS) tja blöd gelaufen Jan
Wer LaTeX lokal hat (z.B. `brew install --cask mactex-no-gui`), kann Schritt 1 und 2 überspringen ^^

1. Installiere Colima (https://colima.run/) und die Docker CLI  
mit brew:
```
brew install colima docker
```
  (Colima startet nur die VM, das `docker` Kommando kommt extra)

2. Starte `colima`
```
colima start
```
  falls Problem:
```
colima restart
```

3. Führe compile Skript aus (beim ersten Mal dauert bissl, das Image ist mehrere GB groß)
```
./docs/compile
```
Erwarteter Output:
```
[...]
Output written on main.pdf (18 pages, 218683 bytes).
Transcript written on main.log.
Latexmk: Getting log file 'main.log'
Latexmk: Examining 'main.fls'
Latexmk: Examining 'main.log'
Latexmk: Log file says output to 'main.pdf'
Latexmk: All targets (main.pdf) are up-to-date
-rw-r--r--  1 user  staff   213K Nov 13 12:49 main.pdf
```
  -> PDF liegt in `docs/main.pdf`

4. Weitere Optionen
```
./docs/compile abgabe=true
```
  -> PDF heißt dann `<Datum>_MV-Praktikum_Delivery.pdf`
```
./docs/compile rebuild
```
  -> alles neu bauen, falls Änderungen nicht übernommen werden
```
./docs/compile clean
```
 -> nur Hilfsdateien löschen
