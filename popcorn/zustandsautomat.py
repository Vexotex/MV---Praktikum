"""Zustandsautomat(en) zur Steuerung des Moduls."""

from enum import Enum, auto


class Zustand(Enum):
    # TODO: echte Zustände festlegen
    INIT = auto()
    BEREIT = auto()
    LAEUFT = auto()
    FEHLER = auto()


class Zustandsautomat:
    """Steuert das Modul. Spricht nie direkt mit MQTT, nur mit dem Modul."""

    def __init__(self, modul):
        self.modul = modul
        self.zustand = Zustand.INIT

    def schritt(self):
        """Einen Durchlauf ausführen: Bedingungen prüfen, ggf. Zustand wechseln."""
        # TODO
        pass
