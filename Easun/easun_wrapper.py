#!/usr/bin/env python3
"""
EASUN Wrapper - simulates mpp-solar behavior but working on PC
"""

import serial
import time
import struct
import json
import sys

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

def read_qpigs():
    """Read QPIGS data from EASUN"""
    try:
        # Open serial port with exact same settings as mpp-solar
        ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=2400,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1.0,
            write_timeout=1.0
        )
        
        # Multiple attempts to handle PC vs Raspberry Pi differences
        for attempt in range(3):
            # Clear buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            time.sleep(0.2)
            
            # Send QPIGS command
            command = "QPIGS"
            cmd_bytes = command.encode('ascii')
            crc = calculate_crc(cmd_bytes)
            crc_bytes = struct.pack('>H', crc)
            message = cmd_bytes + crc_bytes + b'\r'
            
            # Send command
            ser.write(message)
            ser.flush()
            
            # Wait longer on PC
            time.sleep(1.0)
            
            # Read response
            response = b''
            for _ in range(10):  # Multiple read attempts
                if ser.in_waiting > 0:
                    chunk = ser.read(ser.in_waiting)
                    response += chunk
                    time.sleep(0.1)
                else:
                    time.sleep(0.1)
            
            if response and len(response) > 50:
                break
        
        ser.close()
        
        if response:
            # Parse like mpp-solar would
            text = response[:-3].decode('ascii', errors='ignore')
            
            if text.startswith('('):
                # Remove parentheses
                data = text[1:-1] if text.endswith(')') else text[1:]
                values = data.split()
                
                if len(values) >= 17:
                    # Create mpp-solar compatible JSON
                    result = {
                        "_command": "QPIGS",
                        "_command_description": "General Status Parameters inquiry",
                        "grid_voltage": {"value": float(values[0]), "unit": "V"},
                        "grid_frequency": {"value": float(values[1]), "unit": "Hz"},
                        "ac_output_voltage": {"value": float(values[2]), "unit": "V"},
                        "ac_output_frequency": {"value": float(values[3]), "unit": "Hz"},
                        "ac_output_apparent_power": {"value": int(values[4]), "unit": "VA"},
                        "ac_output_active_power": {"value": int(values[5]), "unit": "W"},
                        "output_load_percent": {"value": int(values[6]), "unit": "%"},
                        "bus_voltage": {"value": int(values[7]), "unit": "V"},
                        "battery_voltage": {"value": float(values[8].replace('!', '')), "unit": "V"},
                        "battery_charging_current": {"value": int(values[9]), "unit": "A"},
                        "battery_capacity": {"value": int(values[10]), "unit": "%"},
                        "inverter_temperature": {"value": int(values[11]), "unit": "°C"},
                        "pv_input_current": {"value": float(values[12]), "unit": "A"},
                        "pv_input_voltage": {"value": float(values[13]), "unit": "V"},
                        "battery_voltage_scc": {"value": float(values[14]), "unit": "V"},
                        "battery_discharge_current": {"value": int(values[15]), "unit": "A"}
                    }
                    
                    return result
    
    except Exception as e:
        return {"error": str(e)}
    
    return {"error": "No response from inverter"}

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode
        result = read_qpigs()
        if "error" not in result:
            print("✓ EASUN communication successful!")
            print(f"Battery: {result['battery_voltage']['value']}V")
            print(f"PV Power: {result['pv_input_voltage']['value'] * result['pv_input_current']['value']:.1f}W")
            print(f"AC Output: {result['ac_output_active_power']['value']}W")
        else:
            print(f"✗ Error: {result['error']}")
    else:
        # Normal mode - output JSON like mpp-solar
        result = read_qpigs()
        print(json.dumps(result))

if __name__ == "__main__":
    main()