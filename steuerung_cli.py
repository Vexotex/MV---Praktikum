"""Manuelle Steuerung von Modul 1 (Delivery) und Modul 2 (Storage) über die Kommandozeile.

Start:
    python steuerung_cli.py                       interaktiv (Befehl "hilfe" zeigt alles)
    python steuerung_cli.py "modul 1; band an"    Befehle direkt ausführen und beenden
    python steuerung_cli.py --offline             ohne Broker, Publishes werden nur angezeigt

Achtung: Nicht gleichzeitig mit Main.py / Module1.py / Module2.py benutzen,
sonst schalten Zustandsautomat und Mensch gegeneinander.
"""

import argparse
import cmd
import json
import sys
import threading
import time

from paho.mqtt.client import Client, CallbackAPIVersion

from popcorn.config import (
    BROKER_HOST, BROKER_PORT, USER, PASSWORD,
    TOPIC_PREFIX_DELIVERY_SENSORS, TOPIC_PREFIX_DELIVERY_ACTORS,
    TOPIC_PREFIX_STORAGE_SENSORS, TOPIC_PREFIX_STORAGE_ACTORS,
    TOPIC_DELIVERY_INTERFACES, TOPIC_STORAGE_INTERFACES,
)
from popcorn.komponenten import Foerderband, Ruettler, Abtransport, Lampen


# Kurznamen für die Handshake-Topics (Befehl "signal")
SIGNALE = {
    "m2_voll":   "MV/VPS/DeliveryStorage/M2_Silo_Full",
    "m2_notaus": "MV/VPS/DeliveryStorage/M2_Emergency",
    "m3_voll":   "MV/VPS/StorageDosing/M3SiloVoll",
    "m3_notaus": "MV/VPS/StorageDosing/M3Not-Aus",
}

SENSOREN = ["Top", "Bottom", "Funnel", "Emergency"]

WAHR = {"an", "ein", "1", "true", "on", "ja"}
FALSCH = {"aus", "0", "false", "off", "nein"}


def parse_bool(text):
    """'an'/'aus', '1'/'0', 'true'/'false' -> bool, sonst None."""
    text = text.strip().lower()
    if text in WAHR:
        return True
    if text in FALSCH:
        return False
    return None


class Verbindung:
    """Minimaler Ersatz für MqttVerbindung: Komponenten brauchen nur .mqtt_client."""

    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client


class OfflineInfo:
    def wait_for_publish(self, timeout=None):
        pass


class OfflineClient:
    """Tut so, als wäre er ein MQTT-Client, und gibt jeden Publish nur aus."""

    def publish(self, topic, payload, qos=0, retain=False):
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        print(f"  [offline] {topic} <- {payload}")
        return OfflineInfo()


class ModulSteuerung:
    """Die Aktoren eines Moduls, gebaut aus den Komponenten des Projekts."""

    def __init__(self, nummer, name, prefix_sensoren, prefix_aktoren, antrieb, antrieb_name):
        self.nummer = nummer
        self.name = name
        self.prefix_sensoren = prefix_sensoren
        self.antrieb = antrieb                  # Foerderband bzw. Ruettler (Muskel)
        self.antrieb_name = antrieb_name
        self.abtransport = Abtransport("abtransport", prefix_aktoren)
        self.lampen = Lampen("lampen", prefix_aktoren)
        self.lampen_zustand = {"Red": False, "Orange": False, "Green": False}

    def set_mqtt(self, verbindung):
        self.antrieb.set_mqtt(verbindung)
        self.abtransport.set_mqtt(verbindung)
        self.lampen.set_mqtt(verbindung)


