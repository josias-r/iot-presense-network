"""Configuration settings and topic hierarchy definitions."""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "127.0.0.1")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_KEEPALIVE_SEC = int(os.getenv("MQTT_KEEPALIVE_SEC", "60"))

FOREST_ROOT_TOPIC = os.getenv("FOREST_ROOT_TOPIC", "forest")

class Topics:
    """Standardized MQTT topic naming conventions across the project."""

    # Sensor
    SENSOR_HEARTBEAT_PATTERN = f"{FOREST_ROOT_TOPIC}/sensors/+/heartbeat"
    SENSOR_STATUS_PATTERN = f"{FOREST_ROOT_TOPIC}/sensors/+/status"
    SENSOR_MOTION_PATTERN = f"{FOREST_ROOT_TOPIC}/sensors/+/motion"

    @staticmethod
    def sensor_heartbeat(sensor_id: str) -> str:
        return f"{FOREST_ROOT_TOPIC}/sensors/{sensor_id}/heartbeat"

    @staticmethod
    def sensor_status(sensor_id: str) -> str:
        return f"{FOREST_ROOT_TOPIC}/sensors/{sensor_id}/status"

    @staticmethod
    def sensor_motion(sensor_id: str) -> str:
        return f"{FOREST_ROOT_TOPIC}/sensors/{sensor_id}/motion"

    # Warning Sign
