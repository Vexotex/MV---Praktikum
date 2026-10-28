"""Das Modul der Anlage: besitzt die Komponenten."""

from popcorn.komponenten import Foerderband, Fuelltrichter, Abtransport


class Delivery:
    """Fasst alle Komponenten zusammen und verteilt eingehende MQTT-Nachrichten."""

    def __init__(self):
        self.fuelltrichter = Fuelltrichter("fuelltrichter")
        self.foerderband = Foerderband("foerderband")
        self.abtransport = Abtransport("abtransport")
        # TODO: weitere Komponenten
        # TODO: Schnittstellen zu den Nachbarmodulen (siehe schnittstellen.py)

    def set_mqtt(self, mqtt_verbindung):
        """Verbindet Delivery mit der MQTT-Schnittstelle."""
        self.mqtt = mqtt_verbindung

    def starten(self):
        """Topics aller Komponenten abonnieren."""
        # TODO
        pass

    def update_top(self, payload_value):
        self.fuelltrichter.top = payload_value

    def update_bottom(self, payload_value):
        self.fuelltrichter.bottom = payload_value

    def update_funnel(self, payload_value):
        self.funnel = payload_value

    def update_emergency(self, payload_value):
        self.emergency = payload_value