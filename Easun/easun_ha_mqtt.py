#!/usr/bin/env python3
"""
EASUN to Home Assistant MQTT integration
Sends data with Home Assistant auto-discovery
"""

import serial
import time
import struct
import json
import logging
import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
MQTT_BROKER = "192.168.68.250"
MQTT_PORT = 1883
MQTT_USER = "mppclient"
MQTT_PASS = "supersecret"
MQTT_TOPIC_PREFIX = "easun"
DEVICE_ID = "easun_shm2_7k"

def calculate_crc(data):
    """Calculate CRC16-XMODEM checksum"""
    crc = 0
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

def read_easun_data(port='/dev/ttyUSB0', timeout=3.0):
    """Read data from EASUN inverter - using working code from live monitor"""
    try:
        ser = serial.Serial(port, 2400, timeout=timeout)
        ser.dtr = True
        time.sleep(0.1)
        
        # Send QPIGS command (hex format that works)
        cmd = bytes.fromhex('5150494753b7a90d')
        ser.write(cmd)
        time.sleep(0.3)
        
        response = ser.read(300)
        ser.close()
        
        if response:
            response_text = response.decode('utf-8', errors='ignore')
            
            # Parse response using working parser
            import re
            match = re.search(r'\(([0-9\.\s]+)', response_text)
            if not match:
                return {"error": "No valid response pattern"}
                
            values = match.group(1).strip().split()
            
            if len(values) >= 21:
                result = {
                    "grid_voltage": float(values[0]),
                    "grid_frequency": float(values[1]),
                    "ac_output_voltage": float(values[2]),
                    "ac_output_frequency": float(values[3]),
                    "ac_output_apparent_power": int(values[4]),
                    "ac_output_active_power": int(values[5]),
                    "output_load_percent": int(values[6]),
                    "bus_voltage": int(values[7]),
                    "battery_voltage": float(values[8]),
                    "battery_charging_current": int(values[9]),
                    "battery_capacity": int(values[10]),
                    "inverter_temperature": int(values[11]),
                    "pv_input_current": int(values[12]),
                    "pv_input_voltage": float(values[13]),
                    "battery_voltage_scc": float(values[14]),
                    "battery_discharge_current": int(values[15])
                }
                
                # Use real PV power from values[19] (like live monitor)
                result["pv_input_power"] = int(values[19]) if len(values) > 19 and values[19].isdigit() else 0
                return result
                
        return {"error": "No valid response"}
    
    except Exception as e:
        logger.error(f"Communication error: {e}")
        return {"error": str(e)}

def setup_ha_discovery(client):
    """Setup Home Assistant auto-discovery"""
    sensors = {
        "grid_voltage": {"name": "Grid Voltage", "unit": "V", "icon": "mdi:transmission-tower"},
        "grid_frequency": {"name": "Grid Frequency", "unit": "Hz", "icon": "mdi:sine-wave"},
        "ac_output_voltage": {"name": "AC Output Voltage", "unit": "V", "icon": "mdi:power-plug"},
        "ac_output_frequency": {"name": "AC Output Frequency", "unit": "Hz", "icon": "mdi:sine-wave"},
        "ac_output_apparent_power": {"name": "AC Output Apparent Power", "unit": "VA", "icon": "mdi:flash"},
        "ac_output_active_power": {"name": "AC Output Active Power", "unit": "W", "icon": "mdi:flash"},
        "output_load_percent": {"name": "Output Load", "unit": "%", "icon": "mdi:gauge"},
        "bus_voltage": {"name": "Bus Voltage", "unit": "V", "icon": "mdi:transmission-tower"},
        "battery_voltage": {"name": "Battery Voltage", "unit": "V", "icon": "mdi:battery"},
        "battery_charging_current": {"name": "Battery Charging Current", "unit": "A", "icon": "mdi:battery-charging"},
        "battery_capacity": {"name": "Battery Capacity", "unit": "%", "icon": "mdi:battery"},
        "inverter_temperature": {"name": "Inverter Temperature", "unit": "°C", "icon": "mdi:thermometer"},
        "pv_input_current": {"name": "PV Input Current", "unit": "A", "icon": "mdi:solar-power"},
        "pv_input_voltage": {"name": "PV Input Voltage", "unit": "V", "icon": "mdi:solar-power"},
        "pv_input_power": {"name": "PV Input Power", "unit": "W", "icon": "mdi:solar-power"},
        "battery_voltage_scc": {"name": "Battery Voltage SCC", "unit": "V", "icon": "mdi:battery"},
        "battery_discharge_current": {"name": "Battery Discharge Current", "unit": "A", "icon": "mdi:battery-minus"}
    }
    
    for sensor_id, config in sensors.items():
        discovery_topic = f"homeassistant/sensor/{DEVICE_ID}_{sensor_id}/config"
        state_topic = f"{MQTT_TOPIC_PREFIX}/sensor/{sensor_id}/state"
        
        discovery_payload = {
            "name": config["name"],
            "unique_id": f"{DEVICE_ID}_{sensor_id}",
            "state_topic": state_topic,
            "unit_of_measurement": config["unit"],
            "icon": config["icon"],
            "device": {
                "identifiers": [DEVICE_ID],
                "name": "EASUN SHM II 7K",
                "model": "SHM II 7K",
                "manufacturer": "EASUN"
            }
        }
        
        client.publish(discovery_topic, json.dumps(discovery_payload), retain=True)
        logger.info(f"Published discovery for {sensor_id}")

def publish_data(client, data):
    """Publish sensor data to MQTT"""
    for sensor_id, value in data.items():
        if not sensor_id.startswith('error'):
            topic = f"{MQTT_TOPIC_PREFIX}/sensor/{sensor_id}/state"
            client.publish(topic, str(value), retain=True)
    
    logger.info(f"Published data: PV={data.get('pv_input_power', 0):.1f}W, Battery={data.get('battery_voltage', 0):.1f}V ({data.get('battery_capacity', 0)}%)")

def main():
    """Main function"""
    try:
        # Setup MQTT client
        client = mqtt.Client()
        client.username_pw_set(MQTT_USER, MQTT_PASS)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Setup Home Assistant discovery
        setup_ha_discovery(client)
        
        # Main loop
        while True:
            data = read_easun_data()
            
            if 'error' not in data:
                publish_data(client, data)
                print(f"✓ Data sent: PV={data['pv_input_power']:.1f}W, Battery={data['battery_voltage']:.1f}V ({data['battery_capacity']}%)")
            else:
                logger.error(f"Read error: {data['error']}")
            
            time.sleep(30)  # Send every 30 seconds
            
    except KeyboardInterrupt:
        logger.info("Stopping...")
        client.disconnect()
    except Exception as e:
        logger.error(f"Main error: {e}")

if __name__ == "__main__":
    main()