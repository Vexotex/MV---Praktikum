"""Das Modul der Anlage: besitzt die Komponenten."""

from popcorn.komponenten import Foerderband, Fuelltrichter


class Delivery:
    """Fasst alle Komponenten zusammen und verteilt eingehende MQTT-Nachrichten."""

    def __init__(self, verbindung):
        self.verbindung = verbindung
        self.fuelltrichter = Fuelltrichter("fuelltrichter", verbindung)
        self.foerderband = Foerderband("foerderband", verbindung)
        # TODO: weitere Komponenten
        # TODO: Schnittstellen zu den Nachbarmodulen (siehe schnittstellen.py)

    def starten(self):
        """Topics aller Komponenten abonnieren."""
        # TODO
        pass
