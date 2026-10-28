from popcorn.Module.delivery import Delivery
from popcorn.mqtt_verbindung import MqttVerbindung
from popcorn.zustandsautomat import Zustandsautomat


def main():
    modul = Delivery()
    
    mqtt_verbindung = MqttVerbindung(modul)
    # Falls Verbindung aufgebaut werden konnte
    if mqtt_verbindung == None:
        return

    modul.set_mqtt(mqtt_verbindung)
    automat = Zustandsautomat(modul)

    # TODO: verbinden, Modul starten, Automat in Schleife laufen lassen


if __name__ == "__main__":
    main()