class SteuerungCLI(cmd.Cmd):
    intro = (
        "\nVPS-Handsteuerung Modul 1 (Delivery) + Modul 2 (Storage)\n"
        "Befehl 'hilfe' zeigt alle Befehle. Beenden mit 'ende' oder Strg+D.\n"
        "Achtung: Nicht parallel zu Main.py/Module1.py/Module2.py benutzen!\n"
    )

    def __init__(self, mqtt_client, offline=False):
        super().__init__()
        self.offline = offline
        self.mqtt_client = mqtt_client
        verbindung = Verbindung(mqtt_client)

        self.module = {
            1: ModulSteuerung(1, "Delivery", TOPIC_PREFIX_DELIVERY_SENSORS, TOPIC_PREFIX_DELIVERY_ACTORS,
                              Foerderband("foerderband", TOPIC_PREFIX_DELIVERY_ACTORS), "Förderband"),
            2: ModulSteuerung(2, "Storage", TOPIC_PREFIX_STORAGE_SENSORS, TOPIC_PREFIX_STORAGE_ACTORS,
                              Ruettler("ruettler", TOPIC_PREFIX_STORAGE_ACTORS), "Muskel"),
        }
        for modul in self.module.values():
            modul.set_mqtt(verbindung)

        self.aktiv = self.module[1]
        self.sensorwerte = {}       # topic -> (wert, uhrzeit)
        self.sensor_lock = threading.Lock()
        self.mithoeren = False
        self.eingeschaltet = set()  # (modulnummer, "antrieb"/"luft"), wird beim Beenden abgeschaltet
        self._prompt_setzen()

    # --- Hilfsfunktionen -------------------------------------------------

    def _prompt_setzen(self):
        self.prompt = f"M{self.aktiv.nummer} {self.aktiv.name}> "

    def _ok(self, erfolg, text):
        print(("  OK: " if erfolg else "  FEHLER (Publish fehlgeschlagen): ") + text)

    def _module_aus_argument(self, arg):
        """'' -> aktives Modul, 'alle' -> beide, '1'/'2' -> dieses."""
        arg = arg.strip().lower()
        if arg == "":
            return [self.aktiv]
        if arg == "alle":
            return list(self.module.values())
        if arg in ("1", "2"):
            return [self.module[int(arg)]]
        print("  Modul muss 1, 2 oder 'alle' sein.")
        return []

    def nachricht_empfangen(self, topic, payload):
        """Wird aus dem MQTT-Thread aufgerufen. Darf nie eine Exception werfen."""
        try:
            text = payload.decode("utf-8")
            try:
                daten = json.loads(text)
                wert = daten["value"] if isinstance(daten, dict) and "value" in daten else daten
            except json.JSONDecodeError:
                wert = text
        except Exception:
            wert = repr(payload)
        with self.sensor_lock:
            self.sensorwerte[topic] = (wert, time.strftime("%H:%M:%S"))
        if self.mithoeren:
            print(f"\n  << {topic} = {wert}")

    # --- Befehle ---------------------------------------------------------

    def do_modul(self, arg):
        """modul 1|2 – aktives Modul wählen."""
        if arg.strip() not in ("1", "2"):
            print("  Benutzung: modul 1 | modul 2")
            return
        self.aktiv = self.module[int(arg)]
        self._prompt_setzen()

    def do_band(self, arg):
        """band an|aus – Antrieb des aktiven Moduls (M1: Förderband, M2: Muskel). Luft läuft automatisch mit."""
        wert = parse_bool(arg)
        if wert is None:
            print("  Benutzung: band an | band aus")
            return
        m = self.aktiv
        erfolg = m.antrieb.start() if wert else m.antrieb.stop()
        if erfolg:
            (self.eingeschaltet.add if wert else self.eingeschaltet.discard)((m.nummer, "antrieb"))
        self._ok(erfolg, f"M{m.nummer} {m.antrieb_name} {'AN' if wert else 'AUS'}")

    do_muskel = do_band
    do_antrieb = do_band

    def do_luft(self, arg):
        """luft an|aus – Druckluft des aktiven Moduls."""
        wert = parse_bool(arg)
        if wert is None:
            print("  Benutzung: luft an | luft aus")
            return
        m = self.aktiv
        erfolg = m.abtransport.start_air() if wert else m.abtransport.stop_air()
        if erfolg:
            (self.eingeschaltet.add if wert else self.eingeschaltet.discard)((m.nummer, "luft"))
        self._ok(erfolg, f"M{m.nummer} Druckluft {'AN' if wert else 'AUS'}")

    def do_lampen(self, arg):
        """lampen <r> <o> <g>  z. B. 'lampen 1 0 1'
lampen rot|orange|gruen [...]  nur die genannten an, z. B. 'lampen rot gruen'
lampen alle | lampen aus"""
        teile = arg.lower().split()
        if not teile:
            print("  Benutzung: lampen 1 0 1 | lampen rot gruen | lampen alle | lampen aus")
            return

        if len(teile) == 3 and all(parse_bool(t) is not None for t in teile):
            rot, orange, gruen = (parse_bool(t) for t in teile)
        elif teile == ["alle"]:
            rot = orange = gruen = True
        elif teile == ["aus"]:
            rot = orange = gruen = False
        else:
            namen = {"rot": "r", "red": "r", "orange": "o", "gelb": "o", "gruen": "g", "grün": "g", "green": "g"}
            unbekannt = [t for t in teile if t not in namen]
            if unbekannt:
                print(f"  Unbekannte Lampe(n): {', '.join(unbekannt)}")
                return
            gewaehlt = {namen[t] for t in teile}
            rot, orange, gruen = "r" in gewaehlt, "o" in gewaehlt, "g" in gewaehlt

        m = self.aktiv
        erfolg = m.lampen.set_lampen(rot, orange, gruen)
        if erfolg:
            m.lampen_zustand = {"Red": rot, "Orange": orange, "Green": gruen}
        an = [n for n, w in (("rot", rot), ("orange", orange), ("grün", gruen)) if w] or ["keine"]
        self._ok(erfolg, f"M{m.nummer} Lampen an: {', '.join(an)}")

    def do_stop(self, arg):
        """stop [1|2|alle] – Antrieb und Luft aus (ohne Angabe: aktives Modul)."""
        for m in self._module_aus_argument(arg):
            erfolg = m.antrieb.stop()
            erfolg = m.abtransport.stop_air() and erfolg
            if erfolg:
                self.eingeschaltet.discard((m.nummer, "antrieb"))
                self.eingeschaltet.discard((m.nummer, "luft"))
            self._ok(erfolg, f"M{m.nummer} {m.antrieb_name} + Druckluft AUS")

    def do_allesaus(self, arg):
        """allesaus – Antrieb, Luft und Lampen beider Module aus."""
        self.do_stop("alle")
        for m in self.module.values():
            self._ok(m.lampen.set_lampen(False, False, False), f"M{m.nummer} Lampen AUS")

    def do_signal(self, arg):
        """signal <name> true|false – Handshake-Signal publishen (zum Testen der Kopplung).
Namen: m2_voll, m2_notaus, m3_voll, m3_notaus. Payload: {"value": true|false}"""
        teile = arg.lower().split()
        if len(teile) != 2 or teile[0] not in SIGNALE or parse_bool(teile[1]) is None:
            print(f"  Benutzung: signal <{'|'.join(SIGNALE)}> true|false")
            return
        topic, wert = SIGNALE[teile[0]], parse_bool(teile[1])
        info = self.mqtt_client.publish(topic, json.dumps({"value": wert}), qos=0)
        try:
            info.wait_for_publish(timeout=10)
            self._ok(True, f"{topic} <- {wert}")
        except RuntimeError:
            self._ok(False, topic)

    def do_status(self, arg):
        """status – letzte Sensorwerte, Handshake-Signale und gesendete Aktor-Zustände."""
        with self.sensor_lock:
            werte = dict(self.sensorwerte)

        def zeile(name, topic):
            wert, zeit = werte.get(topic, ("–", ""))
            print(f"    {name:<12} {str(wert):<8} {zeit}")

        for m in self.module.values():
            markierung = "  <- aktiv" if m is self.aktiv else ""
            print(f"\n  M{m.nummer} {m.name}{markierung}")
            print("   Sensoren:")
            for sensor in SENSOREN:
                zeile(sensor, m.prefix_sensoren + sensor)
            lampen = [n for n, w in m.lampen_zustand.items() if w] or ["keine"]
            print("   Aktoren (zuletzt gesendet):")
            print(f"    {m.antrieb_name:<12} {'AN' if m.antrieb.running else 'AUS'}")
            print(f"    {'Druckluft':<12} {'AN' if m.abtransport.air else 'AUS'}")
            print(f"    {'Lampen':<12} {', '.join(lampen)}")

        print("\n  Handshake-Signale:")
        for name, topic in SIGNALE.items():
            zeile(name, topic)
        if self.offline:
            print("\n  (offline: es werden keine Sensorwerte empfangen)")
        print()

    def do_mithoeren(self, arg):
        """mithoeren an|aus – eingehende Sensornachrichten live anzeigen."""
        wert = parse_bool(arg)
        if wert is None:
            print("  Benutzung: mithoeren an | mithoeren aus")
            return
        self.mithoeren = wert
        print(f"  Mithören {'AN' if wert else 'AUS'}")

    def do_hilfe(self, arg):
        """hilfe – diese Übersicht."""
        print("""
  modul 1|2                  aktives Modul wählen (1 = Delivery, 2 = Storage)
  band an|aus                Antrieb (M1 Förderband, M2 Muskel); Luft läuft automatisch mit
  luft an|aus                Druckluft
  lampen 1 0 1               Lampen rot/orange/grün setzen
  lampen rot gruen           nur die genannten Lampen an (auch: alle, aus)
  stop [1|2|alle]            Antrieb + Luft aus
  allesaus                   alles an beiden Modulen aus, auch die Lampen
  signal m2_voll true        Handshake-Signal senden (m2_voll, m2_notaus, m3_voll, m3_notaus)
  status                     Sensorwerte und Aktor-Zustände anzeigen
  mithoeren an|aus           eingehende Nachrichten live anzeigen
  ende                       beenden (eingeschaltete Antriebe/Luft werden abgeschaltet)

  Mehrere Befehle in einer Zeile mit ';' trennen, z. B.: modul 2; band an
""")

    def do_ende(self, arg):
        """ende – Programm beenden."""
        return True

    do_exit = do_ende
    do_quit = do_ende

    def do_EOF(self, arg):
        print()
        return True

    # --- cmd-Verhalten ----------------------------------------------------

    def precmd(self, line):
        # mehrere Befehle mit ';' in einer Zeile erlauben
        if ";" in line:
            for teil in line.split(";"):
                if teil.strip() and self.onecmd(teil.strip()):
                    return "ende"
            return ""
        return line

    def emptyline(self):
        pass

    def default(self, line):
        print(f"  Unbekannter Befehl: {line!r} – 'hilfe' zeigt alle Befehle.")

    def aufraeumen(self):
        """Was in dieser Sitzung eingeschaltet wurde, wieder ausschalten."""
        for nummer in sorted({n for n, _ in self.eingeschaltet}):
            print(f"  Schalte M{nummer} beim Beenden ab ...")
            self.do_stop(str(nummer))


