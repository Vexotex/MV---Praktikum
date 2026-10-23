"""Dünner Wrapper um den MQTT-Client."""


class MqttVerbindung:
    """Kapselt Verbindung, Publish und Subscribe zum Broker."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        # TODO: paho-mqtt Client anlegen

    def verbinden(self):
        # TODO
        pass

    def trennen(self):
        # TODO
        pass

    def senden(self, topic: str, nachricht: str):
        # TODO
        pass

    def abonnieren(self, topic: str, callback):
        # TODO
        pass
