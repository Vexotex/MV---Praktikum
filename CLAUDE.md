# MV – Maschinennahe Vernetzung: Popcorn-Anlage

Studienprojekt. Wir steuern **ein Modul** einer Popcorn-Produktionsanlage
(Fülltrichter, Förderband, …). Die Kommunikation mit der Anlage läuft
**ausschließlich über einen MQTT-Broker** – es gibt keinen direkten Zugriff auf
die Hardware.

## Zusammenarbeit (wichtig)

- Der Nutzer schreibt den Code **größtenteils selbst** – es ist ein Lernprojekt.
- Claude soll erklären, reviewen, Fragen beantworten und Hinweise geben, aber
  **keine größeren Implementierungen schreiben**, außer es wird explizit danach
  gefragt. Lieber kurze Beispiele/Pseudo-Code als fertige Lösungen.
- Vorhandene `TODO`-Stellen nicht ungefragt ausfüllen.
- Sprache: Deutsch (Code-Bezeichner und Kommentare ebenfalls deutsch).

## Architektur

```
Main.py                    Einstiegspunkt: Verbindung aufbauen, Modul + Automat starten
popcorn/
  config.py                Broker-Adresse, Port, Topic-Namen
  mqtt_verbindung.py       Dünner Wrapper um den MQTT-Client (connect, publish, subscribe)
  komponenten.py           Basisklasse Komponente + Fuelltrichter, Foerderband, …
  schnittstellen.py        Schnittstellen zu den Nachbarmodulen der Anlage (auch über MQTT)
  modul.py                 Modul = Sammlung der Komponenten, verteilt MQTT-Nachrichten
  zustandsautomat.py       Zustände (Enum) + Zustandsautomat(en), steuern das Modul
```

Grundidee:
- Jede **Komponente** kennt ihre eigenen Topics, wertet eingehende Nachrichten
  aus (Sensorwerte → Attribute) und bietet Methoden für Befehle (→ publish).
- **Schnittstellen** bilden den Austausch mit den anderen Modulen der Anlage ab
  (z.B. Übergabe-Signale) – technisch wie Komponenten, nur zeigen sie nach außen.
- Das **Modul** besitzt die Komponenten und Schnittstellen und leitet Nachrichten an die richtige
  Komponente weiter.
- Der **Zustandsautomat** liest nur Zustände/Werte aus dem Modul und ruft
  Befehle auf – er spricht nie direkt mit MQTT.

## Technik

- Python 3
- MQTT-Bibliothek: `paho-mqtt` (`pip install paho-mqtt`)
- Start: `python Main.py`
