from popcorn.Module.delivery import Delivery
from popcorn.mqtt_verbindung import MqttVerbindung
import time

modul = Delivery()

mqtt_verbindung = None
mqtt_verbindung = MqttVerbindung(modul)
# Falls Verbindung aufgebaut werden konnte
if mqtt_verbindung == None:
    print("no wörki")

modul.set_mqtt(mqtt_verbindung)
print("verbindung set")

while True:
    pass