import time
import json
import paho.mqtt.client as mqtt
from .config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_BASE_TOPIC

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"Successfully connected to MQTT Broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
    else:
        print(f"Failed to connect, reason code: {reason_code}")

def main():
    print("--- Starting IoT Presence Node ---")
    
    # Initialize the MQTT Client (using API v2 for modern paho-mqtt support)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    
    # Connect to the broker
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
    
    # Start the network loop in a background thread to handle keep-alives and callbacks
    client.loop_start()
    
    test_node_id = "node_test_01"
    topic = f"{MQTT_BASE_TOPIC}/{test_node_id}"
    
    try:
        # Simulate a sensor reading every 3 seconds
        while True:
            payload = {
                "node_id": test_node_id,
                "location": {"x": 10, "y": 25},
                "timestamp": int(time.time()),
                "state": "detected"
            }
            
            # Publish the dictionary as a JSON formatted string
            client.publish(topic, json.dumps(payload))
            print(f"Published -> {topic}: {payload}")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nStopping script...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("Disconnected cleanly.")

if __name__ == "__main__":
    main()
