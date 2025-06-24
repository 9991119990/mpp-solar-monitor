#!/usr/bin/env python3
"""
MPP Solar PIP5048MG - Kompletní integrace pro monitoring a Home Assistant
"""

import json
import time
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# Přidáme mpp-solar do PATH
os.environ['PATH'] = f"{os.environ.get('PATH', '')}:/home/dell/.local/bin"

class MPPSolarMonitor:
    def __init__(self, device_path='/dev/hidraw2'):
        self.device_path = device_path
        self.last_data = {}
        
    def get_device_info(self):
        """Získá základní informace o zařízení"""
        info = {}
        
        # Protocol ID
        result = self._run_command('QPI')
        if result:
            info['protocol'] = result.get('protocol_id', 'Unknown')
        
        # Device ID
        result = self._run_command('QID')
        if result:
            info['device_id'] = result.get('device_id', 'Unknown')
        
        # Firmware version
        result = self._run_command('QVFW')
        if result:
            info['firmware'] = result.get('firmware_version', 'Unknown')
        
        # Mode
        result = self._run_command('QMOD')
        if result:
            info['mode'] = result.get('device_mode', 'Unknown')
        
        return info
    
    def get_status_data(self):
        """Získá aktuální stavová data"""
        return self._run_command('QPIGS')
    
    def get_settings_data(self):
        """Získá nastavení invertoru"""
        return self._run_command('QPIRI')
    
    def get_warning_status(self):
        """Získá varování a chyby"""
        return self._run_command('QPIWS')
    
    def _run_command(self, command):
        """Spustí mpp-solar příkaz a vrátí data"""
        try:
            cmd = ['mpp-solar', '-p', self.device_path, '-c', command, '-o', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                # Odstraníme metadata a vrátíme jen hodnoty
                clean_data = {k: v for k, v in data.items() if not k.startswith('_')}
                return clean_data
            else:
                print(f"Chyba příkazu {command}: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"Timeout při vykonávání příkazu {command}")
            return None
        except json.JSONDecodeError:
            print(f"Chyba parsování JSON pro příkaz {command}")
            return None
        except Exception as e:
            print(f"Chyba při vykonávání příkazu {command}: {e}")
            return None
    
    def get_all_data(self):
        """Získá všechna dostupná data"""
        timestamp = datetime.now()
        
        data = {
            'timestamp': timestamp.isoformat(),
            'device_info': self.get_device_info(),
            'status': self.get_status_data(),
            'settings': self.get_settings_data(),
            'warnings': self.get_warning_status()
        }
        
        # Přidáme vypočítané hodnoty
        if data['status']:
            status = data['status']
            
            # PV výkon
            pv_voltage = status.get('pv_input_voltage', 0)
            pv_current = status.get('pv_input_current_for_battery', 0)
            data['status']['pv_power_calculated'] = round(pv_voltage * pv_current, 1)
            
            # Baterie výkon
            bat_voltage = status.get('battery_voltage', 0)
            bat_discharge = status.get('battery_discharge_current', 0)
            bat_charge = status.get('battery_charging_current', 0)
            net_current = bat_discharge - bat_charge
            data['status']['battery_power'] = round(bat_voltage * net_current, 1)
            
            # Efektivita
            pv_power = data['status']['pv_power_calculated']
            ac_power = status.get('ac_output_active_power', 0)
            if pv_power > 0:
                data['status']['efficiency'] = round((ac_power / pv_power) * 100, 1)
            else:
                data['status']['efficiency'] = 0
        
        self.last_data = data
        return data
    
    def print_status(self, data=None):
        """Zobrazí přehledný status"""
        if not data:
            data = self.last_data
        
        if not data or 'status' not in data:
            print("Žádná data k zobrazení")
            return
        
        status = data['status']
        device_info = data.get('device_info', {})
        
        print("\n" + "="*70)
        print(f"{'MPP Solar PIP5048MG - Monitoring':^70}")
        print("="*70)
        
        print(f"Čas:      {data['timestamp']}")
        print(f"Zařízení: {device_info.get('device_id', 'N/A')}")
        print(f"Protokol: {device_info.get('protocol', 'N/A')}")
        print(f"Režim:    {device_info.get('mode', 'N/A')}")
        
        print("\n" + "-"*70)
        print("AC SÍŤOVÉ NAPÁJENÍ")
        print("-"*70)
        print(f"Napětí:    {status.get('ac_input_voltage', 0):>8.1f} V")
        print(f"Frekvence: {status.get('ac_input_frequency', 0):>8.1f} Hz")
        
        print("\n" + "-"*70)
        print("AC VÝSTUP")
        print("-"*70)
        print(f"Napětí:       {status.get('ac_output_voltage', 0):>8.1f} V")
        print(f"Frekvence:    {status.get('ac_output_frequency', 0):>8.1f} Hz")
        print(f"Výkon:        {status.get('ac_output_active_power', 0):>8d} W")
        print(f"Zdánlivý:     {status.get('ac_output_apparent_power', 0):>8d} VA")
        print(f"Zatížení:     {status.get('ac_output_load', 0):>8d} %")
        
        print("\n" + "-"*70)
        print("BATERIE")
        print("-"*70)
        print(f"Napětí:       {status.get('battery_voltage', 0):>8.1f} V")
        print(f"Nabíjení:     {status.get('battery_charging_current', 0):>8d} A")
        print(f"Vybíjení:     {status.get('battery_discharge_current', 0):>8d} A")
        print(f"Kapacita:     {status.get('battery_capacity', 0):>8d} %")
        print(f"Výkon:        {status.get('battery_power', 0):>8.1f} W")
        
        print("\n" + "-"*70)
        print("SOLÁRNÍ PANELY")
        print("-"*70)
        print(f"Napětí:       {status.get('pv_input_voltage', 0):>8.1f} V")
        print(f"Proud:        {status.get('pv_input_current_for_battery', 0):>8.1f} A")
        print(f"Výkon:        {status.get('pv_power_calculated', 0):>8.1f} W")
        print(f"Výkon (HW):   {status.get('pv_input_power', 0):>8d} W")
        
        print("\n" + "-"*70)
        print("SYSTÉM")
        print("-"*70)
        print(f"Teplota:      {status.get('inverter_heat_sink_temperature', 0):>8d} °C")
        print(f"Bus napětí:   {status.get('bus_voltage', 0):>8d} V")
        print(f"Efektivita:   {status.get('efficiency', 0):>8.1f} %")
        
        # Statusové indikátory
        print("\n" + "-"*70)
        print("STAVY")
        print("-"*70)
        indicators = {
            'Zatížení zapnuto': status.get('is_load_on', 0),
            'SCC nabíjení': status.get('is_scc_charging_on', 0),
            'AC nabíjení': status.get('is_ac_charging_on', 0),
            'Nabíjení aktivní': status.get('is_charging_on', 0),
        }
        
        for name, value in indicators.items():
            icon = "✓" if value else "✗"
            print(f"{icon} {name}")
        
        print("="*70)
    
    def save_to_json(self, filename=None, data=None):
        """Uloží data do JSON souboru"""
        if not data:
            data = self.get_all_data()
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"mpp_solar_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Data uložena do {filename}")
        except Exception as e:
            print(f"✗ Chyba při ukládání: {e}")
    
    def continuous_monitoring(self, interval=10, save_interval=300):
        """Kontinuální monitoring s ukládáním"""
        print(f"Spouštím kontinuální monitoring:")
        print(f"- Refresh interval: {interval}s")
        print(f"- Save interval: {save_interval}s")
        print("Stiskněte Ctrl+C pro ukončení\n")
        
        last_save = 0
        
        try:
            while True:
                # Získej a zobraz aktuální data
                data = self.get_all_data()
                self.print_status(data)
                
                # Periodické ukládání
                current_time = time.time()
                if current_time - last_save >= save_interval:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    self.save_to_json(f"mpp_log_{timestamp}.json", data)
                    last_save = current_time
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring ukončen")
            
            # Poslední uložení
            final_data = self.get_all_data()
            self.save_to_json("mpp_final.json", final_data)
    
    def generate_home_assistant_config(self):
        """Generuje konfiguraci pro Home Assistant"""
        
        # Získáme vzorová data pro generování sensorů
        sample_data = self.get_all_data()
        if not sample_data or 'status' not in sample_data:
            print("Nelze získat data pro generování HA konfigurace")
            return
        
        status = sample_data['status']
        
        # MQTT sensor konfigurace
        ha_config = {
            'sensor': []
        }
        
        # Definice sensorů
        sensors = [
            ('ac_input_voltage', 'AC Input Voltage', 'V', 'voltage', 'mdi:lightning'),
            ('ac_output_voltage', 'AC Output Voltage', 'V', 'voltage', 'mdi:power-plug'),
            ('ac_output_active_power', 'AC Output Power', 'W', 'power', 'mdi:flash'),
            ('ac_output_load', 'AC Output Load', '%', None, 'mdi:gauge'),
            ('battery_voltage', 'Battery Voltage', 'V', 'voltage', 'mdi:battery'),
            ('battery_charging_current', 'Battery Charging Current', 'A', 'current', 'mdi:battery-charging'),
            ('battery_discharge_current', 'Battery Discharge Current', 'A', 'current', 'mdi:battery-minus'),
            ('battery_capacity', 'Battery Capacity', '%', 'battery', 'mdi:battery'),
            ('battery_power', 'Battery Power', 'W', 'power', 'mdi:battery-lightning'),
            ('pv_input_voltage', 'PV Input Voltage', 'V', 'voltage', 'mdi:solar-power'),
            ('pv_input_current_for_battery', 'PV Input Current', 'A', 'current', 'mdi:solar-power'),
            ('pv_power_calculated', 'PV Power', 'W', 'power', 'mdi:solar-power'),
            ('inverter_heat_sink_temperature', 'Inverter Temperature', '°C', 'temperature', 'mdi:thermometer'),
            ('efficiency', 'Inverter Efficiency', '%', None, 'mdi:percent'),
        ]
        
        for key, name, unit, device_class, icon in sensors:
            if key in status:
                sensor_config = {
                    'name': f"MPP Solar {name}",
                    'unique_id': f"mpp_solar_{key}",
                    'state_topic': f"homeassistant/sensor/mpp_solar/{key}/state",
                    'unit_of_measurement': unit,
                    'icon': icon,
                    'device': {
                        'identifiers': ['mpp_solar_pip5048mg'],
                        'name': 'MPP Solar PIP5048MG',
                        'model': 'PIP5048MG',
                        'manufacturer': 'MPP Solar'
                    }
                }
                
                if device_class:
                    sensor_config['device_class'] = device_class
                
                ha_config['sensor'].append(sensor_config)
        
        # Binary sensorory pro stavy
        binary_sensors = [
            ('is_load_on', 'Load Status', 'mdi:power'),
            ('is_scc_charging_on', 'SCC Charging', 'mdi:battery-charging'),
            ('is_ac_charging_on', 'AC Charging', 'mdi:power-plug'),
            ('is_charging_on', 'Charging Status', 'mdi:battery-plus'),
        ]
        
        ha_config['binary_sensor'] = []
        for key, name, icon in binary_sensors:
            if key in status:
                sensor_config = {
                    'name': f"MPP Solar {name}",
                    'unique_id': f"mpp_solar_{key}",
                    'state_topic': f"homeassistant/binary_sensor/mpp_solar/{key}/state",
                    'payload_on': '1',
                    'payload_off': '0',
                    'icon': icon,
                    'device': {
                        'identifiers': ['mpp_solar_pip5048mg'],
                        'name': 'MPP Solar PIP5048MG',
                        'model': 'PIP5048MG',
                        'manufacturer': 'MPP Solar'
                    }
                }
                ha_config['binary_sensor'].append(sensor_config)
        
        # Uložení konfigurace
        with open('home_assistant_mpp_solar.yaml', 'w', encoding='utf-8') as f:
            import yaml
            yaml.dump(ha_config, f, default_flow_style=False, allow_unicode=True)
        
        print("✓ Home Assistant konfigurace vygenerována: home_assistant_mpp_solar.yaml")
        
        # Generuj MQTT publisher skript
        self._generate_mqtt_publisher()
        
        return ha_config
    
    def _generate_mqtt_publisher(self):
        """Generuje MQTT publisher skript pro HA"""
        
        mqtt_script = '''#!/usr/bin/env python3
"""
MQTT Publisher pro MPP Solar data do Home Assistant
"""

import json
import time
import paho.mqtt.client as mqtt
from mpp_solar_integration import MPPSolarMonitor

class MQTTPublisher:
    def __init__(self, broker_host='localhost', broker_port=1883, 
                 username=None, password=None):
        self.client = mqtt.Client()
        self.monitor = MPPSolarMonitor()
        
        if username:
            self.client.username_pw_set(username, password)
        
        self.client.connect(broker_host, broker_port, 60)
        
    def publish_data(self):
        """Publikuje aktuální data do MQTT"""
        data = self.monitor.get_all_data()
        
        if not data or 'status' not in data:
            return
        
        status = data['status']
        
        # Publikuj všechny hodnoty
        for key, value in status.items():
            topic = f"homeassistant/sensor/mpp_solar/{key}/state"
            self.client.publish(topic, str(value))
        
        print(f"✓ Data publikována do MQTT: {len(status)} hodnot")
    
    def run_continuous(self, interval=30):
        """Kontinuální publikování"""
        print(f"MQTT Publisher spuštěn (interval: {interval}s)")
        
        try:
            while True:
                self.publish_data()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\\nMQTT Publisher ukončen")
        finally:
            self.client.disconnect()

if __name__ == "__main__":
    # Konfigurace MQTT
    BROKER_HOST = 'localhost'  # IP vašeho Home Assistant
    BROKER_PORT = 1883
    USERNAME = None  # MQTT username
    PASSWORD = None  # MQTT password
    
    publisher = MQTTPublisher(BROKER_HOST, BROKER_PORT, USERNAME, PASSWORD)
    publisher.run_continuous(30)  # Publikuj každých 30 sekund
'''
        
        with open('mqtt_publisher.py', 'w', encoding='utf-8') as f:
            f.write(mqtt_script)
        
        print("✓ MQTT Publisher skript vygenerován: mqtt_publisher.py")

def main():
    print("MPP SOLAR PIP5048MG - INTEGRACE")
    print("="*50)
    
    monitor = MPPSolarMonitor()
    
    # Test připojení
    print("Testování připojení...")
    test_data = monitor.get_device_info()
    
    if not test_data or not any(test_data.values()):
        print("✗ Nepodařilo se připojit k MPP Solar")
        print("Zkontrolujte:")
        print("- Je měnič zapnutý?")
        print("- Je USB kabel připojený?")
        print("- Je /dev/hidraw2 dostupný?")
        return
    
    print("✓ Připojení úspěšné!")
    print(f"Protocol: {test_data.get('protocol', 'N/A')}")
    print(f"Device ID: {test_data.get('device_id', 'N/A')}")
    
    # Zobraz aktuální stav
    print("\nZískávám aktuální data...")
    current_data = monitor.get_all_data()
    monitor.print_status(current_data)
    
    # Menu možností
    while True:
        print("\n" + "="*50)
        print("MOŽNOSTI:")
        print("1. Obnovit data")
        print("2. Uložit do JSON")
        print("3. Kontinuální monitoring")
        print("4. Generovat Home Assistant konfiguraci")
        print("5. Ukončit")
        
        try:
            choice = input("\nVolba (1-5): ").strip()
            
            if choice == '1':
                current_data = monitor.get_all_data()
                monitor.print_status(current_data)
                
            elif choice == '2':
                monitor.save_to_json()
                
            elif choice == '3':
                interval = input("Interval obnovení (výchozí 10s): ").strip()
                interval = int(interval) if interval.isdigit() else 10
                monitor.continuous_monitoring(interval)
                
            elif choice == '4':
                print("\nGeneruji Home Assistant konfiguraci...")
                monitor.generate_home_assistant_config()
                print("\nNávod k použití:")
                print("1. Zkopírujte home_assistant_mpp_solar.yaml do HA konfigurace")
                print("2. Spusťte mqtt_publisher.py pro zasílání dat")
                print("3. Restartujte Home Assistant")
                
            elif choice == '5':
                print("Ukončuji...")
                break
                
            else:
                print("Neplatná volba")
                
        except EOFError:
            print("\nUkončuji...")
            break
        except ValueError:
            print("Neplatná hodnota")
        except KeyboardInterrupt:
            print("\nUkončuji...")
            break

if __name__ == "__main__":
    main()