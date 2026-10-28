"""Dünner Wrapper um den MQTT-Client."""
import config
from paho.mqtt.client import Client


class MqttVerbindung:
    """Kapselt Verbindung, Publish und Subscribe zum Broker."""

    def __init__(self, modul):

        self.modul = modul

        # initalize the mqtt_client and its functions
        self.mqtt_client = Client(Client.CallbackAPIVersion.VERSION2)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_connect_fail = self.on_connect_fail
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_subscribe = self.on_subscribe

        # start the connection
        self.mqtt_client.connect(
            config.BROKER_HOST,
            config.BROKER_PORT
            )

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(f"Failed to connect: {reason_code}")
            return None
        print("MQTT connection established.")
        client.subscribe(config.TOPIC_PREFIX_DELIVERY_ACTORS + "#")



    def on_message(self, client, userdata, msg):

        userdata.append(msg.payload)
        value = self.decode_bool(msg.payload)

        # Silo Top, type=bool, default=true
        if msg.topic.endswith("Top"):
            self.modul.update_top(value)

        # Silo Bottom, type=bool, default=true
        elif msg.topic.endswith("Bottom"):
            self.modul.update_bottom(value)

        # Trichter an Schlauch, type=bool, default=false
        elif msg.topic.endswith("Funnel"):
            self.modul.update_funnel(value)
            
        # NOT-AUS, type=bool, default=true
        elif msg.topic.endswith("Emergency"):
            self.modul.update_emergency(value)
        
        else:
            print("Topic Error.")

    def decode_bool(payload: bytes) -> bool:
        value = payload.decode("utf-8").strip().lower()

        if value == "true":
            return True
        if value == "false":
            return False

        raise ValueError(f"Ungültiger Boolean-Payload: {value!r}")