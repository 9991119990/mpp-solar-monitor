#!/usr/bin/env python3
"""
Advanced EASUN SHM II 7K Test Script
Tests different baud rates and protocols
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

def test_connection(port_name, baud_rate, timeout=2.0):
    """Test connection with specific settings"""
    print(f"\nTesting {port_name} at {baud_rate} baud...")
    
    try:
        port = serial.Serial(
            port=port_name,
            baudrate=baud_rate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )
        
        # Clear buffers
        port.reset_input_buffer()
        port.reset_output_buffer()
        
        # Send QPIGS command
        command = "QPIGS"
        cmd_bytes = command.encode('ascii')
        crc = calculate_crc(cmd_bytes)
        crc_bytes = struct.pack('>H', crc)
        message = cmd_bytes + crc_bytes + b'\r'
        
        print(f"Sending: {message.hex()} ({command})")
        port.write(message)
        port.flush()
        
        # Read response with multiple attempts
        response = b''
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if port.in_waiting > 0:
                chunk = port.read(port.in_waiting)
                response += chunk
                # Check if we got end of response
                if b'\r' in chunk:
                    break
            time.sleep(0.05)
        
        port.close()
        
        if response:
            print(f"Response length: {len(response)} bytes")
            print(f"Response (hex): {response.hex()}")
            
            # Try to parse response
            if len(response) > 3:
                # Remove CR and CRC (last 3 bytes)
                data = response[:-3]
                try:
                    text = data.decode('ascii', errors='ignore')
                    print(f"Response (text): {text}")
                    
                    # Check if it looks like a valid QPIGS response
                    if text.startswith('(') and len(text) > 50:
                        print("✓ Valid QPIGS response detected!")
                        return True
                except:
                    pass
        else:
            print("No response")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return False

def test_all_settings():
    """Test different baud rates and settings"""
    port_name = '/dev/ttyUSB0'
    
    # Common baud rates for inverters
    baud_rates = [2400, 4800, 9600, 19200, 38400, 57600, 115200]
    
    print("EASUN SHM II 7K Communication Test")
    print("=" * 60)
    
    for baud in baud_rates:
        if test_connection(port_name, baud):
            print(f"\n✓ SUCCESS: Communication established at {baud} baud!")
            return baud
    
    print("\n✗ Failed to establish communication with any baud rate")
    
    # Try with different timeout
    print("\nTrying with longer timeout (5 seconds)...")
    for baud in [2400, 9600]:
        if test_connection(port_name, baud, timeout=5.0):
            print(f"\n✓ SUCCESS: Communication established at {baud} baud with longer timeout!")
            return baud
    
    return None

def main():
    # Find working baud rate
    working_baud = test_all_settings()
    
    if working_baud:
        print(f"\n\nRecommended settings:")
        print(f"- Port: /dev/ttyUSB0")
        print(f"- Baud rate: {working_baud}")
        print(f"- Protocol: PI30")
        print(f"\nYou can now use:")
        print(f"mpp-solar -p /dev/ttyUSB0 -P PI30 -b {working_baud} -c QPIGS")

if __name__ == "__main__":
    main()