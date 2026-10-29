"""Zustandsautomat(en) zur Steuerung des Moduls."""

from enum import Enum, auto


class Zustand(Enum):
    INIT = auto() # PON
    BEREIT = auto()
    LAEUFT = auto()
    STOP = auto()
    NACHLAUF = auto()
    VORLAUF = auto()


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
        
        if self.ist_Not_Aus_ausgelöst():
            self.alles_aus()
            self.zustand = Zustand.STOP
            return
        
        match self.zustand:
            case Zustand.INIT:
                neuer_zustand = Zustand.BEREIT
            
            case Zustand.BEREIT:
                # checks
                if not self.M2_kann_empfangen():
                    break

                # Wenn alles ok
                # TODO Fließband und Druckluft an
                 
                neuer_zustand = Zustand.LAEUFT
            
            case Zustand.LAEUFT:
                # checks
                if self.ist_Silo_leer():
                    self.counter = self.wartezeit_in_sekunden / self.intervall
                    neuer_zustand = Zustand.Nachlauf
                
                # Wenn alles ok -> bleiben wir am laufen
                break
            
            case Zustand.STOP:
                if self.ist_Not_Aus_ausgelöst():
                    break
                if self.ist_Silo_leer():
                    break
                
            case Zustand.NACHLAUF:
                self.counter -= 1
                if self.counter <= 0:
                    neuer_zustand = Zustand.STOP
                break
            
            case Zustand.VORLAUF:
                break
        
        self.zustand = neuer_zustand
        return
    
    def ist_Not_Aus_ausgelöst():
        # TODO
        pass
    
    def alles_aus():
        # TODO
        pass    
    
    def ist_Silo_leer():
        # TODO
        pass

    def M2_kann_empfangen():
        # TODO
        pass