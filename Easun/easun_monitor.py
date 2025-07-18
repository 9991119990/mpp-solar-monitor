#!/usr/bin/env python3
"""
EASUN SHM II 7K Monitor
Simplified monitoring script
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

def read_inverter_data():
    """Read data from EASUN inverter"""
    port_name = '/dev/ttyUSB0'
    baud_rate = 2400
    
    try:
        # Open serial port
        ser = serial.Serial(
            port=port_name,
            baudrate=baud_rate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1,  # Small timeout for non-blocking reads
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )
        
        # Clear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.1)
        
        # Prepare QPIGS command
        command = "QPIGS"
        cmd_bytes = command.encode('ascii')
        crc = calculate_crc(cmd_bytes)
        crc_bytes = struct.pack('>H', crc)
        message = cmd_bytes + crc_bytes + b'\r'
        
        print(f"Sending command: {command}")
        print(f"Message hex: {message.hex()}")
        
        # Send command
        ser.write(message)
        ser.flush()
        
        # Wait for response (up to 3 seconds)
        response = b''
        start_time = time.time()
        
        while time.time() - start_time < 3.0:
            # Check for data
            waiting = ser.in_waiting
            if waiting > 0:
                chunk = ser.read(waiting)
                response += chunk
                print(f"Received {len(chunk)} bytes, total: {len(response)}")
                
                # Check if we have a complete response (ends with \r)
                if b'\r' in response:
                    print("Complete response received")
                    break
            else:
                time.sleep(0.05)
        
        ser.close()
        
        if response:
            print(f"\nTotal response: {len(response)} bytes")
            print(f"Response hex: {response.hex()}")
            
            # Try to decode
            if len(response) > 3:
                # Remove CR and CRC
                data = response[:-3]
                try:
                    text = data.decode('ascii', errors='ignore')
                    print(f"Response text: {text}")
                    
                    # Parse if it looks valid
                    if text.startswith('('):
                        return parse_response(text)
                except Exception as e:
                    print(f"Decode error: {e}")
        else:
            print("No response received")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def parse_response(text):
    """Parse QPIGS response"""
    # Remove parentheses
    if text.startswith('('):
        text = text[1:]
    if text.endswith(')'):
        text = text[:-1]
    
    # Split values
    values = text.split()
    print(f"\nParsed {len(values)} values")
    
    if len(values) >= 17:
        data = {
            'grid_voltage': float(values[0]),
            'grid_frequency': float(values[1]),
            'ac_output_voltage': float(values[2]),
            'ac_output_frequency': float(values[3]),
            'ac_output_power': int(values[5]),
            'load_percent': int(values[6]),
            'battery_voltage': float(values[8].replace('!', '')),
            'battery_capacity': int(values[10]),
            'temperature': int(values[11]),
            'pv_voltage': float(values[13]),
            'pv_current': float(values[12]),
            'pv_power': float(values[13]) * float(values[12])
        }
        return data
    
    return None

def main():
    print("EASUN SHM II 7K Monitor")
    print("=" * 60)
    
    data = read_inverter_data()
    
    if data:
        print("\n✓ Inverter Data:")
        print("-" * 40)
        print(f"Grid: {data['grid_voltage']}V @ {data['grid_frequency']}Hz")
        print(f"Output: {data['ac_output_voltage']}V, {data['ac_output_power']}W ({data['load_percent']}%)")
        print(f"Battery: {data['battery_voltage']}V ({data['battery_capacity']}%)")
        print(f"PV: {data['pv_voltage']}V, {data['pv_power']:.1f}W")
        print(f"Temperature: {data['temperature']}°C")
    else:
        print("\n✗ Failed to read inverter data")

if __name__ == "__main__":
    main()