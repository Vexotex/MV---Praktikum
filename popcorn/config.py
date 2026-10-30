"""Zentrale Konfiguration: Broker und Topics."""

# MQTT-Broker
BROKER_HOST = "dover.init.th-owl.de"
BROKER_PORT = 1884 # wichtig! nicht standard MQTT Port
USER = "dover_python"
PASSWORD = "inIT2025!" 

# VariablenDoku = http://executor.init.th-owl.de/mv2526

TOPIC_PREFIX_DELIVERY_SENSORS = "MV/VPS/Sensors/Delivery/"
TOPIC_PREFIX_DELIVERY_ACTORS = "MV/VPS/Delivery/Transport/"

TOPIC_PREFIX_STORAGE_SENSORS = "MV/VPS/Sensors/Storage/"
TOPIC_PREFIX_STORAGE_ACTORS = "MV/VPS/Storage/Transport/"

# konstanten
intervall = 0.1 # des Zustandsautomaten
