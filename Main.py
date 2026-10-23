from popcorn import config
from popcorn.modul import Modul
from popcorn.mqtt_verbindung import MqttVerbindung
from popcorn.zustandsautomat import Zustandsautomat


def main():
    verbindung = MqttVerbindung(config.BROKER_HOST, config.BROKER_PORT)
    modul = Modul(verbindung)
    automat = Zustandsautomat(modul)

    # TODO: verbinden, Modul starten, Automat in Schleife laufen lassen


if __name__ == "__main__":
    main()
