"""Configuration settings and topic hierarchy definitions."""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

# MQTT Broker Configuration
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "127.0.0.1")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_KEEPALIVE_SEC = int(os.getenv("MQTT_KEEPALIVE_SEC", "60"))

# Topic Namespace Roots
FOREST_ROOT_TOPIC = os.getenv("FOREST_ROOT_TOPIC", "forest")


class Topics:
    """Standardized MQTT topic naming conventions."""

    # Sensor topics
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

    # Spatial Hazard Alerts (Decoupled Broadcast)
    ALERTS_GLOBAL = f"{FOREST_ROOT_TOPIC}/alerts"

    @staticmethod
    def alerts_sector(sector_id: str) -> str:
        return f"{FOREST_ROOT_TOPIC}/alerts/{sector_id}"

    # Warning Sign status / health
    WARNING_SIGN_STATUS_PATTERN = f"{FOREST_ROOT_TOPIC}/warning_signs/+/status"

    @staticmethod
    def warning_sign_status(sign_id: str) -> str:
        return f"{FOREST_ROOT_TOPIC}/warning_signs/{sign_id}/status"
