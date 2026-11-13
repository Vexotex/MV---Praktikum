"""Das Storage Modul der Anlage: besitzt die Komponenten Silo, Ruettler und Abtransport."""

from popcorn.codec import decode_bool, encode_bool
from popcorn.komponenten import Ruettler, Silo, Abtransport, Lampen
from popcorn.config import (
    TOPIC_PREFIX_STORAGE_ACTORS, 
    TOPIC_PREFIX_STORAGE_SENSORS, 
    TOPIC_STORAGE_INTERFACES_LISTEN,
    TOPIC_STORAGE_INTERFACES_SPEAK
)


class Storage:
    """Fasst alle Komponenten zusammen und verteilt eingehende MQTT-Nachrichten."""

    def __init__(self):

        # import mqtt_topics for Module from Config
        self.TOPIC_PREFIX_SENSORS = TOPIC_PREFIX_STORAGE_SENSORS
        self.TOPIC_PREFIX_ACTORS = TOPIC_PREFIX_STORAGE_ACTORS
        self.TOPIC_INTERFACES_LISTEN = TOPIC_STORAGE_INTERFACES_LISTEN
        self.TOPIC_INTERFACES_SPEAK = TOPIC_STORAGE_INTERFACES_SPEAK

        # initialise Components
        self.silo = Silo("silo", self.TOPIC_PREFIX_ACTORS)
        self.ruettler = Ruettler("ruettler", self.TOPIC_PREFIX_ACTORS)
        self.abtransport = Abtransport("abtransport", self.TOPIC_PREFIX_ACTORS)
        self.lampen = Lampen("lampen", self.TOPIC_PREFIX_ACTORS)
        self.emergency = True
        self.m3_emergency = True
        self.m3_silo_full = False

    def to_stop(self) -> bool:
        return (
            not self.emergency or
            self.abtransport.funnel or
            not self.m3_emergency
        )

    def from_bereit(self) -> bool:   
        return(
            self.silo.sensor_bottom and
            not self.m3_silo_full
        )

    def from_laeuft(self) -> bool:   
        return(
            not self.silo.sensor_bottom or
            self.m3_silo_full
        )

    def from_stop(self) -> bool:   
        return(
            not self.emergency and
            not self.silo.sensor_bottom and
            self.abtransport.funnel and
            not self.m3_emergency
        )

    def set_mqtt(self, mqtt_verbindung):
        """Verbindet STORAGE und Komponenten mit der MQTT-Schnittstelle."""
        self.mqtt = mqtt_verbindung
        self.silo.set_mqtt(mqtt_verbindung)
        self.ruettler.set_mqtt(mqtt_verbindung)
        self.abtransport.set_mqtt(mqtt_verbindung)
        self.lampen.set_mqtt(mqtt_verbindung)

    def on_message(self, msg):
        
        value = decode_bool(msg.payload)
        if value is None:
            print(f"Ungültige Payload auf {msg.topic}: {msg.payload!r}")
            return

        # Silo Top, type=bool, default=true
        if msg.topic.endswith("Top"):
            self.silo.sensor_top = value

        # Silo Bottom, type=bool, default=true
        elif msg.topic.endswith("Bottom"):
            self.silo.sensor_bottom = value
            self.send_silo_full(value)

        # Trichter an Schlauch, type=bool, default=false
        elif msg.topic.endswith("Funnel"):
            self.abtransport.funnel = value
            
        # NOT-AUS, type=bool, default=true
        elif msg.topic.endswith("/Emergency"):
            self.emergency = value
            self.send_emergency(value)
            

        elif msg.topic.endswith("M3SiloVoll"):
            self.m3_silo_full = value

        elif msg.topic.endswith("M3Not-Aus"):
            self.m3_emergency = value


        else:
            print("Topic Error.")
            print(msg.topic)

    def stop_all(self):
        return (self.ruettler.stop() and self.abtransport.stop_air())

    def transport_start(self):
        return self.ruettler.start()

    def transport_stop(self):
        return self.ruettler.stop()

    def air_start(self):
        return self.abtransport.start_air()

    def air_stop(self):
        return self.abtransport.stop_air()

    def send_emergency(self, value: bool):
        """Not aus an modul 1 schicken"""
        self.mqtt.mqtt_client.publish("MV/VPS/DeliveryStorage/M2_Emergency", encode_bool(value), qos=0)

    def send_silo_full(self, value: bool):
        """Silo voll status senden"""
        self.mqtt.mqtt_client.publish("MV/VPS/DeliveryStorage/M2_Silo_Full", encode_bool(value), qos=0)
