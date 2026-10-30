from popcorn.Module.delivery import Delivery
from popcorn.mqtt_verbindung import MqttVerbindung
import time

modul = Delivery()
mqtt_verbindung = MqttVerbindung(modul)

modul.foerderband.start()
time.sleep(5)
modul.foerderband.stop()
modul.lampen.set_lampen("true","true","true")
time.sleep(5)
modul.lampen.set_lampen("false","false","false")