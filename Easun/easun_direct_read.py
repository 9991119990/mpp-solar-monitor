#!/usr/bin/env python3
"""
Direct EASUN reader using low-level file operations
Similar to how it works on Raspberry Pi
"""

import os
import time
import struct
import termios
import tty

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

def setup_serial_port(port_path):
    """Setup serial port with termios"""
    # Open port
    fd = os.open(port_path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    
    # Get current settings
    old_attrs = termios.tcgetattr(fd)
    
    # Configure for 2400 8N1
    attrs = termios.tcgetattr(fd)
    
    # Set baud rate
    attrs[4] = attrs[5] = termios.B2400
    
    # 8N1
    attrs[2] = attrs[2] & ~termios.CSIZE
    attrs[2] = attrs[2] | termios.CS8
    attrs[2] = attrs[2] & ~termios.PARENB
    attrs[2] = attrs[2] & ~termios.CSTOPB
    
    # Raw mode
    attrs[3] = attrs[3] & ~(termios.ECHO | termios.ECHONL | termios.ICANON | termios.ISIG | termios.IEXTEN)
    attrs[0] = attrs[0] & ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK | termios.ISTRIP | termios.INLCR | termios.IGNCR | termios.ICRNL | termios.IXON)
    attrs[1] = attrs[1] & ~termios.OPOST
    
    # Apply settings
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    termios.tcflush(fd, termios.TCIFLUSH)
    
    return fd, old_attrs

def read_easun_data():
    """Read data from EASUN using direct file operations"""
    port_path = '/dev/ttyUSB0'
    
    print("EASUN Direct Reader")
    print("=" * 60)
    
    try:
        # Setup port
        fd, old_attrs = setup_serial_port(port_path)
        
        # Prepare QPIGS command
        command = "QPIGS"
        cmd_bytes = command.encode('ascii')
        crc = calculate_crc(cmd_bytes)
        crc_bytes = struct.pack('>H', crc)
        message = cmd_bytes + crc_bytes + b'\r'
        
        print(f"Sending command: {command}")
        print(f"Message hex: {message.hex()}")
        
        # Clear any pending data
        try:
            while True:
                os.read(fd, 1000)
        except:
            pass
        
        # Send command
        os.write(fd, message)
        
        # Read response
        response = b''
        start_time = time.time()
        consecutive_timeouts = 0
        
        print("Reading response...")
        
        while time.time() - start_time < 5.0:
            try:
                # Set to blocking mode for read
                flags = os.fcntl.fcntl(fd, os.fcntl.F_GETFL)
                os.fcntl.fcntl(fd, os.fcntl.F_SETFL, flags & ~os.O_NONBLOCK)
                
                # Read with timeout
                chunk = os.read(fd, 256)
                if chunk:
                    response += chunk
                    consecutive_timeouts = 0
                    print(f"Received {len(chunk)} bytes, total: {len(response)}")
                    
                    # Check if we have a complete response
                    if b'\r' in response and len(response) > 50:
                        print("Complete response received!")
                        break
                        
                # Set back to non-blocking
                os.fcntl.fcntl(fd, os.fcntl.F_SETFL, flags | os.O_NONBLOCK)
                
            except BlockingIOError:
                consecutive_timeouts += 1
                if consecutive_timeouts > 20:
                    break
                time.sleep(0.05)
            except Exception as e:
                print(f"Read error: {e}")
                break
        
        # Restore settings and close
        termios.tcsetattr(fd, termios.TCSADRAIN, old_attrs)
        os.close(fd)
        
        if response:
            print(f"\nTotal response: {len(response)} bytes")
            print(f"Response hex: {response.hex()}")
            
            # Try to decode
            if len(response) > 3:
                try:
                    # Remove CR and CRC
                    data = response[:-3].decode('ascii', errors='ignore')
                    print(f"Decoded text: {data}")
                    
                    # Parse if valid
                    if data.startswith('(') and len(data) > 50:
                        print("\n✓ Valid QPIGS response!")
                        parse_qpigs(data)
                        return True
                except Exception as e:
                    print(f"Decode error: {e}")
        else:
            print("No response received")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return False

def parse_qpigs(data):
    """Parse and display QPIGS data"""
    # Remove parentheses
    if data.startswith('('):
        data = data[1:]
    if data.endswith(')'):
        data = data[:-1]
    
    values = data.split()
    
    if len(values) >= 17:
        print("\nParsed Data:")
        print("-" * 40)
        print(f"Grid Voltage: {values[0]} V")
        print(f"AC Output: {values[2]} V, {values[5]} W")
        print(f"Battery: {values[8].replace('!', '')} V, {values[10]}%")
        print(f"PV: {values[13]} V, {float(values[13]) * float(values[12]):.1f} W")
        print(f"Temperature: {values[11]} °C")

def main():
    if read_easun_data():
        print("\n✓ Successfully read EASUN data!")
        print("\nNext steps:")
        print("1. Update MQTT credentials in send_easun_data.sh")
        print("2. Test with: ./send_easun_data.sh")
    else:
        print("\n✗ Failed to read data")
        print("\nSince it worked on Raspberry Pi, consider:")
        print("1. Using a powered USB hub")
        print("2. Testing with shorter USB cable")
        print("3. Running directly on Raspberry Pi")

if __name__ == "__main__":
    main()