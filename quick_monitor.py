#!/usr/bin/env python3
"""
Rychly kontinualni monitor pro MPP Solar - zobrazuje jen klicove hodnoty
"""

import subprocess
import json
import os
import time
from datetime import datetime

# Pridame mpp-solar do PATH
os.environ['PATH'] = f"{os.environ.get('PATH', '')}:/home/dell/.local/bin"

def get_quick_data():
    """Ziska rychle jen zakladni data"""
    try:
        cmd = ['mpp-solar', '-p', '/dev/hidraw2', '-c', 'QPIGS', '-o', 'json']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {k: v for k, v in data.items() if not k.startswith('_')}
        return None
    except Exception:
        return None

def print_quick_status(data):
    """Zobrazi rychly prehled"""
    if not data:
        print("❌ Chyba cteni dat")
        return
    
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    # PV panel
    pv_v = data.get('pv_input_voltage', 0)
    pv_i = data.get('pv_input_current_for_battery', 0)
    pv_p = pv_v * pv_i
    
    # Baterie
    bat_v = data.get('battery_voltage', 0)
    bat_cap = data.get('battery_capacity', 0)
    bat_charge = data.get('battery_charging_current', 0)
    bat_discharge = data.get('battery_discharge_current', 0)
    
    # AC vystup
    ac_v = data.get('ac_output_voltage', 0)
    ac_p = data.get('ac_output_active_power', 0)
    ac_load = data.get('ac_output_load', 0)
    
    # Teplota
    temp = data.get('inverter_heat_sink_temperature', 0)
    
    # Stavy
    scc_charging = "🔋" if data.get('is_scc_charging_on', 0) else "⭕"
    load_on = "⚡" if data.get('is_load_on', 0) else "⭕"
    
    print(f"\r{timestamp} │ PV: {pv_v:5.1f}V {pv_i:4.1f}A {pv_p:5.0f}W │ BAT: {bat_v:4.1f}V {bat_cap:2d}% {bat_charge:2d}A │ AC: {ac_v:5.1f}V {ac_p:3d}W {ac_load:2d}% │ {temp:2d}°C │ {scc_charging}{load_on}", end="")

def main():
    print("MPP SOLAR - RYCHLY MONITOR")
    print("=" * 70)
    print("Cas      │ PV Panel (V/A/W)    │ Baterie (V/%/A)  │ AC Vystup (V/W/%) │ T  │St")
    print("-" * 70)
    
    try:
        while True:
            data = get_quick_data()
            print_quick_status(data)
            time.sleep(2)  # Refresh kazdych 2 sekundy
            
    except KeyboardInterrupt:
        print("\n\nMonitor ukoncen")

if __name__ == "__main__":
    main()