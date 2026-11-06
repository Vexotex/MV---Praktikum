"""Dünner Wrapper um den MQTT-Client."""
from popcorn.config import (BROKER_HOST, BROKER_PORT, USER, PASSWORD)
from paho.mqtt.client import Client


class MqttVerbindung:
    """Kapselt Verbindung, Publish und Subscribe zum Broker."""

    def __init__(self, modul):

        self.modul = modul

        # initalize the mqtt_client and its functions
        self.mqtt_client = Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        print("on_message referred")

        self.mqtt_client.username_pw_set(USER, PASSWORD)

        # start the connection
        self.mqtt_client.connect(
            host = BROKER_HOST,
            port = BROKER_PORT
            )
        self.mqtt_client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if  rc != 0:
            print(f"Failed to connect: {rc}")
            return None

        client.subscribe(self.modul.TOPIC_PREFIX_SENSORS + "#")
        print("Subscribed to " + self.modul.TOPIC_PREFIX_SENSORS + "#")
        for interface in self.modul.TOPIC_INTERFACES:
            client.subscribe(interface)
            print("Subscribed to " + interface)
        print("MQTT connection established.")

    def on_message(self, client, userdata, msg):
        self.modul.on_message(msg)