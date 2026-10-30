"""Zustandsautomat(en) zur Steuerung des Moduls."""

from enum import Enum, auto


class Zustand(Enum):
    INIT = auto() # PON
    BEREIT = auto()
    VORLAUF = auto()
    LAEUFT = auto()
    STOP = auto()
    NACHLAUF = auto()


class Zustandsautomat:
    """Steuert das Modul. Spricht nie direkt mit MQTT, nur mit dem Modul."""

    def __init__(self, _modul, _intervall):
        self.modul = _modul
        self.zustand = Zustand.INIT
        self.intervall = _intervall
        self.counter = 0
        self.wartezeit_in_sekunden = 1

    def schritt(self):
        """Einen Durchlauf ausführen: Bedingungen prüfen, ggf. Zustand wechseln."""
        
        if (self.ist_Not_Aus_ausgeloest() or 
            self.ist_trichter_voll() or 
            self.ist_M2_Not_Aus_ausgeloest()
            ):
            self.alles_aus()
            self.zustand = Zustand.STOP
            return
        
        match self.zustand:
            case Zustand.INIT:
                self.alles_aus()
                neuer_zustand = Zustand.BEREIT
            
            case Zustand.BEREIT:
                # checks
                if not (self.ist_Silo_leer() or self.ist_M2_Silo_voll()):
                    break

                # Wenn alles ok
                self.druckluft_an()
                self.set_counter(1)
                neuer_zustand = Zustand.VORLAUF
            
            case Zustand.VORLAUF:
                self.counter -= 1
                if self.counter <= 0:
                    self.foerderband_an()
                    neuer_zustand = Zustand.LAEUFT
                break
            
            case Zustand.LAEUFT:
                # checks
                if self.ist_Silo_leer() or self.ist_M2_Silo_voll():
                    self.set_counter(1)
                    neuer_zustand = Zustand.Nachlauf
                
                # Wenn alles ok -> bleiben wir am laufen
                break
            
            case Zustand.STOP:
                if (self.ist_Not_Aus_ausgeloest() or 
                    self.ist_Silo_leer() or 
                    self.ist_trichter_voll() or
                    self.ist_M2_Not_Aus_ausgeloest()
                    ):
                    break
                # Wenn alles ok
                neuer_zustand = Zustand.BEREIT
                
            case Zustand.NACHLAUF:
                self.counter -= 1
                if self.counter <= 0:
                    neuer_zustand = Zustand.BEREIT
                break
        
        self.zustand = neuer_zustand
        
        self.lampen_aktualisieren(self.zustand)
        
        return
    
    # --- checks ---
    def ist_Not_Aus_ausgeloest():
        # TODO
        pass
    
    def ist_M2_Not_Aus_ausgeloest():
        # TODO
        pass
    
    def ist_Silo_leer():
        # TODO
        pass

    def ist_M2_Silo_voll():
        # TODO
        pass
    
    def ist_trichter_voll():
        # TODO
        pass
    
    # --- Intern ---
    def set_counter(Zeit_in_Sekunden):
        """Setzt die WarteZeit in Sekunden"""
        self.counter = Zeit_in_Sekunden / self.intervall
        return
    
    # --- Aktorensteuerung ---
    def foerderband_an():
        # TODO
        pass
    
    def alles_aus():
        # TODO Förderband, Druckluft, Lampen
        pass
    
    # --- Lampensteuerung ---
    def lampen_aktualisieren(zustand):
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
        
        return