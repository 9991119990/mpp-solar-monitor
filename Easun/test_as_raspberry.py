#!/usr/bin/env python3
"""
Test EASUN exactly as it worked on Raspberry Pi
"""

import serial
import time
import struct
import json

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

def main():
    print("Testing EASUN as on Raspberry Pi")
    print("=" * 60)
    
    # Exactly same settings as worked on Raspberry
    port = serial.Serial(
        port='/dev/ttyUSB0',
        baudrate=2400,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=2,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False
    )
    
    # Clear buffers
    port.reset_input_buffer()
    port.reset_output_buffer()
    
    print("Port opened successfully")
    
    # Wait a bit
    time.sleep(1)
    
    # Send QPIGS
    command = "QPIGS"
    cmd_bytes = command.encode('ascii')
    crc = calculate_crc(cmd_bytes)
    crc_bytes = struct.pack('>H', crc)
    message = cmd_bytes + crc_bytes + b'\r'
    
    print(f"Sending: {message.hex()}")
    port.write(message)
    port.flush()
    
    # Wait for response - simple approach
    time.sleep(2)
    
    response = port.read(1000)  # Read up to 1000 bytes
    
    if response:
        print(f"Response: {len(response)} bytes")
        print(f"Hex: {response.hex()}")
        
        # Try to decode
        try:
            text = response.decode('ascii', errors='ignore')
            print(f"Text: {text}")
            
            # If it looks like QPIGS response
            if text.startswith('(') and len(text) > 50:
                print("\n✓ SUCCESS! Got valid response")
                
                # Parse for display
                data = text[1:-3]  # Remove ( and )\r\n
                values = data.split()
                
                print("\nData:")
                print(f"Battery: {values[8]} V")
                print(f"PV: {values[13]} V")
                print(f"AC Output: {values[5]} W")
                
                # Create JSON like mpp-solar
                result = {
                    "_command": "QPIGS",
                    "battery_voltage": {"value": float(values[8].replace('!', '')), "unit": "V"},
                    "pv_input_voltage": {"value": float(values[13]), "unit": "V"},
                    "ac_output_active_power": {"value": int(values[5]), "unit": "W"}
                }
                
                print("\nJSON output:")
                print(json.dumps(result, indent=2))
                
                return True
        except Exception as e:
            print(f"Parse error: {e}")
    else:
        print("No response")
    
    port.close()
    return False

if __name__ == "__main__":
    if main():
        print("\n✓ Communication working!")
        print("\nNow you need to:")
        print("1. Install mosquitto-clients: sudo apt install mosquitto-clients")
        print("2. Update MQTT credentials in send_easun_data.sh")
        print("3. Run: ./send_easun_data.sh")
    else:
        print("\n✗ Communication failed")
        print("\nCheck:")
        print("1. Is inverter powered on?")
        print("2. Correct cable connected?")
        print("3. Try different USB port")