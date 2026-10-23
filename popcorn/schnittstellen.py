"""Schnittstellen zu den Nachbarmodulen der Anlage."""

from popcorn.komponenten import Komponente


class Schnittstelle(Komponente):
    """Austausch mit einem anderen Modul über MQTT."""

    def __init__(self, name: str, verbindung):
        super().__init__(name, verbindung)
        # TODO: Signale, z.B. nachbar_bereit

    # TODO: Befehle/Meldungen, z.B. uebergabe_melden()
