#!/usr/bin/env python3
"""
Quick EASUN test - main commands only
"""

import serial
import time
import re

def send_command(ser, command_str, cmd_name):
    """Send command and get response"""
    try:
        cmd_bytes = bytes.fromhex(command_str)
        ser.write(cmd_bytes)
        time.sleep(0.3)
        response = ser.read(300)
        
        if response:
            response_text = response.decode('utf-8', errors='ignore')
            print(f"{cmd_name}:")
            print(f"  Raw: {response_text}")
            
            # Parse specific responses
            if cmd_name == 'QPIGS':
                parse_qpigs(response_text)
            elif cmd_name == 'QPIRI':
                parse_qpiri(response_text)
            
            print()
        else:
            print(f"{cmd_name}: No response")
            print()
            
    except Exception as e:
        print(f"{cmd_name}: Error - {e}")
        print()

def parse_qpigs(response_text):
    """Parse QPIGS response"""
    match = re.search(r'\(([0-9\.\s]+)', response_text)
    if match:
        values = match.group(1).strip().split()
        if len(values) >= 15:
            print(f"  Grid: {values[0]}V, {values[1]}Hz")
            print(f"  AC Output: {values[2]}V, {values[3]}Hz, {values[5]}W, {values[6]}%")
            print(f"  Battery: {values[8]}V, {values[10]}%, Charge: {values[9]}A")
            print(f"  PV: {values[13]}V, {values[12]}A")
            print(f"  Temperature: {values[11]}°C")
            print(f"  Bus Voltage: {values[7]}V")

def parse_qpiri(response_text):
    """Parse QPIRI response"""
    match = re.search(r'\(([0-9\.\s]+)', response_text)
    if match:
        values = match.group(1).strip().split()
        if len(values) >= 10:
            print(f"  Rated Power: {values[8]}VA")
            print(f"  Rated Voltage: {values[0]}V")
            print(f"  Rated Current: {values[1]}A")
            print(f"  Battery Voltage: {values[2]}V")

def main():
    print("EASUN SHM II 7K - Quick Test")
    print("=" * 40)
    
    # Main commands only
    commands = {
        'QPI': '515049beac0d',          # Protocol ID
        'QPIGS': '5150494753b7a90d',    # Status data
        'QPIRI': '5150495249e9ad0d',    # Rating information
        'QID': '514944c90d',            # Serial number
        'QVFW': '51564657c1d40d',       # Firmware version
        'QMOD': '514d4f4449c10d',       # Device mode
        'QPIWS': '5150495753b4da0d',    # Warning status
        'QET': '51455441190d',          # Total energy
        'QED': '514544c60d',            # Energy today
    }
    
    try:
        ser = serial.Serial('/dev/ttyUSB0', 2400, timeout=3)
        ser.dtr = True
        time.sleep(0.2)
        
        for cmd_name, cmd_hex in commands.items():
            send_command(ser, cmd_hex, cmd_name)
            
        ser.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()