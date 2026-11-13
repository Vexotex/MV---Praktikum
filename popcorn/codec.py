"""Einheitliches Encoding/Decoding der MQTT-Payloads.

Format vom Broker (Sensor-Topics): b'{"value":true,"dataType":"Boolean"}'
"""
import json


def encode_bool(value: bool) -> str:
    """bool -> '{"value":true,"dataType":"Boolean"}' (gleiches Format wie der Broker)"""
    return json.dumps({"value": bool(value), "dataType": "Boolean"}, separators=(",", ":"))


def decode_bool(payload: bytes) -> bool | None:
    """Payload -> bool. Gibt None zurück, wenn die Payload nicht verstanden wird.

    Akzeptiert (tolerant, damit auch Gegenstellen mit anderem Format funktionieren):
      {"value": true}, {"value": 1}, true, 1, "true", "an"/"aus", "on"/"off" ...
    Wirft NIE eine Exception, da es im MQTT-Thread aufgerufen wird.
    """
    try:
        text = payload.decode("utf-8").strip()
    except (UnicodeDecodeError, AttributeError):
        return None

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = text  # kein JSON -> als Rohtext behandeln

    if isinstance(data, dict):
        data = data.get("value")

    if isinstance(data, bool):
        return data
    if isinstance(data, (int, float)) and data in (0, 1):
        return bool(data)
    if isinstance(data, str):
        s = data.strip().lower()
        if s in ("true", "1", "on", "an", "ein"):
            return True
        if s in ("false", "0", "off", "aus"):
            return False
    return None
