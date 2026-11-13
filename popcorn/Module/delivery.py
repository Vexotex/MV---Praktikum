"""Das Delivery Modul der Anlage: besitzt die Komponenten Silo, Foerderband und Abtransport."""

from popcorn.config import (
    TOPIC_PREFIX_DELIVERY_ACTORS, 
    TOPIC_PREFIX_DELIVERY_SENSORS, 
    TOPIC_DELIVERY_INTERFACES
)
from popcorn.komponenten import Foerderband, Silo, Abtransport, Lampen
import json


class Delivery:
    """Fasst alle Komponenten zusammen und verteilt eingehende MQTT-Nachrichten."""

    def __init__(self):

        # import mqtt_topics for Module from Config
        self.TOPIC_PREFIX_SENSORS = TOPIC_PREFIX_DELIVERY_SENSORS
        self.TOPIC_PREFIX_ACTORS = TOPIC_PREFIX_DELIVERY_ACTORS
        self.TOPIC_INTERFACES = TOPIC_DELIVERY_INTERFACES

        # initialise Components
        self.silo = Silo("silo", self.TOPIC_PREFIX_ACTORS)
        self.foerderband = Foerderband("foerderband", self.TOPIC_PREFIX_ACTORS)
        self.abtransport = Abtransport("abtransport", self.TOPIC_PREFIX_ACTORS)
        self.lampen = Lampen("lampen", self.TOPIC_PREFIX_ACTORS)
        self.emergency = True
        self.m2_emergency = True
        self.m2_silo_full = True

    def to_stop(self) -> bool:
        return (
            not self.emergency or
            self.abtransport.funnel or
            not self.m2_emergency
        )

    def from_bereit(self) -> bool:   
        return not (
            not self.silo.sensor_bottom or
            self.m2_silo_full
        )

    def from_laueft(self) -> bool:   
        return(
            not self.silo.sensor_bottom or
            self.m2_silo_full
        )

    def from_stop(self) -> bool:   
        return(
            not self.emergency or
            not self.silo.sensor_bottom or
            self.abtransport.funnel or
            not self.m2_emergency
        )

    def set_mqtt(self, mqtt_verbindung):
        """Verbindet Delivery und Komponenten mit der MQTT-Schnittstelle."""
        self.mqtt = mqtt_verbindung
        self.silo.set_mqtt(mqtt_verbindung)
        self.foerderband.set_mqtt(mqtt_verbindung)
        self.abtransport.set_mqtt(mqtt_verbindung)
        self.lampen.set_mqtt(mqtt_verbindung)

    def on_message(self, msg):
        
        value = self.decode_bool(msg)

        # Silo Top, type=bool, default=true
        if msg.topic.endswith("Top"):
            self.silo.sensor_top = value

        # Silo Bottom, type=bool, default=true
        elif msg.topic.endswith("Bottom"):
            self.silo.sensor_bottom = value

        # Trichter an Schlauch, type=bool, default=false
        elif msg.topic.endswith("Funnel"):
            self.abtransport.funnel = value
            
        # NOT-AUS, type=bool, default=true
        elif msg.topic.endswith("Emergency"):
            self.emergency = value

        # NOT-AUS Modul 2, type=bool, default=true
        elif msg.topic.endswith("M2_Emergency"):
            self.m2_emergency = value

        # Silo voll Modul 2, type=bool, default=false
        elif msg.topic.endswith("M2_Silo_Full"):
            self.m2_silo_full = value

        else:
            print("Topic Error:" + msg.topic)
            print()
            
    def stop_all(self):
        return (self.foerderband.stop() and self.abtransport.stop_air())

    def transport_start(self):
        return self.foerderband.start()

    def transport_stop(self):
        return self.foerderband.stop()

    def air_start(self):
        return self.abtransport.start_air()

    def air_stop(self):
        return self.abtransport.stop_air()

    def decode_bool(self, msg) -> bool:

        payload = msg.payload

        # print(f"mid: {msg.mid}")
        # print("topic: " + msg.topic)
        # print(f"payload: {payload}")

        try:
            decoded = json.loads(payload.decode("utf-8"))
            value = decoded["value"]

            # print(f"value: {value}")
            # print() 

            if not isinstance(value, bool):
                raise ValueError(
                    f"value ist kein Boolean: {value}"
                )

            return value

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"Ungültige MQTT-Payload: {e}") from e