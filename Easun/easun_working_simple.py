#!/usr/bin/env python3
"""
Simple working EASUN reader - verified working with new cable
"""

import serial
import time
import re

def read_easun_data():
    """Read data from EASUN inverter"""
    try:
        ser = serial.Serial('/dev/ttyUSB0', 2400, timeout=3)
        ser.dtr = True
        time.sleep(0.1)
        
        # Send QPIGS command
        cmd = bytes.fromhex('5150494753b7a90d')
        ser.write(cmd)
        
        # Read response
        response = ser.read(200)
        ser.close()
        
        # Clean response - remove garbage at end
        text = response.decode('utf-8', errors='ignore')
        
        # Extract data between ( and first non-printable character
        match = re.search(r'\(([0-9\.\s]+)', text)
        if match:
            data_str = match.group(1).strip()
            values = data_str.split()
            
            if len(values) >= 20:
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
                    'battery_discharge_current': int(values[15])
                }
        
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("EASUN SHM II 7K Monitor - Simple Version")
    print("=" * 40)
    
    while True:
        data = read_easun_data()
        if data:
            print(f"PV: {data['pv_input_voltage']}V, {data['pv_input_current']}A")
            print(f"Battery: {data['battery_voltage']}V, {data['battery_capacity']}%")
            print(f"AC Output: {data['ac_output_active_power']}W, {data['output_load_percent']}%")
            print(f"Temperature: {data['inverter_heat_sink_temp']}°C")
            print("-" * 40)
        else:
            print("No data received")
        
        time.sleep(5)