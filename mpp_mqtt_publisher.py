#!/usr/bin/env python3
"""
MQTT Publisher pro MPP Solar data do Home Assistant
Publikuje data z MPP Solar PIP5048MG do MQTT pro HA autodiscovery
"""

import json
import time
import subprocess
import os
import sys
from datetime import datetime

# Přidáme mpp-solar do PATH
os.environ['PATH'] = f"{os.environ.get('PATH', '')}:/home/dell/.local/bin"

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("Instaluji paho-mqtt...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', 'paho-mqtt', '--break-system-packages'])
    import paho.mqtt.client as mqtt

class MPPMQTTPublisher:
    def __init__(self, broker_host='localhost', broker_port=1883, 
                 username=None, password=None, device_path='/dev/hidraw2'):
        
        self.device_path = device_path
        self.client = mqtt.Client()
        self.connected = False
        
        # MQTT callback
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
        # Autentifikace
        if username and password:
            self.client.username_pw_set(username, password)
        
        # Připojení
        try:
            self.client.connect(broker_host, broker_port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"Chyba připojení k MQTT broker: {e}")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f"✓ Připojeno k MQTT broker")
            self.publish_autodiscovery()
        else:
            print(f"✗ Chyba připojení k MQTT: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        print("✗ Odpojeno od MQTT broker")
    
    def get_mpp_data(self, command):
        """Získá data z MPP Solar"""
        try:
            cmd = ['mpp-solar', '-p', self.device_path, '-c', command, '-o', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                clean_data = {k: v for k, v in data.items() if not k.startswith('_')}
                return clean_data
            return None
        except Exception as e:
            print(f"Chyba při čtení {command}: {e}")
            return None
    
    def publish_autodiscovery(self):
        """Publikuje auto-discovery konfiguraci pro Home Assistant"""
        if not self.connected:
            return
        
        print("Publikuji HA autodiscovery konfiguraci...")
        
        # Získáme vzorová data
        sample_data = self.get_mpp_data('QPIGS')
        if not sample_data:
            print("Nelze získat vzorová data pro autodiscovery")
            return
        
        device_info = {
            "identifiers": ["mpp_solar_pip5048mg"],
            "name": "MPP Solar PIP5048MG",
            "model": "PIP5048MG", 
            "manufacturer": "MPP Solar",
            "sw_version": "PI30"
        }
        
        # Senzory
        sensors = [
            ('ac_input_voltage', 'AC Input Voltage', 'V', 'voltage', 'mdi:lightning'),
            ('ac_output_voltage', 'AC Output Voltage', 'V', 'voltage', 'mdi:power-plug'),
            ('ac_output_active_power', 'AC Output Power', 'W', 'power', 'mdi:flash'),
            ('ac_output_load', 'AC Output Load', '%', None, 'mdi:gauge'),
            ('battery_voltage', 'Battery Voltage', 'V', 'voltage', 'mdi:battery'),
            ('battery_charging_current', 'Battery Charging Current', 'A', 'current', 'mdi:battery-charging'),
            ('battery_discharge_current', 'Battery Discharge Current', 'A', 'current', 'mdi:battery-minus'),
            ('battery_capacity', 'Battery Capacity', '%', 'battery', 'mdi:battery'),
            ('pv_input_voltage', 'PV Input Voltage', 'V', 'voltage', 'mdi:solar-power'),
            ('pv_input_current_for_battery', 'PV Input Current', 'A', 'current', 'mdi:solar-power'),
            ('pv_input_power', 'PV Input Power', 'W', 'power', 'mdi:solar-power'),
            ('inverter_heat_sink_temperature', 'Inverter Temperature', '°C', 'temperature', 'mdi:thermometer'),
            ('bus_voltage', 'Bus Voltage', 'V', 'voltage', 'mdi:flash')
        ]
        
        for sensor_key, name, unit, device_class, icon in sensors:
            if sensor_key in sample_data:
                config = {
                    "name": f"MPP Solar {name}",
                    "unique_id": f"mpp_solar_{sensor_key}",
                    "state_topic": f"mpp_solar/sensor/{sensor_key}",
                    "unit_of_measurement": unit,
                    "icon": icon,
                    "device": device_info
                }
                
                if device_class:
                    config["device_class"] = device_class
                
                config_topic = f"homeassistant/sensor/mpp_solar_{sensor_key}/config"
                self.client.publish(config_topic, json.dumps(config), retain=True)
        
        # Binary senzory
        binary_sensors = [
            ('is_load_on', 'Load Status', 'mdi:power'),
            ('is_scc_charging_on', 'SCC Charging', 'mdi:battery-charging'),
            ('is_ac_charging_on', 'AC Charging', 'mdi:power-plug'),
            ('is_charging_on', 'Charging Status', 'mdi:battery-plus')
        ]
        
        for sensor_key, name, icon in binary_sensors:
            if sensor_key in sample_data:
                config = {
                    "name": f"MPP Solar {name}",
                    "unique_id": f"mpp_solar_{sensor_key}",
                    "state_topic": f"mpp_solar/binary_sensor/{sensor_key}",
                    "payload_on": "1",
                    "payload_off": "0",
                    "icon": icon,
                    "device": device_info
                }
                
                config_topic = f"homeassistant/binary_sensor/mpp_solar_{sensor_key}/config"
                self.client.publish(config_topic, json.dumps(config), retain=True)
        
        print("✓ Autodiscovery konfigurace publikována")
    
    def publish_data(self):
        """Publikuje aktuální data"""
        if not self.connected:
            print("✗ Není připojení k MQTT")
            return False
        
        # Získáme všechna data
        status_data = self.get_mpp_data('QPIGS')
        settings_data = self.get_mpp_data('QPIRI') 
        
        if not status_data:
            print("✗ Nepodařilo se získat data")
            return False
        
        # Publikujeme všechny hodnoty ze statusu
        for key, value in status_data.items():
            if isinstance(value, (int, float)):
                topic = f"mpp_solar/sensor/{key}"
                self.client.publish(topic, str(value))
            elif isinstance(value, bool) or str(value) in ['0', '1']:
                topic = f"mpp_solar/binary_sensor/{key}"
                self.client.publish(topic, str(int(value)))
        
        # Vypočítané hodnoty
        pv_voltage = status_data.get('pv_input_voltage', 0)
        pv_current = status_data.get('pv_input_current_for_battery', 0)
        pv_power_calc = round(pv_voltage * pv_current, 1)
        
        bat_voltage = status_data.get('battery_voltage', 0)
        bat_charge = status_data.get('battery_charging_current', 0)
        bat_discharge = status_data.get('battery_discharge_current', 0)
        bat_power = round(bat_voltage * (bat_discharge - bat_charge), 1)
        
        # Publikujeme vypočítané hodnoty
        self.client.publish("mpp_solar/sensor/pv_power_calculated", str(pv_power_calc))
        self.client.publish("mpp_solar/sensor/battery_power", str(bat_power))
        
        # Efektivita
        ac_power = status_data.get('ac_output_active_power', 0)
        if pv_power_calc > 0:
            efficiency = round((ac_power / pv_power_calc) * 100, 1)
            self.client.publish("mpp_solar/sensor/efficiency", str(efficiency))
        
        # Timestamp
        self.client.publish("mpp_solar/sensor/last_update", datetime.now().isoformat())
        
        return True
    
    def run_continuous(self, interval=30):
        """Kontinuální publikování dat"""
        print(f"🚀 MPP Solar MQTT Publisher spuštěn")
        print(f"📊 Interval publikování: {interval} sekund")
        print(f"📡 Device: {self.device_path}")
        print("📋 Stiskněte Ctrl+C pro ukončení\n")
        
        try:
            while True:
                if self.publish_data():
                    print(f"✓ {datetime.now().strftime('%H:%M:%S')} - Data publikována")
                else:
                    print(f"✗ {datetime.now().strftime('%H:%M:%S')} - Chyba publikování")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 MQTT Publisher ukončen")
        finally:
            self.client.loop_stop()
            self.client.disconnect()

def main():
    print("MPP SOLAR MQTT PUBLISHER PRO HOME ASSISTANT")
    print("="*50)
    
    # Konfigurace MQTT - upravte podle vašeho prostředí
    BROKER_HOST = 'localhost'  # IP adresa vašeho Home Assistant/MQTT broker
    BROKER_PORT = 1883
    USERNAME = None            # MQTT username (pokud je potřeba)
    PASSWORD = None            # MQTT password (pokud je potřeba)
    INTERVAL = 30              # Interval v sekundách
    
    print(f"MQTT Broker: {BROKER_HOST}:{BROKER_PORT}")
    print(f"Username: {USERNAME or 'None'}")
    print(f"Interval: {INTERVAL}s")
    
    # Test připojení k MPP Solar
    print("\nTestuji připojení k MPP Solar...")
    try:
        cmd = ['mpp-solar', '-p', '/dev/hidraw2', '-c', 'QPI', '-o', 'json']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            protocol = data.get('protocol_id', 'Unknown')
            print(f"✓ MPP Solar připojen (protokol: {protocol})")
        else:
            print("✗ MPP Solar nedostupný")
            return
    except Exception as e:
        print(f"✗ Chyba testu MPP Solar: {e}")
        return
    
    # Spustíme publisher
    publisher = MPPMQTTPublisher(BROKER_HOST, BROKER_PORT, USERNAME, PASSWORD)
    
    # Počkáme na připojení
    for i in range(5):
        if publisher.connected:
            break
        time.sleep(1)
    
    if not publisher.connected:
        print("✗ Nepodařilo se připojit k MQTT broker")
        print("Zkontrolujte:")
        print("- Je MQTT broker spuštěný?")
        print("- Je správná IP adresa a port?")
        print("- Jsou správné přihlašovací údaje?")
        return
    
    # Spustíme kontinuální publikování
    publisher.run_continuous(INTERVAL)

if __name__ == "__main__":
    main()