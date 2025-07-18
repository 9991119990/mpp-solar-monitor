#!/usr/bin/env python3
"""
Test MQTT connection to Home Assistant
"""

import json
import subprocess
import sys

def test_mqtt_publish():
    """Test MQTT publishing with dummy data"""
    
    # Dummy EASUN data (similar to what mpp-solar would produce)
    dummy_data = {
        "_command": "QPIGS",
        "_command_description": "General Status Parameters inquiry",
        "grid_voltage": {"value": 230.0, "unit": "V"},
        "grid_frequency": {"value": 50.0, "unit": "Hz"},
        "ac_output_voltage": {"value": 230.0, "unit": "V"},
        "ac_output_frequency": {"value": 50.0, "unit": "Hz"},
        "ac_output_apparent_power": {"value": 344, "unit": "VA"},
        "ac_output_active_power": {"value": 327, "unit": "W"},
        "output_load_percent": {"value": 5, "unit": "%"},
        "bus_voltage": {"value": 383, "unit": "V"},
        "battery_voltage": {"value": 51.40, "unit": "V"},
        "battery_charging_current": {"value": 0, "unit": "A"},
        "battery_capacity": {"value": 42, "unit": "%"},
        "inverter_temperature": {"value": 26, "unit": "°C"},
        "pv_input_current": {"value": 0.0, "unit": "A"},
        "pv_input_voltage": {"value": 172.1, "unit": "V"},
        "battery_voltage_scc": {"value": 0.00, "unit": "V"},
        "battery_discharge_current": {"value": 4, "unit": "A"}
    }
    
    print("Testing MQTT connection with dummy EASUN data")
    print("=" * 60)
    
    # You need to update these with your actual HA details
    MQTT_BROKER = "192.168.68.250"  # Replace with your HA IP
    MQTT_USER = "your_ha_user"       # Replace with your HA username
    MQTT_PASS = "your_ha_password"   # Replace with your HA password
    MQTT_TOPIC = "easun/inverter/QPIGS"
    
    json_data = json.dumps(dummy_data)
    
    try:
        # Test MQTT publish
        cmd = [
            'mosquitto_pub',
            '-h', MQTT_BROKER,
            '-p', '1883',
            '-u', MQTT_USER,
            '-P', MQTT_PASS,
            '-t', MQTT_TOPIC,
            '-m', json_data
        ]
        
        print(f"Publishing to: {MQTT_BROKER}")
        print(f"Topic: {MQTT_TOPIC}")
        print(f"Data: {json_data[:100]}...")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("\n✓ MQTT publish successful!")
            print("\nCheck in Home Assistant:")
            print("1. Settings → Devices & services → MQTT")
            print("2. Configure → Listen to a topic")
            print(f"3. Enter topic: {MQTT_TOPIC}")
            print("\nYou should see the dummy data!")
        else:
            print(f"\n✗ MQTT publish failed:")
            print(f"Error: {result.stderr}")
            print("\nCheck:")
            print("1. MQTT broker IP address")
            print("2. Username/password")
            print("3. Network connectivity")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure to update MQTT_BROKER, MQTT_USER, MQTT_PASS")

if __name__ == "__main__":
    test_mqtt_connection()
    
    print("\n" + "=" * 60)
    print("TO FIX SERIAL COMMUNICATION:")
    print("1. Try physically disconnecting and reconnecting USB cable")
    print("2. Try different USB port")
    print("3. Restart the inverter")
    print("4. Test on Raspberry Pi directly if possible")
    print("5. Check cable - might need different one for PC vs RPi")