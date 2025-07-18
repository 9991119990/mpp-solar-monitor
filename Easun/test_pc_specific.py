#!/usr/bin/env python3
"""
Test EASUN on PC (not Raspberry Pi)
Some USB adapters behave differently on PC
"""

import serial
import time
import struct
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

def test_with_delays():
    """Test with various delays and settings"""
    port_name = '/dev/ttyUSB0'
    
    print("EASUN Test - PC specific settings")
    print("=" * 60)
    
    # Try different inter-character delays
    for delay in [0, 0.01, 0.05, 0.1]:
        print(f"\nTesting with {delay}s inter-character delay...")
        
        try:
            ser = serial.Serial(
                port=port_name,
                baudrate=2400,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=5.0,
                write_timeout=2.0,
                inter_byte_timeout=0.5,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            # Set break condition briefly (some inverters need this)
            ser.send_break(duration=0.25)
            time.sleep(0.5)
            
            # Clear buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Send QPIGS command with delays
            command = "QPIGS"
            cmd_bytes = command.encode('ascii')
            crc = calculate_crc(cmd_bytes)
            crc_bytes = struct.pack('>H', crc)
            message = cmd_bytes + crc_bytes + b'\r'
            
            print(f"Sending: {message.hex()}")
            
            # Send byte by byte with delay
            for byte in message:
                ser.write(bytes([byte]))
                ser.flush()
                if delay > 0:
                    time.sleep(delay)
            
            # Wait for response
            print("Waiting for response...")
            response = b''
            empty_reads = 0
            
            while empty_reads < 10:
                waiting = ser.in_waiting
                if waiting > 0:
                    chunk = ser.read(waiting)
                    response += chunk
                    print(f"Got {len(chunk)} bytes, total: {len(response)}")
                    empty_reads = 0
                    
                    # Check for end
                    if b'\r' in chunk and len(response) > 50:
                        break
                else:
                    empty_reads += 1
                    time.sleep(0.1)
            
            ser.close()
            
            if response and len(response) > 10:
                print(f"Response: {response.hex()}")
                try:
                    text = response[:-3].decode('ascii', errors='ignore')
                    print(f"Decoded: {text}")
                    if text.startswith('('):
                        print("\n✓ SUCCESS with delay={delay}s!")
                        return True
                except:
                    pass
                    
        except Exception as e:
            print(f"Error: {e}")
            if 'ser' in locals() and ser.is_open:
                ser.close()
    
    return False

def test_alternative_method():
    """Try alternative communication method"""
    print("\n\nTrying alternative method (like on Raspberry Pi)...")
    
    try:
        import subprocess
        
        # Configure port like on Raspberry
        subprocess.run(['stty', '-F', '/dev/ttyUSB0', '2400', 'cs8', '-cstopb', '-parenb', 'raw', '-echo'], check=True)
        time.sleep(0.5)
        
        # Send command using echo
        cmd = b'\x51\x50\x49\x47\x53\xB7\xA9\x0D'
        
        with open('/dev/ttyUSB0', 'wb') as port:
            port.write(cmd)
            port.flush()
        
        # Read response
        response = b''
        with open('/dev/ttyUSB0', 'rb') as port:
            start = time.time()
            while time.time() - start < 3:
                try:
                    chunk = port.read(1)
                    if chunk:
                        response += chunk
                        if len(response) > 100 and b'\r' in response:
                            break
                except:
                    time.sleep(0.01)
        
        if response:
            print(f"Got response: {len(response)} bytes")
            print(f"Hex: {response.hex()}")
            return True
            
    except Exception as e:
        print(f"Alternative method error: {e}")
    
    return False

def main():
    # First try normal method with delays
    if test_with_delays():
        print("\n✓ Communication working!")
    else:
        # Try alternative method
        if test_alternative_method():
            print("\n✓ Alternative method works!")
        else:
            print("\n✗ Communication failed")
            print("\nSince it worked on Raspberry Pi, try:")
            print("1. Different USB port")
            print("2. USB hub with external power")
            print("3. Shorter/better USB cable")
            print("4. Run on Raspberry Pi directly")

if __name__ == "__main__":
    main()