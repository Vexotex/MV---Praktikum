"""Zustandsautomat(en) zur Steuerung des Moduls."""

from enum import Enum, auto
from config import INTERVALL

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

    def schritt(self):
        """Einen Durchlauf ausführen: Bedingungen prüfen, ggf. Zustand wechseln."""
        
        if (self.ist_Not_Aus_ausgeloest() or 
            self.ist_trichter_voll() or 
            self.ist_M2_Not_Aus_ausgeloest()
            ):
            while True:
                if self.modul.stop_all():
                    break
            self.zustand = Zustand.STOP
            return
        
        match self.zustand:
            case Zustand.INIT:
                self.modul.stop_all()
                neuer_zustand = Zustand.BEREIT
            
            case Zustand.BEREIT:
                # checks Silo of Module 1 and 2
                if not (self.ist_Silo_leer() or self.ist_M2_Silo_voll()):
                    pass
                else: # Wenn alles ok
                    self.modul.air_start()
                    self.set_wait_in_seconds(1)
                    neuer_zustand = Zustand.VORLAUF
            
            case Zustand.VORLAUF:
                self.counter -= 1
                if self.counter <= 0:
                    self.modul.transport_start()
                    neuer_zustand = Zustand.LAEUFT
            
            case Zustand.LAEUFT:
                if self.ist_Silo_leer() or self.ist_M2_Silo_voll():
                    self.set_wait_in_seconds(1)
                    neuer_zustand = Zustand.NACHLAUF
                
                # Wenn alles ok -> bleiben wir am laufen
            
            case Zustand.STOP:
                if (self.ist_Not_Aus_ausgeloest() or 
                    self.ist_Silo_leer() or 
                    self.ist_trichter_voll() or
                    self.ist_M2_Not_Aus_ausgeloest()
                    ):
                    pass
                else:
                    neuer_zustand = Zustand.BEREIT
                
            case Zustand.NACHLAUF:
                self.counter -= 1
                if self.counter <= 0:
                    self.modul.transport_stop()
                    self.modul.air_stop()
                    neuer_zustand = Zustand.BEREIT
        
        self.zustand = neuer_zustand
        
        self.lampen_aktualisieren(self.zustand)
        
        return
    
    # --- checks ---
    def ist_Not_Aus_ausgeloest(self):
        return self.modul.emergency
    
    def ist_M2_Not_Aus_ausgeloest(self):
        return self.modul.m2_emergency
    
    def ist_Silo_leer(self):
        return not(self.modul.silo.sensor_bottom)

    def ist_M2_Silo_voll(self):
        return self.modul.silo.sensor_top
    
    def ist_trichter_voll(self):
        return self.modul.abtransport.funnel
    
    # --- Intern ---
    def set_wait_in_seconds(self, Zeit_in_Sekunden):
        """Setzt die WarteZeit in Sekunden"""
        self.counter = Zeit_in_Sekunden / INTERVALL
        return
    
    # --- Lampensteuerung ---
    def lampen_aktualisieren(self, zustand):
        match zustand:
            case Zustand.INIT:
                while True:
                    if self.modul.lampen.set_lampen("true","true","true"):
                        break
            case Zustand.BEREIT:
                while True:
                    if self.modul.lampen.set_lampen("false","true","false"):
                        break
            case Zustand.VORLAUF:
                while True:
                    if self.modul.lampen.set_lampen("false","true","true"):
                        break
            case Zustand.LAEUFT:
                while True:
                    if self.modul.lampen.set_lampen("false","false","true"):
                        break
            case Zustand.STOP:
                while True:
                    if self.modul.lampen.set_lampen("true","false","false"):
                        break
            case Zustand.NACHLAUF:
                while True:
                    if self.modul.lampen.set_lampen("false","true","true"):
                        break