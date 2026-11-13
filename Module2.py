from popcorn.config import INTERVALL
from popcorn.Module.storage import Storage
from popcorn.mqtt_verbindung import MqttVerbindung
from popcorn.zustandsautomat import Zustandsautomat
import time

async def Module2():
    modul = Storage()
    
    mqtt_verbindung = MqttVerbindung(modul)
    # Falls Verbindung aufgebaut werden konnte
    if mqtt_verbindung == None:
        return

    modul.set_mqtt(mqtt_verbindung)
    automat = Zustandsautomat(modul)

    while True:
        automat.schritt()
        time.sleep(INTERVALL)


if __name__ == "__main__":
    Module2()
