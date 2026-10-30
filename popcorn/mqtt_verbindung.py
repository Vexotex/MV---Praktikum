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
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_subscribe = self.on_subscribe

        # start the connection
        self.mqtt_client.connect(
            config.BROKER_HOST,
            config.BROKER_PORT
            )

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            print(f"Failed to connect: {rc}")
            return None
        print("MQTT connection established.")
        client.subscribe(self.modul.TOPIC_PREFIX_SENSORS + "#")

    def on_message(self, client, userdata, msg):
        print("msg : " + msg)
        print()
        print("userdata :" + userdata)
        userdata.append(msg.payload)
        self.modul.on_message(msg)