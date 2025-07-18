#!/usr/bin/env python3
"""
EASUN to Home Assistant direct integration for Raspberry Pi
Based on working configuration and online research
"""

import serial
import time
import struct
import json
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    """Read data from EASUN inverter with Raspberry Pi specific settings"""
    try:
        # Open serial port with settings optimized for Raspberry Pi
        ser = serial.Serial(
            port=port,
            baudrate=2400,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
            write_timeout=timeout,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )
        
        # CRITICAL: Set DTR to True for EASUN communication
        ser.dtr = True
        ser.rts = False
        
        # Clear buffers and wait
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.5)
        
        # Send QPIGS command
        command = "QPIGS"
        cmd_bytes = command.encode('ascii')
        crc = calculate_crc(cmd_bytes)
        crc_bytes = struct.pack('>H', crc)
        message = cmd_bytes + crc_bytes + b'\r'
        
        logger.info(f"Sending command: {message.hex()}")
        
        # Send command
        ser.write(message)
        ser.flush()
        
        # Wait for response - Raspberry Pi specific timing
        time.sleep(2.0)  # As per original working configuration
        
        # Read response - simple approach that worked on external PC
        response = ser.read(1000)  # Read up to 1000 bytes
        
        logger.info(f"Received {len(response)} bytes: {response[:50]}...")
        
        ser.close()
        
        if response and len(response) > 50:
            # Parse response
            try:
                # Find start and end of data
                start_idx = response.find(b'(')
                end_idx = response.find(b')')
                
                if start_idx >= 0 and end_idx > start_idx:
                    data_text = response[start_idx+1:end_idx].decode('ascii', errors='ignore')
                    values = data_text.split()
                    
                    logger.info(f"Parsed {len(values)} values")
                    
                    if len(values) >= 17:
                        # Create structured data
                        result = {
                            "grid_voltage": float(values[0]),
                            "grid_frequency": float(values[1]),
                            "ac_output_voltage": float(values[2]),
                            "ac_output_frequency": float(values[3]),
                            "ac_output_apparent_power": int(values[4]),
                            "ac_output_active_power": int(values[5]),
                            "output_load_percent": int(values[6]),
                            "bus_voltage": int(values[7]),
                            "battery_voltage": float(values[8].replace('!', '')),
                            "battery_charging_current": int(values[9]),
                            "battery_capacity": int(values[10]),
                            "inverter_temperature": int(values[11]),
                            "pv_input_current": float(values[12]),
                            "pv_input_voltage": float(values[13]),
                            "battery_voltage_scc": float(values[14]),
                            "battery_discharge_current": int(values[15])
                        }
                        
                        # Calculate PV power
                        result["pv_input_power"] = result["pv_input_voltage"] * result["pv_input_current"]
                        
                        return result
                    else:
                        logger.error(f"Not enough values: {len(values)}")
                        return {"error": f"Incomplete data: only {len(values)} values"}
                else:
                    logger.error("Could not find valid data in response")
                    return {"error": "Invalid response format"}
                    
            except Exception as e:
                logger.error(f"Parse error: {e}")
                return {"error": f"Parse error: {str(e)}"}
        else:
            logger.error("No response or response too short")
            return {"error": "No response from inverter"}
    
    except Exception as e:
        logger.error(f"Communication error: {e}")
        return {"error": str(e)}

def send_to_mqtt(data, mqtt_config):
    """Send data to MQTT broker"""
    import paho.mqtt.client as mqtt
    
    try:
        client = mqtt.Client()
        client.username_pw_set(mqtt_config['user'], mqtt_config['password'])
        client.connect(mqtt_config['broker'], mqtt_config['port'], 60)
        
        # Send as JSON to single topic (like mpp-solar)
        topic = mqtt_config['topic']
        
        # Format data for Home Assistant
        mqtt_data = {}
        for key, value in data.items():
            if not key.startswith('error'):
                mqtt_data[key] = {
                    "value": value,
                    "unit": get_unit(key)
                }
        
        payload = json.dumps(mqtt_data)
        client.publish(topic, payload, retain=True)
        
        logger.info(f"Published to MQTT: {topic}")
        client.disconnect()
        return True
        
    except Exception as e:
        logger.error(f"MQTT error: {e}")
        return False

def get_unit(key):
    """Get unit for each measurement"""
    units = {
        "grid_voltage": "V",
        "grid_frequency": "Hz",
        "ac_output_voltage": "V",
        "ac_output_frequency": "Hz",
        "ac_output_apparent_power": "VA",
        "ac_output_active_power": "W",
        "output_load_percent": "%",
        "bus_voltage": "V",
        "battery_voltage": "V",
        "battery_charging_current": "A",
        "battery_capacity": "%",
        "inverter_temperature": "°C",
        "pv_input_current": "A",
        "pv_input_voltage": "V",
        "battery_voltage_scc": "V",
        "battery_discharge_current": "A",
        "pv_input_power": "W"
    }
    return units.get(key, "")

def main():
    # Configuration
    serial_port = os.getenv('EASUN_PORT', '/dev/ttyUSB0')
    
    mqtt_config = {
        'broker': os.getenv('MQTT_BROKER', '192.168.68.250'),
        'port': int(os.getenv('MQTT_PORT', '1883')),
        'user': os.getenv('MQTT_USER', 'homeassistant'),
        'password': os.getenv('MQTT_PASS', 'your_password'),
        'topic': os.getenv('MQTT_TOPIC', 'easun/inverter/QPIGS')
    }
    
    if '--test' in sys.argv:
        # Test mode - just read and print
        logger.info("Running in test mode")
        data = read_easun_data(serial_port)
        
        if 'error' not in data:
            print("\n✓ EASUN communication successful!")
            print(f"Battery: {data['battery_voltage']}V ({data['battery_capacity']}%)")
            print(f"PV: {data['pv_input_voltage']}V × {data['pv_input_current']}A = {data['pv_input_power']:.1f}W")
            print(f"AC Output: {data['ac_output_active_power']}W ({data['output_load_percent']}% load)")
            print(f"Temperature: {data['inverter_temperature']}°C")
            print("\nFull data:")
            print(json.dumps(data, indent=2))
        else:
            print(f"\n✗ Error: {data['error']}")
            sys.exit(1)
    else:
        # Production mode - read and send to MQTT
        data = read_easun_data(serial_port)
        
        if 'error' not in data:
            if send_to_mqtt(data, mqtt_config):
                logger.info("Data sent successfully")
                # Also output JSON for compatibility
                print(json.dumps(data))
            else:
                logger.error("Failed to send to MQTT")
                sys.exit(1)
        else:
            logger.error(f"Read error: {data['error']}")
            sys.exit(1)

if __name__ == "__main__":
    main()