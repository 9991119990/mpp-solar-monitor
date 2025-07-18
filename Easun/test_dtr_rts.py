#!/usr/bin/env python3
"""
Test serial communication with DTR/RTS control
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

def test_serial_configs():
    """Test different serial configurations"""
    port_name = '/dev/ttyUSB0'
    
    configs = [
        {'dtr': True, 'rts': True, 'name': 'DTR+RTS'},
        {'dtr': True, 'rts': False, 'name': 'DTR only'},
        {'dtr': False, 'rts': True, 'name': 'RTS only'},
        {'dtr': False, 'rts': False, 'name': 'No DTR/RTS'},
    ]
    
    for config in configs:
        print(f"\nTesting with {config['name']}...")
        
        try:
            ser = serial.Serial(
                port=port_name,
                baudrate=2400,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1
            )
            
            # Set DTR/RTS
            ser.dtr = config['dtr']
            ser.rts = config['rts']
            
            # Clear buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            time.sleep(0.5)
            
            # Send QPIGS command
            command = "QPIGS"
            cmd_bytes = command.encode('ascii')
            crc = calculate_crc(cmd_bytes)
            crc_bytes = struct.pack('>H', crc)
            message = cmd_bytes + crc_bytes + b'\r'
            
            print(f"Sending: {message.hex()}")
            ser.write(message)
            ser.flush()
            
            # Read response
            response = b''
            start_time = time.time()
            
            while time.time() - start_time < 2.0:
                if ser.in_waiting > 0:
                    chunk = ser.read(ser.in_waiting)
                    response += chunk
                    if b'\r' in chunk:
                        break
                time.sleep(0.05)
            
            ser.close()
            
            if response:
                print(f"Response: {len(response)} bytes")
                print(f"Hex: {response.hex()}")
                if len(response) > 20:
                    print("✓ Good response!")
                    return True
            else:
                print("No response")
                
        except Exception as e:
            print(f"Error: {e}")
    
    return False

def main():
    print("Testing serial configurations for EASUN inverter")
    print("=" * 60)
    
    if test_serial_configs():
        print("\n✓ Found working configuration!")
    else:
        print("\n✗ No working configuration found")
        print("\nPossible issues:")
        print("- Wrong cable (check if null modem/crossover is needed)")
        print("- Inverter not powered on or in standby")
        print("- Wrong protocol (try PI18 instead of PI30)")

if __name__ == "__main__":
    main()