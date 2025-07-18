#!/usr/bin/env python3
"""
Detailed EASUN QPIGS parser - all available parameters
"""

import serial
import time
import re

def parse_qpigs_detailed(response_text):
    """Parse ALL parameters from QPIGS response"""
    match = re.search(r'\(([0-9\.\s]+)', response_text)
    if not match:
        return None
        
    data_str = match.group(1).strip()
    values = data_str.split()
    
    print(f"Total values found: {len(values)}")
    print(f"Raw values: {values}")
    print()
    
    if len(values) >= 21:
        parameters = {
            # Basic AC/DC measurements
            'grid_voltage': float(values[0]),                    # V
            'grid_frequency': float(values[1]),                  # Hz
            'ac_output_voltage': float(values[2]),               # V
            'ac_output_frequency': float(values[3]),             # Hz
            'ac_output_apparent_power': int(values[4]),          # VA
            'ac_output_active_power': int(values[5]),            # W
            'output_load_percent': int(values[6]),               # %
            
            # DC measurements
            'bus_voltage': int(values[7]),                       # V
            'battery_voltage': float(values[8]),                 # V
            'battery_charge_current': int(values[9]),            # A
            'battery_capacity': int(values[10]),                 # %
            
            # Temperature and PV
            'inverter_heat_sink_temp': int(values[11]),          # °C
            'pv_input_current': int(values[12]),                 # A
            'pv_input_voltage': float(values[13]),               # V
            'battery_voltage_scc': float(values[14]),            # V (Solar Charge Controller)
            'battery_discharge_current': int(values[15]),        # A
            
            # Status and additional data
            'device_status': values[16],                         # Binary status flags
            'battery_voltage_offset_fan': values[17],            # Fan control
            'eeprom_version': values[18],                        # EEPROM version
            'pv_charging_power': int(values[19]) if values[19].isdigit() else 0,  # W
            'device_status2': values[20] if len(values) > 20 else '',  # Additional status
        }
        
        # Parse device status bits (value[16])
        if len(values[16]) >= 8:
            status_bits = values[16]
            status_flags = {
                'add_sbu_priority_version': status_bits[0] == '1',
                'configuration_status': status_bits[1] == '1', 
                'scc_firmware_version': status_bits[2] == '1',
                'load_status': status_bits[3] == '1',
                'battery_voltage_steady': status_bits[4] == '1',
                'charging_status': status_bits[5] == '1',
                'scc_charging_status': status_bits[6] == '1',
                'ac_charging_status': status_bits[7] == '1',
            }
            parameters['status_flags'] = status_flags
        
        return parameters
    
    return None

def main():
    print("EASUN SHM II 7K - Detailed Parameter Analysis")
    print("=" * 60)
    
    try:
        ser = serial.Serial('/dev/ttyUSB0', 2400, timeout=3)
        ser.dtr = True
        time.sleep(0.2)
        
        # Send QPIGS command
        cmd = bytes.fromhex('5150494753b7a90d')
        ser.write(cmd)
        time.sleep(0.3)
        response = ser.read(300)
        
        if response:
            response_text = response.decode('utf-8', errors='ignore')
            print(f"Raw response: {response_text}")
            print()
            
            # Parse all parameters
            data = parse_qpigs_detailed(response_text)
            
            if data:
                print("DETAILED PARAMETER BREAKDOWN:")
                print("=" * 60)
                
                print("🔌 AC GRID INPUT:")
                print(f"  Voltage: {data['grid_voltage']} V")
                print(f"  Frequency: {data['grid_frequency']} Hz")
                print()
                
                print("⚡ AC OUTPUT:")
                print(f"  Voltage: {data['ac_output_voltage']} V")
                print(f"  Frequency: {data['ac_output_frequency']} Hz")
                print(f"  Apparent Power: {data['ac_output_apparent_power']} VA")
                print(f"  Active Power: {data['ac_output_active_power']} W")
                print(f"  Load Percentage: {data['output_load_percent']} %")
                print()
                
                print("🔋 BATTERY:")
                print(f"  Voltage: {data['battery_voltage']} V")
                print(f"  Capacity: {data['battery_capacity']} %")
                print(f"  Charge Current: {data['battery_charge_current']} A")
                print(f"  Discharge Current: {data['battery_discharge_current']} A")
                print(f"  SCC Voltage: {data['battery_voltage_scc']} V")
                print()
                
                print("☀️ PV SOLAR:")
                print(f"  Voltage: {data['pv_input_voltage']} V")
                print(f"  Current: {data['pv_input_current']} A")
                print(f"  Charging Power: {data['pv_charging_power']} W")
                print()
                
                print("🌡️ SYSTEM:")
                print(f"  Temperature: {data['inverter_heat_sink_temp']} °C")
                print(f"  Bus Voltage: {data['bus_voltage']} V")
                print(f"  EEPROM Version: {data['eeprom_version']}")
                print()
                
                print("📊 STATUS FLAGS:")
                if 'status_flags' in data:
                    for flag, status in data['status_flags'].items():
                        print(f"  {flag}: {'✅' if status else '❌'}")
                else:
                    print(f"  Raw status: {data['device_status']}")
                print()
                
                print("🔧 ADDITIONAL:")
                print(f"  Fan Control: {data['battery_voltage_offset_fan']}")
                print(f"  Device Status 2: {data['device_status2']}")
                
                # Calculate derived values
                power_factor = data['ac_output_active_power'] / data['ac_output_apparent_power'] if data['ac_output_apparent_power'] > 0 else 0
                pv_power = data['pv_input_voltage'] * data['pv_input_current']
                
                print()
                print("📈 CALCULATED VALUES:")
                print(f"  Power Factor: {power_factor:.3f}")
                print(f"  PV Power (V×I): {pv_power:.1f} W")
                print(f"  Battery Power: {data['battery_voltage'] * (data['battery_discharge_current'] - data['battery_charge_current']):.1f} W")
                
        else:
            print("No response received")
            
        ser.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()