"""Zustandsautomat(en) zur Steuerung des Moduls."""

from enum import Enum, auto
from popcorn.config import INTERVALL

class Zustand(Enum):
    INIT = auto() # PON
    BEREIT = auto()
    VORLAUF = auto()
    LAEUFT = auto()
    STOP = auto()
    NACHLAUF = auto()


class Zustandsautomat:
    """Steuert das Modul. Spricht nie direkt mit MQTT, nur mit dem Modul."""

    def __init__(self, _modul):
        self.modul = _modul
        self.zustand = Zustand.INIT
        self.counter = 0
        self.wartezeit_in_sekunden = 1
        self.stopwechsel = False

    def schritt(self):
        """Einen Durchlauf ausführen: Bedingungen prüfen, ggf. Zustand wechseln."""
        neuer_zustand = self.zustand
        
        if self.modul.to_stop():
            self.modul.stop_all()
            self.zustand = Zustand.STOP
            if not self.stopwechsel:
                print("STOp!")
                self.stopwechsel = True
            return
        
        match self.zustand:
            case Zustand.INIT:
                self.modul.stop_all()
                neuer_zustand = Zustand.BEREIT
                print("Init -> Bereit")
            
            case Zustand.BEREIT:
                # checks Silo of Module 1 and 2
                if self.modul.from_bereit():
                    pass
                else: # Wenn alles ok
                    self.modul.air_start()
                    self.set_wait_in_seconds(1)
                    neuer_zustand = Zustand.VORLAUF
                    print("Bereit -> Vorlauf")
            
            case Zustand.VORLAUF:
                self.counter -= 1
                if self.counter <= 0:
                    self.modul.transport_start()
                    neuer_zustand = Zustand.LAEUFT
                    print("Vorlauf -> Läuft")
            
            case Zustand.LAEUFT:
                if self.modul.from_laeuft():
                    self.set_wait_in_seconds(1)
                    neuer_zustand = Zustand.NACHLAUF
                    print("Läuft -> Nachlauf")
                # Wenn alles ok -> bleiben wir am laufen
            
            case Zustand.STOP:
                if self.modul.from_stop():
                    pass
                else:
                    neuer_zustand = Zustand.BEREIT
                    self.stopwechsel = False
                    print("STOp -> Bereit")
                
            case Zustand.NACHLAUF:
                self.counter -= 1
                if self.counter <= 0:
                    self.modul.transport_stop()
                    self.modul.air_stop()
                    neuer_zustand = Zustand.BEREIT
                    print("Nachlauf -> Bereit")
        
        self.zustand = neuer_zustand
        
        self.lampen_aktualisieren(self.zustand)
        
        return
    
    # --- Intern ---
    def set_wait_in_seconds(self, Zeit_in_Sekunden):
        """Setzt die WarteZeit in Sekunden"""
        self.counter = Zeit_in_Sekunden / INTERVALL
        return
    
    # --- Lampensteuerung ---
    def lampen_aktualisieren(self, zustand):
        match zustand:
            case Zustand.INIT:
                self.modul.lampen.set_lampen("true","true","true")
            case Zustand.BEREIT:
                self.modul.lampen.set_lampen("false","true","false")
            case Zustand.VORLAUF:
                self.modul.lampen.set_lampen("false","true","true")
            case Zustand.LAEUFT:
                self.modul.lampen.set_lampen("false","false","true")
            case Zustand.STOP:
                self.modul.lampen.set_lampen("true","false","false")
            case Zustand.NACHLAUF:
                self.modul.lampen.set_lampen("false","true","true")