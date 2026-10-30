from popcorn.Module.delivery import Delivery
from popcorn.mqtt_verbindung import MqttVerbindung
import time

modul = Delivery()

mqtt_verbindung = None
mqtt_verbindung = MqttVerbindung(modul)
# Falls Verbindung aufgebaut werden konnte
if mqtt_verbindung == None:
    print("no wörki")

mqtt_verbindung.mqtt_client.loop()
modul.set_mqtt(mqtt_verbindung)
print("verbindung set")
modul.lampen.set_lampen("true","true","true")
time.sleep(5)
modul.lampen.set_lampen("false","false","false")