"""Das Modul der Anlage: besitzt die Komponenten."""

from popcorn.komponenten import Ruettler, Silo, Abtransport
from popcorn import config


class Delivery:
    """Fasst alle Komponenten zusammen und verteilt eingehende MQTT-Nachrichten."""

    def __init__(self):

        # import mqtt_topics for Module from Config
        self.TOPIC_PREFIX_SENSORS = config.TOPIC_PREFIX_DELIVERY_SENSORS
        self.TOPIC_PREFIX_ACTORS = config.TOPIC_PREFIX_DELIVERY_ACTORS

        # initialise Components
        self.silo = Silo("silo", self.TOPIC_PREFIX_ACTORS)
        self.foerderband = Ruettler("ruettler", self.TOPIC_PREFIX_ACTORS)
        self.abtransport = Abtransport("abtransport", self.TOPIC_PREFIX_ACTORS)


    def set_mqtt(self, mqtt_verbindung):
        """Verbindet Delivery und Komponenten mit der MQTT-Schnittstelle."""
        self.mqtt = mqtt_verbindung
        self.silo.set_mqtt(mqtt_verbindung)
        self.ruettler.set_mqtt(mqtt_verbindung)
        self.abtransport.set_mqtt(mqtt_verbindung)

    def on_message(self, msg):
        
        value = self.decode_bool(msg.payload)

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


        else:
            print("Topic Error.")

    def decode_bool(payload: bytes) -> bool:
        value = payload.decode("utf-8").strip().lower()

        if value == "true":
            return True
        if value == "false":
            return False

        raise ValueError(f"Ungültiger Boolean-Payload: {value!r}")        