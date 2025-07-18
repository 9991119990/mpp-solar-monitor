#!/usr/bin/env python3
"""
EASUN SHM II 7K Data Reader
Reads and parses data from the inverter
"""

import serial
import time
import struct
import json
from datetime import datetime

class EasunReader:
    def __init__(self, port='/dev/ttyUSB0', baud=2400):
        self.port_name = port
        self.baud_rate = baud
        self.timeout = 2.0
        
    def calculate_crc(self, data):
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
    
    def send_command(self, port, command):
        """Send command and get response"""
        cmd_bytes = command.encode('ascii')
        crc = self.calculate_crc(cmd_bytes)
        crc_bytes = struct.pack('>H', crc)
        message = cmd_bytes + crc_bytes + b'\r'
        
        # Clear buffers
        port.reset_input_buffer()
        port.reset_output_buffer()
        
        # Send command
        port.write(message)
        port.flush()
        
        # Read response
        response = b''
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            if port.in_waiting > 0:
                chunk = port.read(port.in_waiting)
                response += chunk
                if b'\r' in chunk:
                    break
            time.sleep(0.05)
        
        return response
    
    def parse_qpigs(self, response):
        """Parse QPIGS response"""
        # Remove CR and CRC
        if len(response) < 3:
            print(f"Response too short: {len(response)} bytes")
            return None
            
        data = response[:-3].decode('ascii', errors='ignore')
        print(f"Raw data: {data}")
        
        # Remove parentheses if present
        if data.startswith('('):
            data = data[1:]
        if data.endswith(')'):
            data = data[:-1]
        
        # Split values
        values = data.split()
        
        # Parse according to PI30 QPIGS format
        if len(values) < 17:
            print(f"Warning: Got {len(values)} values, expected at least 17")
            return None
        
        result = {
            'grid_voltage': float(values[0]) if values[0] != 'NA' else 0.0,
            'grid_frequency': float(values[1]) if values[1] != 'NA' else 0.0,
            'ac_output_voltage': float(values[2]) if values[2] != 'NA' else 0.0,
            'ac_output_frequency': float(values[3]) if values[3] != 'NA' else 0.0,
            'ac_output_apparent_power': int(values[4]) if values[4] != 'NA' else 0,
            'ac_output_active_power': int(values[5]) if values[5] != 'NA' else 0,
            'output_load_percent': int(values[6]) if values[6] != 'NA' else 0,
            'bus_voltage': int(values[7]) if values[7] != 'NA' else 0,
            'battery_voltage': float(values[8].replace('!', '')) if values[8] != 'NA' else 0.0,
            'battery_charging_current': int(values[9]) if values[9] != 'NA' else 0,
            'battery_capacity': int(values[10]) if values[10] != 'NA' else 0,
            'inverter_temperature': int(values[11]) if values[11] != 'NA' else 0,
            'pv_input_current': float(values[12]) if values[12] != 'NA' else 0.0,
            'pv_input_voltage': float(values[13]) if values[13] != 'NA' else 0.0,
            'battery_voltage_scc': float(values[14]) if values[14] != 'NA' else 0.0,
            'battery_discharge_current': int(values[15]) if values[15] != 'NA' else 0,
            'device_status': values[16] if len(values) > 16 else ''
        }
        
        # Calculate PV power
        result['pv_input_power'] = result['pv_input_voltage'] * result['pv_input_current']
        
        # Parse device status if available
        if len(result['device_status']) >= 8:
            status = result['device_status']
            result['status'] = {
                'load_on': status[4] == '1' if len(status) > 4 else False,
                'charging': status[6] == '1' if len(status) > 6 else False,
                'scc_charging': status[6] == '1' if len(status) > 6 else False,
                'ac_charging': status[7] == '1' if len(status) > 7 else False
            }
        
        return result
    
    def read_data(self):
        """Read data from inverter"""
        try:
            port = serial.Serial(
                port=self.port_name,
                baudrate=self.baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            # Get QPIGS data
            response = self.send_command(port, 'QPIGS')
            port.close()
            
            print(f"Response length: {len(response)} bytes")
            print(f"Response hex: {response.hex()}")
            
            if response:
                data = self.parse_qpigs(response)
                if data:
                    data['timestamp'] = datetime.now().isoformat()
                    return data
            
        except Exception as e:
            print(f"Error reading data: {e}")
        
        return None

def main():
    reader = EasunReader()
    
    print("EASUN SHM II 7K Data Reader")
    print("=" * 60)
    
    # Read data
    data = reader.read_data()
    
    if data:
        print("\nInverter Data:")
        print("-" * 60)
        print(f"Grid Voltage: {data['grid_voltage']} V")
        print(f"Grid Frequency: {data['grid_frequency']} Hz")
        print(f"AC Output Voltage: {data['ac_output_voltage']} V")
        print(f"AC Output Power: {data['ac_output_active_power']} W")
        print(f"Output Load: {data['output_load_percent']} %")
        print(f"Battery Voltage: {data['battery_voltage']} V")
        print(f"Battery Capacity: {data['battery_capacity']} %")
        print(f"Battery Charging: {data['battery_charging_current']} A")
        print(f"PV Voltage: {data['pv_input_voltage']} V")
        print(f"PV Current: {data['pv_input_current']} A")
        print(f"PV Power: {data['pv_input_power']:.1f} W")
        print(f"Temperature: {data['inverter_temperature']} °C")
        
        # Save to JSON
        with open('easun_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("\nData saved to easun_data.json")
    else:
        print("Failed to read data from inverter")

if __name__ == "__main__":
    main()