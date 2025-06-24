#!/usr/bin/env python3
"""
Jednoduchy skript pro zobrazeni vsech aktualnich dat z MPP Solar menice
"""

import subprocess
import json
import os
from datetime import datetime

# Pridame mpp-solar do PATH
os.environ['PATH'] = f"{os.environ.get('PATH', '')}:/home/dell/.local/bin"

def get_mpp_data(command):
    """Ziska data z MPP Solar"""
    try:
        cmd = ['mpp-solar', '-p', '/dev/hidraw2', '-c', command, '-o', 'json']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            # Odstraníme metadata (_command, _command_description)
            clean_data = {k: v for k, v in data.items() if not k.startswith('_')}
            return clean_data
        else:
            print(f"Chyba príkazu {command}: {result.stderr}")
            return None
    except Exception as e:
        print(f"Chyba: {e}")
        return None

def show_all_current_data():
    """Zobrazi vsechny aktualni data"""
    
    print("="*80)
    print(f"{'MPP SOLAR PIP5048MG - AKTUALNI DATA':^80}")
    print(f"{'Cas: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^80}")
    print("="*80)
    
    # 1. ZAKLADNI INFORMACE
    print("\n🔧 ZAKLADNI INFORMACE:")
    print("-" * 50)
    
    protocol = get_mpp_data('QPI')
    if protocol:
        print(f"Protocol ID:     {protocol.get('protocol_id', 'N/A')}")
    
    device_id = get_mpp_data('QID') 
    if device_id:
        print(f"Device ID:       {device_id.get('device_id', 'N/A')}")
    
    firmware = get_mpp_data('QVFW')
    if firmware:
        print(f"Firmware:        {firmware.get('firmware_version', 'N/A')}")
    
    mode = get_mpp_data('QMOD')
    if mode:
        print(f"Rezim:           {mode.get('device_mode', 'N/A')}")
    
    # 2. HLAVNI STATUS - QPIGS
    print("\n⚡ HLAVNI STATUS (QPIGS):")
    print("-" * 50)
    
    status = get_mpp_data('QPIGS')
    if status:
        # AC vstup (sit)
        print(f"AC Vstup:")
        print(f"  Napeti:        {status.get('ac_input_voltage', 0):>8.1f} V")
        print(f"  Frekvence:     {status.get('ac_input_frequency', 0):>8.1f} Hz")
        
        # AC vystup
        print(f"\nAC Vystup:")
        print(f"  Napeti:        {status.get('ac_output_voltage', 0):>8.1f} V")
        print(f"  Frekvence:     {status.get('ac_output_frequency', 0):>8.1f} Hz")
        print(f"  Vykon:         {status.get('ac_output_active_power', 0):>8d} W")
        print(f"  Zdanlivy:      {status.get('ac_output_apparent_power', 0):>8d} VA")
        print(f"  Zatizeni:      {status.get('ac_output_load', 0):>8d} %")
        
        # Baterie
        print(f"\nBaterie:")
        print(f"  Napeti:        {status.get('battery_voltage', 0):>8.1f} V")
        print(f"  Nabijeni:      {status.get('battery_charging_current', 0):>8d} A")
        print(f"  Vybijeni:      {status.get('battery_discharge_current', 0):>8d} A")
        print(f"  Kapacita:      {status.get('battery_capacity', 0):>8d} %")
        print(f"  SCC napeti:    {status.get('battery_voltage_from_scc', 0):>8.1f} V")
        
        # Solární panely
        pv_voltage = status.get('pv_input_voltage', 0)
        pv_current = status.get('pv_input_current_for_battery', 0)
        pv_power_calc = pv_voltage * pv_current
        
        print(f"\nSolarni panely:")
        print(f"  Napeti:        {pv_voltage:>8.1f} V")
        print(f"  Proud:         {pv_current:>8.1f} A")
        print(f"  Vykon (calc):  {pv_power_calc:>8.1f} W")
        print(f"  Vykon (HW):    {status.get('pv_input_power', 0):>8d} W")
        
        # System
        print(f"\nSystem:")
        print(f"  Teplota:       {status.get('inverter_heat_sink_temperature', 0):>8d} °C")
        print(f"  Bus napeti:    {status.get('bus_voltage', 0):>8d} V")
        
        # Statusove indikatory
        print(f"\nStavy (1=ano, 0=ne):")
        statuses = {
            'Zatizeni zapnuto': 'is_load_on',
            'SBU priorita': 'is_sbu_priority_version_added',
            'Konfigurace zmenena': 'is_configuration_changed',
            'SCC FW aktualizovan': 'is_scc_firmware_updated',
            'Bat. napeti stabilni': 'is_battery_voltage_to_steady_while_charging',
            'Nabijeni aktivni': 'is_charging_on',
            'SCC nabijeni': 'is_scc_charging_on',
            'AC nabijeni': 'is_ac_charging_on',
            'Float nabijeni': 'is_charging_to_float',
            'Zapnuto': 'is_switched_on'
        }
        
        for name, key in statuses.items():
            value = status.get(key, 0)
            icon = "✓" if value else "✗"
            print(f"  {icon} {name:<20} ({value})")
    
    # 3. NASTAVENI - QPIRI
    print("\n⚙️  NASTAVENI MENICE (QPIRI):")
    print("-" * 50)
    
    settings = get_mpp_data('QPIRI')
    if settings:
        print(f"AC vystup:")
        print(f"  Jmenovite napeti:  {settings.get('ac_output_voltage', 'N/A')} V")
        print(f"  Jmenovita frekvence: {settings.get('ac_output_frequency', 'N/A')} Hz")
        print(f"  Jmenovity vykon:   {settings.get('ac_output_apparent_power', 'N/A')} VA")
        print(f"  Jmenovity vykon:   {settings.get('ac_output_active_power', 'N/A')} W")
        
        print(f"\nBaterie:")
        print(f"  Jmenovite napeti:  {settings.get('battery_voltage', 'N/A')} V")
        print(f"  Float napeti:      {settings.get('battery_float_voltage', 'N/A')} V")
        print(f"  Bulk napeti:       {settings.get('battery_bulk_voltage', 'N/A')} V")
        print(f"  Nizke napeti:      {settings.get('battery_low_voltage', 'N/A')} V")
        print(f"  Cutoff napeti:     {settings.get('battery_under_voltage', 'N/A')} V")
        print(f"  Max. nab. proud:   {settings.get('max_charging_current', 'N/A')} A")
        print(f"  Max. AC nab.:      {settings.get('max_ac_charging_current', 'N/A')} A")
        
        print(f"\nAC vstup:")
        print(f"  Rozsah napeti:     {settings.get('ac_input_voltage_range', 'N/A')}")
        print(f"  Output zdroj:      {settings.get('output_source_priority', 'N/A')}")
        print(f"  Charger priority:  {settings.get('charger_source_priority', 'N/A')}")
    
    # 4. VAROVANI - QPIWS
    print("\n⚠️  VAROVANI A CHYBY (QPIWS):")
    print("-" * 50)
    
    warnings = get_mpp_data('QPIWS')
    if warnings:
        warning_codes = warnings.get('warning_codes', '')
        if warning_codes and warning_codes != '00000000':
            print(f"Varovaci kody: {warning_codes}")
            # Dekodování varovacích kódů (podle dokumentace)
            codes = [
                'Inverter fault', 'Bus over voltage', 'Bus under voltage',
                'Bus soft fail', 'Line fail', 'OPV short', 'Inverter voltage too low',
                'Inverter voltage too high', 'Over temperature', 'Fan locked',
                'Battery voltage high', 'Battery low alarm', 'Reserved',
                'Battery under shutdown', 'Reserved', 'Overload',
                'EEPROM fault', 'Inverter over current', 'Inverter soft fail',
                'Self test fail', 'OP DC voltage over', 'Bat open',
                'Current sensor fail', 'Battery short', 'Power limit',
                'PV voltage high', 'MPPT overload fault', 'MPPT overload warning',
                'Battery too low to charge', 'Reserved', 'Reserved', 'Reserved'
            ]
            
            for i, code in enumerate(warning_codes):
                if code == '1' and i < len(codes):
                    print(f"  ⚠️  {codes[i]}")
        else:
            print("✓ Zadna varovani")
    
    # 5. DODATECNE VYPOCTY
    if status:
        print("\n📊 DODATECNE VYPOCTY:")
        print("-" * 50)
        
        # Celkovy vykon baterie (kladny = vybijeni, zaporny = nabijeni)
        bat_voltage = status.get('battery_voltage', 0)
        bat_charge = status.get('battery_charging_current', 0)
        bat_discharge = status.get('battery_discharge_current', 0)
        bat_power = bat_voltage * (bat_discharge - bat_charge)
        
        print(f"Vykon baterie:     {bat_power:>8.1f} W {'(vybijeni)' if bat_power > 0 else '(nabijeni)' if bat_power < 0 else '(klid)'}")
        
        # Efektivita (AC vystup / PV vstup)
        ac_power = status.get('ac_output_active_power', 0)
        if pv_power_calc > 0:
            efficiency = (ac_power / pv_power_calc) * 100
            print(f"Efektivita:        {efficiency:>8.1f} %")
        
        # Celkova spotreba
        total_consumption = ac_power + abs(bat_power) if bat_power < 0 else ac_power - bat_power
        print(f"Celkova spotreba:  {total_consumption:>8.1f} W")
    
    print("\n" + "="*80)
    print("Hotovo! Pro kontinualni monitoring spustte:")
    print("python3 /home/dell/mpp_solar_integration.py")
    print("="*80)

if __name__ == "__main__":
    show_all_current_data()