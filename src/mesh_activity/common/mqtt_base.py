"""Base MQTT Node abstraction managing broker lifecycle, reconnects, and LWT."""

import json
import logging
from typing import Any, Callable, Dict, Optional
import paho.mqtt.client as mqtt

from mesh_activity.common.config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEPALIVE_SEC

logger = logging.getLogger(__name__)


class BaseMQTTNode:
    """Abstract base client for any node communicating over MQTT."""

    def __init__(
        self,
        client_id: str,
        lwt_topic: Optional[str] = None,
        lwt_payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.client_id = client_id
        self.lwt_topic = lwt_topic
        self.lwt_payload = lwt_payload or {"state": "offline"}

        # Use modern paho-mqtt API v2
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id,
        )

        self._configure_callbacks()
        self._configure_lwt()

    def _configure_callbacks(self) -> None:
        self.client.on_connect = self._on_connect_internal
        self.client.on_disconnect = self._on_disconnect_internal
        self.client.on_message = self._on_message_internal

    def _configure_lwt(self) -> None:
        if self.lwt_topic:
            self.client.will_set(
                topic=self.lwt_topic,
                payload=json.dumps(self.lwt_payload),
                qos=1,
                retain=True,
            )

    def connect(
        self,
        host: str = MQTT_BROKER_HOST,
        port: int = MQTT_BROKER_PORT,
        keepalive: int = MQTT_KEEPALIVE_SEC,
    ) -> None:
        """Connects to the broker and starts the background network loop."""
        logger.info(f"Connecting [{self.client_id}] to MQTT Broker at {host}:{port}...")
        self.client.connect(host, port, keepalive)
        self.client.loop_start()

    def disconnect(self) -> None:
        """Gracefully disconnects from the broker."""
        logger.info(f"Disconnecting [{self.client_id}] from MQTT Broker...")
        self.client.loop_stop()
        self.client.disconnect()

    def publish_json(
        self,
        topic: str,
        payload: Dict[str, Any] | str,
        qos: int = 1,
        retain: bool = False,
    ) -> None:
        """Helper to serialize and publish payloads."""
        body = payload if isinstance(payload, str) else json.dumps(payload)
        self.client.publish(topic, body, qos=qos, retain=retain)

    def subscribe(self, topic: str, qos: int = 1) -> None:
        """Subscribes to an MQTT topic pattern."""
        self.client.subscribe(topic, qos=qos)
        logger.debug(f"[{self.client_id}] Subscribed to topic: {topic}")

    # Internal MQTT Callbacks to be hooked by subclasses
    def _on_connect_internal(self, client: mqtt.Client, userdata: Any, flags: Any, reason_code: Any, properties: Any) -> None:
        if reason_code == 0:
            logger.info(f"[{self.client_id}] Connected successfully.")
            if self.lwt_topic:
                # Announce online state
                self.publish_json(self.lwt_topic, {"state": "online"}, qos=1, retain=True)
            self.on_connected()
        else:
            logger.error(f"[{self.client_id}] Connection failed with reason: {reason_code}")

    def _on_disconnect_internal(self, client: mqtt.Client, userdata: Any, flags: Any, reason_code: Any, properties: Any) -> None:
        logger.warning(f"[{self.client_id}] Disconnected (reason: {reason_code})")
        self.on_disconnected()

    def _on_message_internal(self, client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        try:
            payload_str = msg.payload.decode("utf-8")
            data = json.loads(payload_str)
            self.on_message_received(msg.topic, data)
        except Exception as e:
            logger.error(f"Failed to parse incoming message on {msg.topic}: {e}")

    # Extension hooks for child nodes
    def on_connected(self) -> None:
        """Hook called when connection succeeds."""
        pass

    def on_disconnected(self) -> None:
        """Hook called on disconnect."""
        pass

    def on_message_received(self, topic: str, payload: Dict[str, Any]) -> None:
        """Hook called when a JSON payload is received."""
        pass