def verbinde():
    """Mit dem Broker verbinden und alle Sensor- und Handshake-Topics abonnieren."""
    verbunden = threading.Event()
    fehler = []
    client = Client(CallbackAPIVersion.VERSION2)
    client.username_pw_set(USER, PASSWORD)

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            fehler.append(str(reason_code))
        else:
            topics = [TOPIC_PREFIX_DELIVERY_SENSORS + "#", TOPIC_PREFIX_STORAGE_SENSORS + "#"]
            topics += sorted(set(TOPIC_DELIVERY_INTERFACES + TOPIC_STORAGE_INTERFACES))
            for topic in topics:
                client.subscribe(topic)
        verbunden.set()

    client.on_connect = on_connect
    print(f"Verbinde mit {BROKER_HOST}:{BROKER_PORT} ...")
    client.connect(BROKER_HOST, BROKER_PORT)
    client.loop_start()
    if not verbunden.wait(timeout=10):
        raise ConnectionError("Keine Antwort vom Broker innerhalb von 10 s.")
    if fehler:
        raise ConnectionError(f"Broker hat die Verbindung abgelehnt: {fehler[0]}")
    print("Verbunden.")
    return client


def main():
    parser = argparse.ArgumentParser(description="Handsteuerung für Modul 1 (Delivery) und Modul 2 (Storage).")
    parser.add_argument("befehle", nargs="*", help='Befehle direkt ausführen, z. B. "modul 1; band an"')
    parser.add_argument("--offline", action="store_true", help="ohne Broker, Publishes nur anzeigen")
    args = parser.parse_args()

    if args.offline:
        client = OfflineClient()
    else:
        try:
            client = verbinde()
        except (OSError, ConnectionError) as e:
            print(f"Verbindung fehlgeschlagen: {e}")
            sys.exit(1)

    cli = SteuerungCLI(client, offline=args.offline)
    if not args.offline:
        client.on_message = lambda c, u, msg: cli.nachricht_empfangen(msg.topic, msg.payload)

    try:
        if args.befehle:
            # Einmal-Modus: Befehle ausführen, eingeschaltete Aktoren bleiben an
            cli.onecmd(cli.precmd(" ".join(args.befehle)))
        else:
            cli.cmdloop()
            cli.aufraeumen()
    except KeyboardInterrupt:
        print()
        cli.aufraeumen()
    finally:
        if not args.offline:
            client.loop_stop()
            client.disconnect()


if __name__ == "__main__":
    main()
