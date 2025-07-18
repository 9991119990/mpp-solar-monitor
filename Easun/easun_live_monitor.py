#!/usr/bin/env python3
"""
EASUN SHM II 7K - Live Monitor
Real-time display with 15s refresh interval
"""

import serial
import time
import re
import os
from datetime import datetime

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def parse_qpigs(response_text):
    """Parse QPIGS response"""
    match = re.search(r'\(([0-9\.\s]+)', response_text)
    if not match:
        return None
        
    values = match.group(1).strip().split()
    
    if len(values) >= 21:
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
                'inverter_temp': int(values[11]),
                'pv_current': int(values[12]),
                'pv_voltage': float(values[13]),
                'battery_scc_voltage': float(values[14]),
                'battery_discharge_current': int(values[15]),
                'device_status': values[16],
                'pv_charging_power': int(values[19]) if len(values) > 19 and values[19].isdigit() else 0,
            }
        except (ValueError, IndexError):
            return None
    return None

def get_status_indicators(data):
    """Get status indicators from device status bits"""
    if not data or 'device_status' not in data:
        return {}
    
    status = data['device_status']
    if len(status) >= 8:
        return {
            'load_on': status[3] == '1',
            'charging': status[5] == '1',
            'scc_charging': status[6] == '1',
            'ac_charging': status[7] == '1',
        }
    return {}

def format_power(watts):
    """Format power with appropriate units"""
    if watts >= 1000:
        return f"{watts/1000:.2f} kW"
    return f"{watts} W"

def get_battery_bar(percentage):
    """Create battery percentage bar"""
    bars = int(percentage / 5)  # 20 bars for 100%
    filled = "█" * bars
    empty = "░" * (20 - bars)
    return f"[{filled}{empty}] {percentage}%"

def get_pv_power_bar(power_watts, max_power=2700):
    """Create PV power percentage bar"""
    percentage = min(100, (power_watts / max_power) * 100)
    bars = int(percentage / 5)  # 20 bars for 100%
    filled = "█" * bars
    empty = "░" * (20 - bars)
    return f"[{filled}{empty}] {percentage:.1f}%"

def display_data(data, timestamp):
    """Display formatted data - simplified version"""
    clear_screen()
    
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                    EASUN SHM II 7K - Live Monitor            ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print(f"Last update: {timestamp}")
    print()
    
    if not data:
        print("❌ No data received from inverter")
        return
    
    # Get status indicators
    status = get_status_indicators(data)
    
    # Display main sections only
    print("☀️ PV SOLAR:")
    scc_indicator = "🟢" if status.get('scc_charging', False) else "🟡"
    real_pv_power = data['pv_charging_power'] if data['pv_charging_power'] > 0 else 0
    print(f"   {scc_indicator} {data['pv_voltage']:.1f}V @ {data['pv_current']}A")
    print(f"   Real Power: {format_power(real_pv_power)}")
    print(f"   {get_pv_power_bar(real_pv_power)}")
    
    if real_pv_power == 0 and data['pv_voltage'] > 200:
        print(f"   Status: Night mode (no generation)")
    print()
    
    print("🔋 BATTERY:")
    charging_indicator = "⚡" if status.get('charging', False) else "💤"
    print(f"   {charging_indicator} {data['battery_voltage']:.1f}V")
    print(f"   {get_battery_bar(data['battery_capacity'])}")
    
    if data['battery_charge_current'] > 0:
        print(f"   Charging: {data['battery_charge_current']}A")
    elif data['battery_discharge_current'] > 0:
        print(f"   Discharging: {data['battery_discharge_current']}A")
    else:
        print(f"   Standby")
    print()
    
    print("⚡ AC OUTPUT:")
    load_indicator = "🟢" if status.get('load_on', False) else "🔴"
    print(f"   {load_indicator} {data['ac_output_voltage']:.1f}V @ {data['ac_output_frequency']:.1f}Hz")
    print(f"   Power: {format_power(data['ac_output_active_power'])} ({data['output_load_percent']}% load)")
    print()
    
    print("🌡️ SYSTEM:")
    temp_status = "🔥" if data['inverter_temp'] > 60 else "🟢" if data['inverter_temp'] < 50 else "🟡"
    print(f"   Temperature: {temp_status} {data['inverter_temp']}°C")
    print()
    
    print("📊 STATUS:")
    print(f"   Solar Charging: {'🟢 YES' if status.get('scc_charging', False) else '🔴 NO'}")
    print(f"   Load: {'🟢 ON' if status.get('load_on', False) else '🔴 OFF'}")
    print()
    
    print("═" * 63)
    print("Press Ctrl+C to stop monitoring")

def read_easun_data():
    """Read data from EASUN inverter"""
    try:
        ser = serial.Serial('/dev/ttyUSB0', 2400, timeout=3)
        ser.dtr = True
        time.sleep(0.1)
        
        # Send QPIGS command
        cmd = bytes.fromhex('5150494753b7a90d')
        ser.write(cmd)
        time.sleep(0.3)
        
        response = ser.read(300)
        ser.close()
        
        if response:
            response_text = response.decode('utf-8', errors='ignore')
            return parse_qpigs(response_text)
        
        return None
        
    except Exception as e:
        print(f"Communication error: {e}")
        return None

def main():
    """Main monitoring loop"""
    print("Starting EASUN Live Monitor...")
    print("Refresh interval: 5 seconds")
    time.sleep(2)
    
    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = read_easun_data()
            display_data(data, timestamp)
            
            # Wait 5 seconds
            time.sleep(5)
            
    except KeyboardInterrupt:
        clear_screen()
        print("\n✅ Monitoring stopped by user")
        print("Thank you for using EASUN Live Monitor!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()