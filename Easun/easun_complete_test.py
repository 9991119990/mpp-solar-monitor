#!/usr/bin/env python3
"""
Complete EASUN SHM II 7K Test - All available commands and data
"""

import serial
import time
import struct
import re

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

def send_command(ser, command_str):
    """Send command and get response"""
    try:
        cmd_bytes = bytes.fromhex(command_str)
        ser.write(cmd_bytes)
        time.sleep(0.3)  # Wait for response
        response = ser.read(500)  # Read more bytes for longer responses
        return response
    except Exception as e:
        return f"Error: {e}".encode()

def parse_qpigs_response(response_text):
    """Parse QPIGS response into readable format"""
    # Extract data between ( and first non-printable character
    match = re.search(r'\(([0-9\.\s]+)', response_text)
    if not match:
        return None
        
    data_str = match.group(1).strip()
    values = data_str.split()
    
    if len(values) < 20:
        return None
        
    try:
        return {
            'grid_voltage': float(values[0]),
            'grid_frequency': float(values[1]), 
            'ac_output_voltage': float(values[2]),
            'ac_output_frequency': float(values[3]),
            'ac_output_apparent_power': int(values[4]),
            'ac_output_active_power': int(values[5]),
            'output_load_percent': int(values[6]),
            'bus_voltage': int(values[7]),
            'battery_voltage': float(values[8]),
            'battery_charge_current': int(values[9]),
            'battery_capacity': int(values[10]),
            'inverter_heat_sink_temp': int(values[11]),
            'pv_input_current': int(values[12]),
            'pv_input_voltage': float(values[13]),
            'battery_voltage_scc': float(values[14]),
            'battery_discharge_current': int(values[15]),
            'device_status': values[16] if len(values) > 16 else '',
            'battery_voltage_offset_fan': values[17] if len(values) > 17 else '',
            'eeprom_version': values[18] if len(values) > 18 else '',
            'pv_charging_power': values[19] if len(values) > 19 else '',
            'device_status2': values[20] if len(values) > 20 else ''
        }
    except (ValueError, IndexError):
        return None

