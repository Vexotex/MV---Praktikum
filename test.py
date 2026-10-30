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


# print("start")
# modul.foerderband.start()
# time.sleep(5)
# print("stop")
# modul.foerderband.stop()



modul.abtransport.start_air()
print("started")
time.sleep(5)
print("stopping now")
modul.abtransport.stop_air()
print("stopped")


# modul.lampen.set_lampen("true","true","true")
# time.sleep(5)
# modul.lampen.set_lampen("false","false","false")