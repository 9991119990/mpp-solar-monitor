#!/usr/bin/env python3
"""
Test EASUN exactly like the working MPP Solar setup
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

def test_communication():
    """Test communication like MPP Solar"""
    port_name = '/dev/ttyUSB0'
    
    # Test response from your successful example:
    # Response (hex): 283030302e302030302e30202032392e382034392e392030333434203033323720303035203338332021312e3430203030302030343220303032362030303030203137322e312030302e30302030303030342030313031303131302030302030302030303130342030313017060d
    # That's "(000.0 00.0  29.8 49.9 0344 0327 005 383 !1.40 000 042 0026 0000 172.1 00.00 00004 01010110 00 00 00104 010..."
    
    print("Testing EASUN communication (MPP Solar compatible mode)")
    print("=" * 60)
    
    # Test with 2400 baud first (as it worked in your test)
    for baud in [2400, 9600, 4800]:
        print(f"\nTesting at {baud} baud...")
        
        try:
            ser = serial.Serial(
                port=port_name,
                baudrate=baud,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=3.0,  # Longer timeout
                write_timeout=1.0,
                inter_byte_timeout=0.1
            )
            
            # Ensure clean state
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            time.sleep(0.5)
            
            # Send QPIGS command
            command = "QPIGS"
            cmd_bytes = command.encode('ascii')
            crc = calculate_crc(cmd_bytes)
            crc_bytes = struct.pack('>H', crc)
            message = cmd_bytes + crc_bytes + b'\r'
            
            print(f"Sending: {message.hex()} ({command})")
            bytes_written = ser.write(message)
            ser.flush()
            print(f"Sent {bytes_written} bytes")
            
            # Read with multiple attempts
            response = b''
            attempts = 0
            max_attempts = 20
            
            while attempts < max_attempts:
                if ser.in_waiting > 0:
                    chunk = ser.read(ser.in_waiting)
                    response += chunk
                    print(f"Received chunk: {len(chunk)} bytes")
                    
                    # Check if response looks complete
                    if len(response) > 100 and b'\r' in response:
                        print("Complete response detected")
                        break
                
                attempts += 1
                time.sleep(0.1)
            
            ser.close()
            
            if response:
                print(f"\nResponse received: {len(response)} bytes")
                print(f"Hex: {response.hex()}")
                
                # Try to decode
                if len(response) > 3:
                    data = response[:-3].decode('ascii', errors='ignore')
                    print(f"Text: {data}")
                    
                    # Check if it's a valid QPIGS response
                    if data.startswith('(') and len(data) > 50:
                        print("\n✓ SUCCESS! Valid QPIGS response")
                        print(f"Recommended settings: {baud} baud")
                        return True
            else:
                print("No response")
                
        except Exception as e:
            print(f"Error: {e}")
            if 'ser' in locals():
                ser.close()
    
    return False

def main():
    if test_communication():
        print("\n✓ Communication established!")
        print("\nNext steps:")
        print("1. Update send_easun_data.sh with correct MQTT credentials")
        print("2. Test with: ./send_easun_data.sh")
    else:
        print("\n✗ Communication failed")
        print("\nPossible issues:")
        print("1. Check cable - needs proper RS232 crossover/null modem")
        print("2. Verify inverter is powered on")
        print("3. Check RJ45 pinout matches (Pin 1=TX, Pin 2=RX, Pin 7/8=GND)")

if __name__ == "__main__":
    main()