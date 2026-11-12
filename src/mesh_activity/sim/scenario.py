"""Simulation harness: spins up simulated sensors, signs, and an analyzer to demonstrate the pipeline."""

import logging
import time

from mesh_activity.common.models import GeoPoint
from mesh_activity.nodes.sensor import SensorNode
from mesh_activity.nodes.warning_sign import WarningSignNode
from mesh_activity.analyzer.analyzer import AnalyzerNode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def run_demo_simulation() -> None:
    """Sets up a virtual forest, starts the analyzer, and simulates animal movement."""
    print("\n=== STARTING IOT WILDLIFE MESH SIMULATION ===\n")

    # 1. Start Analyzer
    analyzer = AnalyzerNode()
    analyzer.connect()

    # 2. Start Warning Signs along the roadway
    # Sign 1 is near the road crossing (lat=47.3780, lon=8.5430)
    sign_near = WarningSignNode(
        sign_id="sign_road_km12",
        location=GeoPoint(latitude=47.3780, longitude=8.5430),
        warning_radius_meters=200.0,
    )
    # Sign 2 is far away down the road (lat=47.3900, lon=8.5600)
    sign_far = WarningSignNode(
        sign_id="sign_road_km15",
        location=GeoPoint(latitude=47.3900, longitude=8.5600),
        warning_radius_meters=200.0,
    )
    sign_near.connect()
    sign_far.connect()

    # 3. Deploy Sensor Nodes along a forest path heading toward km12
    sensor1 = SensorNode(sensor_id="sensor_01", location=GeoPoint(latitude=47.3760, longitude=8.5410))
    sensor2 = SensorNode(sensor_id="sensor_02", location=GeoPoint(latitude=47.3768, longitude=8.5418))
    sensor3 = SensorNode(sensor_id="sensor_03", location=GeoPoint(latitude=47.3775, longitude=8.5425))

    sensor1.connect()
    sensor2.connect()
    sensor3.connect()

    time.sleep(1.0)  # Let MQTT connections settle

    try:
        print("\n--- Simulating animal movement through the forest ---")
        # Step 1: Animal triggers sensor 1
        sensor1.trigger_motion()
        time.sleep(3.0)

        # Step 2: Animal moves to sensor 2 (Correlator recognizes track, predicts trajectory!)
        sensor2.trigger_motion()
        time.sleep(3.0)

        # Step 3: Animal moves to sensor 3 (Track updated, new alert dispatched)
        sensor3.trigger_motion()
        time.sleep(5.0)

    finally:
        print("\n--- Cleaning up simulation nodes ---")
        sensor1.stop()
        sensor2.stop()
        sensor3.stop()
        sign_near.stop()
        sign_far.stop()
        analyzer.disconnect()
        print("Simulation ended cleanly.")


if __name__ == "__main__":
    run_demo_simulation()
