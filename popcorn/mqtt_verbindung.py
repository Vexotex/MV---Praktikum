"""Dünner Wrapper um den MQTT-Client."""
import config
from paho.mqtt.client import Client


class MqttVerbindung:
    """Kapselt Verbindung, Publish und Subscribe zum Broker."""

    def __init__(self):
        # initalize the mqtt_client and its function
        self.mqtt_client = Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_connect_fail = self.on_connect_fail
        self.mqtt_client.on_message = self.on_message

        # start the connection
        self.mqtt_client.connect(
            config.BROKER_HOST,
            config.BROKER_PORT
            )

    def on_connect(self):
        return self.mqtt_client

    def on_connect_fail(self):
        return None

    def on_message(self):
        