def main():
    """Test all EASUN commands"""
    print("EASUN SHM II 7K - Complete Command Test")
    print("=" * 60)
    
    # PI30 Protocol Commands
    commands = {
        'QPI': '515049beac0d',          # Protocol ID inquiry
        'QPIGS': '5150494753b7a90d',    # General status parameters inquiry
        'QID': '514944c90d',            # Device serial number inquiry
        'QVFW': '51564657c1d40d',       # Main CPU firmware version inquiry
        'QVFW2': '5156465732c3f50d',    # Secondary CPU firmware version
        'QMOD': '514d4f4449c10d',       # Device mode inquiry
        'QPIWS': '5150495753b4da0d',    # Device warning status inquiry
        'QFLAG': '51464c414724b60d',    # Device flag status inquiry
        'QPGSn': '5150475330c2f20d',    # Parallel information inquiry (n=0)
        'QPGS0': '5150475330c2f20d',    # Parallel information inquiry for ID 0
        'QMCHGCR': '514d43484743521bf60d', # Max charging current inquiry
        'QMUCHGCR': '514d554348474352a6870d', # Max utility charging current
        'QBOOT': '51424f4f5431350d',    # DSP has bootstrap inquiry
        'QOPM': '514f504d71e30d',       # Output mode inquiry
        'QDI': '51444924b00d',          # Default setting value information
        'QMNU': '514d4e5571dd0d',       # Manufacturer name inquiry
        'QGMN': '51474d4e1e7d0d',       # General model name inquiry
        'QMN': '514d4e71e30d',          # Model name inquiry
        'QWS': '515753b4b00d',          # Warning status inquiry
        'QCHGS': '514348475347f00d',    # Charging source priority inquiry
        'QPIRI': '5150495249e9ad0d',    # Device rating information inquiry
        'QPIGS2': '515049475332c5b80d',  # General status parameters 2
        'QPGS1': '5150475331c3e30d',    # Parallel information inquiry for ID 1
        'QPGS2': '5150475332c4d20d',    # Parallel information inquiry for ID 2
        'QT': '515447910d',             # Time inquiry
        'QET': '51455441190d',          # Total generated energy inquiry
        'QLT': '514c5434b90d',          # Load total consumed energy inquiry
        'QYM': '51594d7a0d',            # Year and month inquiry
        'QMM': '514d4d71e30d',          # Month inquiry
        'QED': '514544c60d',            # Energy of day inquiry
        'QEM': '51454d1b0d',            # Energy of month inquiry
        'QEY': '5145592f0d',            # Energy of year inquiry
        'QLEDn': '514c454430c5e40d',    # Energy of day for parallel machine (n=0)
        'QLEMn': '514c454d30a7970d',    # Energy of month for parallel machine (n=0)
        'QLEYn': '514c454530c6d50d',    # Energy of year for parallel machine (n=0)
    }
    
    try:
        # Open serial connection
        ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=2400,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=3.0,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )
        
        ser.dtr = True
        time.sleep(0.2)
        
        print(f"Port {ser.port} opened successfully")
        print(f"Settings: {ser.baudrate} baud, 8N1")
        print()
        
        # Test all commands
        for cmd_name, cmd_hex in commands.items():
            print(f"Testing {cmd_name} - {get_command_description(cmd_name)}")
            print(f"Sending: {cmd_hex}")
            
            response = send_command(ser, cmd_hex)
            
            if response:
                response_hex = response.hex()
                response_text = response.decode('utf-8', errors='ignore')
                
                print(f"Response (hex): {response_hex}")
                print(f"Response (text): {response_text}")
                
                # Special parsing for QPIGS
                if cmd_name == 'QPIGS':
                    parsed = parse_qpigs_response(response_text)
                    if parsed:
                        print("Parsed QPIGS data:")
                        for key, value in parsed.items():
                            print(f"  {key}: {value}")
                
                print("-" * 60)
            else:
                print("No response received")
                print("-" * 60)
            
            time.sleep(0.5)  # Small delay between commands
        
        ser.close()
        
    except Exception as e:
        print(f"Error: {e}")

def get_command_description(cmd):
    """Get human-readable description of command"""
    descriptions = {
        'QPI': 'Protocol ID inquiry',
        'QPIGS': 'General status parameters inquiry',
        'QID': 'Device serial number inquiry',
        'QVFW': 'Main CPU firmware version inquiry',
        'QVFW2': 'Secondary CPU firmware version',
        'QMOD': 'Device mode inquiry',
        'QPIWS': 'Device warning status inquiry',
        'QFLAG': 'Device flag status inquiry',
        'QPGSn': 'Parallel information inquiry',
        'QPGS0': 'Parallel information inquiry for ID 0',
        'QMCHGCR': 'Max charging current inquiry',
        'QMUCHGCR': 'Max utility charging current',
        'QBOOT': 'DSP has bootstrap inquiry',
        'QOPM': 'Output mode inquiry',
        'QDI': 'Default setting value information',
        'QMNU': 'Manufacturer name inquiry',
        'QGMN': 'General model name inquiry',
        'QMN': 'Model name inquiry',
        'QWS': 'Warning status inquiry',
        'QCHGS': 'Charging source priority inquiry',
        'QPIRI': 'Device rating information inquiry',
        'QPIGS2': 'General status parameters 2',
        'QPGS1': 'Parallel information inquiry for ID 1',
        'QPGS2': 'Parallel information inquiry for ID 2',
        'QT': 'Time inquiry',
        'QET': 'Total generated energy inquiry',
        'QLT': 'Load total consumed energy inquiry',
        'QYM': 'Year and month inquiry',
        'QMM': 'Month inquiry',
        'QED': 'Energy of day inquiry',
        'QEM': 'Energy of month inquiry',
        'QEY': 'Energy of year inquiry',
        'QLEDn': 'Energy of day for parallel machine',
        'QLEMn': 'Energy of month for parallel machine',
        'QLEYn': 'Energy of year for parallel machine',
    }
    return descriptions.get(cmd, 'Unknown command')

if __name__ == "__main__":
    main()