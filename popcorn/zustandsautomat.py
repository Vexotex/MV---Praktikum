"""Zustandsautomat(en) zur Steuerung des Moduls."""

from enum import Enum, auto


class Zustand(Enum):
    INIT = auto() # PON
    BEREIT = auto()
    LAEUFT = auto()
    Nachlauf = auto()
    FEHLER = auto()
    Vorlauf = auto()


class Zustandsautomat:
    """Steuert das Modul. Spricht nie direkt mit MQTT, nur mit dem Modul."""

    def __init__(self, modul):
        self.modul = modul
        self.zustand = Zustand.INIT

    def schritt(self):
        """Einen Durchlauf ausführen: Bedingungen prüfen, ggf. Zustand wechseln."""
        # TODO
        pass
