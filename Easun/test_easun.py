#!/usr/bin/env python3
"""
EASUN SHM II 7K Test Script
Test basic communication with the inverter
"""

import serial
import time
import struct

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

def send_command(port, command):
    """Send command to inverter and get response"""
    # Convert command to bytes
    cmd_bytes = command.encode('ascii')
    
    # Calculate CRC
    crc = calculate_crc(cmd_bytes)
    crc_bytes = struct.pack('>H', crc)
    
    # Build full message: command + CRC + CR
    message = cmd_bytes + crc_bytes + b'\r'
    
    print(f"Sending: {message.hex()}")
    
    # Send command
    port.write(message)
    port.flush()
    
    # Wait for response
    time.sleep(0.5)
    
    # Read response
    response = b''
    while port.in_waiting:
        response += port.read(port.in_waiting)
        time.sleep(0.1)
    
    return response

def main():
    print("EASUN SHM II 7K Communication Test")
    print("-" * 40)
    
    # Serial port configuration
    port_name = '/dev/ttyUSB0'
    baud_rate = 2400
    
    try:
        # Open serial port
        port = serial.Serial(
            port=port_name,
            baudrate=baud_rate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=2.0,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )
        
        print(f"Port {port_name} opened successfully")
        print(f"Settings: {baud_rate} baud, 8N1")
        print()
        
        # Test commands
        commands = [
            ("QPI", "Protocol ID inquiry"),
            ("QPIGS", "General status parameters inquiry"),
            ("QMOD", "Device mode inquiry"),
            ("QPIWS", "Device warning status inquiry")
        ]
        
        for cmd, desc in commands:
            print(f"Testing {cmd} - {desc}")
            response = send_command(port, cmd)
            
            if response:
                print(f"Response (hex): {response.hex()}")
                # Try to decode as ASCII (skip CRC and CR at end)
                try:
                    text = response[:-3].decode('ascii', errors='ignore')
                    print(f"Response (text): {text}")
                except:
                    print("Could not decode response as text")
            else:
                print("No response received")
            
            print("-" * 40)
            time.sleep(1)
        
        port.close()
        
    except serial.SerialException as e:
        print(f"Serial port error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()