#!/usr/bin/env python3
"""
Program to read AM2302 (DHT22) sensor on Raspberry Pi 4
This sensor can measure temperature and humidity
"""

import time
import json
from datetime import datetime
import board
import adafruit_dht
import paho.mqtt.client as mqtt

def main():
    # MQTT Configuration
    MQTT_BROKER = "localhost"
    MQTT_PORT = 1883
    MQTT_TOPIC = "sensors/dht22"
    
    # Initialize MQTT client
    mqtt_client = mqtt.Client()
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
        print("✓ Connected to MQTT broker")
    except Exception as e:
        print(f"✗ MQTT connection error: {e}")
        print("Continuing without MQTT...")
        mqtt_client = None
    
    # Initialize AM2302 (DHT22) sensor
    # Change board.D4 to the GPIO pin you are using (example: D4 = GPIO4)
    # Common pins: D4, D17, D18, D27, D22, D23, D24, D25
    dht_pin = board.D4  # GPIO4 - adjust according to your physical connection
    
    print("=" * 50)
    print("Initializing AM2302 (DHT22) sensor...")
    print(f"Using GPIO4 pin")
    print("=" * 50)
    
    try:
        dht_device = adafruit_dht.DHT22(dht_pin)
        print("✓ Sensor initialized successfully!\n")
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        print("Make sure the sensor is connected correctly.")
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
        return
    
    print("Reading AM2302 (DHT22) Sensor")
    print("=" * 50)
    print("Press Ctrl+C to exit\n")
    
    try:
        while True:
            try:
                # Read data from sensor
                temperature = dht_device.temperature
                humidity = dht_device.humidity
                
                # Create JSON payload with timestamp
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                payload = {
                    "timestamp": timestamp,
                    "sensor": "DHT22",
                    "location": "GPIO4",
                    "temperature": round(temperature, 1),
                    "humidity": round(humidity, 1),
                    "unit_temp": "celsius",
                    "unit_humidity": "percent"
                }
                
                # Convert to JSON string
                json_payload = json.dumps(payload)
                
                # Display readings
                print(f"Temperature: {temperature:.1f} °C")
                print(f"Humidity: {humidity:.1f} %")
                print(f"Timestamp: {timestamp}")
                
                # Publish to MQTT
                if mqtt_client:
                    try:
                        result = mqtt_client.publish(MQTT_TOPIC, json_payload)
                        if result.rc == 0:
                            print(f"✓ Published to MQTT topic: {MQTT_TOPIC} payload: {json_payload}")
                        else:
                            print(f"✗ Failed to publish to MQTT")
                    except Exception as e:
                        print(f"✗ MQTT publish error: {e}")
                
                print("-" * 50)
                
            except RuntimeError as error:
                # DHT sensor sometimes fails to read, this is normal
                print(f"Reading error: {error.args[0]}")
                time.sleep(2)
                continue
            
            # Wait 2 seconds before next reading
            # DHT22 requires minimum 2 seconds between readings
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\nProgram stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure the sensor is connected correctly to Raspberry Pi")
    finally:
        # Clean up MQTT connection
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            print("MQTT connection closed")

if __name__ == "__main__":
    main()
