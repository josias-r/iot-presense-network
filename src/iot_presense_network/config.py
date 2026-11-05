import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Read the variables, providing sensible fallbacks just in case
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "127.0.0.1")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
MQTT_BASE_TOPIC = os.getenv("MQTT_BASE_TOPIC", "project/presence")

# We can also construct derived variables here so we don't have to repeat logic later
def get_node_topic(node_id: str) -> str:
    """Returns the full topic string for a specific node, e.g., 'project/presence/node_A'"""
    return f"{MQTT_BASE_TOPIC}/{node_id}"
