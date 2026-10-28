"""Komponenten des Moduls."""


class Komponente:
    """Basisklasse für alle Komponenten."""

    def __init__(self, name: str, verbindung):
        self.name = name
        self.verbindung = verbindung

    def topics(self) -> list[str]:
        """Topics, die diese Komponente abonnieren möchte."""
        # TODO
        return []

    def nachricht_empfangen(self, topic: str, nachricht: str):
        """Wird vom Modul aufgerufen, wenn eine Nachricht für diese Komponente eintrifft."""
        # TODO
        pass


class Fuelltrichter(Komponente):
    def __init__(self, name: str, verbindung):
        super().__init__(name, verbindung)
        # TODO: Attribute, z.B. Füllstand

    # TODO: Befehle, z.B. oeffnen() / schliessen()


class Foerderband(Komponente):
    def __init__(self, name: str, verbindung):
        super().__init__(name, verbindung)
        # TODO: Attribute, z.B. laeuft

    # TODO: Befehle, z.B. starten() / stoppen()

class Abtransport(Komponente):
    def __init__(self, name, verbindung):
        super().__init__(name, verbindung)
        self.air = False
        self.funnel = False

    def start_air(self):
        pass

    def stop_air(self):
        pass