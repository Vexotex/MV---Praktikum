"""Komponenten des Moduls."""
import json

class Komponente:
    """Basisklasse für alle Komponenten."""

    def __init__(self, name: str, topic):
        self.name = name
        self.topic = topic
    
    def set_mqtt(self, verbindung):
        self.verbindung = verbindung


class Silo(Komponente):
    def __init__(self, name: str, topic):
        super().__init__(name, topic)
        self.sensor_bottom = False
        self.sensor_top = False


class Foerderband(Komponente):
    def __init__(self, name: str, topic):
        super().__init__(name, topic)
        self.running = False

    def start(self):
        """Foerderband starten, MQTT publish"""

        info = self.verbindung.mqtt_client.publish(self.topic + "Actor", "true", qos=1)

        try:
            info.wait_for_publish()

            self.running = True
            return True
        except RuntimeError:
            return False

    def stop(self):
        """Foerderband stoppen, MQTT publish"""

        info = self.verbindung.mqtt_client.publish(self.topic + "Actor", "false", qos=1)

        try:
            info.wait_for_publish()

            self.running = False
            return True
        except RuntimeError:
            return False



class Abtransport(Komponente):
    def __init__(self, name: str, topic):
        super().__init__(name, topic)
        self.air = False
        self.funnel = False

    def start_air(self):
        """Druckluft starten, MQTT publish"""

        info = self.verbindung.mqtt_client.publish(self.topic + "Air", "true", qos=1)

        try:
            info.wait_for_publish()

            self.air = True
            return True
        except RuntimeError:
            return False
        
    def stop_air(self):
        """Foerderband stoppen, MQTT publish"""

        info = self.verbindung.mqtt_client.publish(self.topic + "Air", "false", qos=1)

        try:
            info.wait_for_publish()

            self.air = False
            return True
        except RuntimeError:
            return False
        
class Lampen(Komponente):
    def __init__(self, name, topic):
        super().__init__(name, topic)
        self.lampen = {"Red" : "false",
                       "Yellow" : "false",
                       "Green" : "false"}

    def set_lampen(self, red : str, yellow : str, green : str):
        """ lampen setzen, input red, yellow, green = {"true" | "false"}"""
        allowed = ["true", "false"]
        if not(red in allowed and yellow in allowed and green in allowed):
            return False

        payload = json.dumps({"Red" : red,
                   "Yellow" : yellow,
                   "Green" : green}).encode("utf-8")

        info = self.verbindung.mqtt_client.publish(self.topic + "Lampen", payload, qos=1)

        try:    
            info.wait_for_publish(10)
            print("wait done")
            self.lampen = payload
            return True
        except RuntimeError:
            return False