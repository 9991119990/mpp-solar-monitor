# MPP Solar PIP5048MG Monitor

🔋 Kompletní monitoring řešení pro MPP Solar PIP5048MG měnič s integrací do Home Assistant

## 🌟 Funkce

- ✅ **Přímé čtení dat** z měniče přes USB HID (bez aplikace)
- ✅ **Kompletní monitoring** všech parametrů (PV, baterie, AC, systém)
- ✅ **Home Assistant integrace** přes MQTT autodiscovery
- ✅ **Kontinuální monitoring** s různými intervaly
- ✅ **JSON export** dat pro další zpracování
- ✅ **Rychlý přehled** v reálném čase

## 📊 Vyčítané hodnoty

### Solární panely
- Napětí a proud PV vstupů
- Vypočítaný a hardware měřený výkon

### Baterie  
- Napětí, kapacita v %
- Nabíjecí/vybíjecí proud
- Vypočítaný výkon baterie

### AC síť/výstup
- Vstupní/výstupní napětí a frekvence
- Aktivní výkon a zatížení
- Zdánlivý výkon

### Systém
- Teplota chladiče
- Bus napětí  
- Statusové indikátory (nabíjení, zatížení, atd.)

## 🚀 Rychlé spuštění

### Zobrazit aktuální data
```bash
python3 show_current_data.py
```

### Rychlý monitoring
```bash
python3 quick_monitor.py
```

### Home Assistant MQTT
```bash
# Upravte IP adresu MQTT broker v souboru
nano mpp_mqtt_publisher.py

# Spusťte publisher  
python3 mpp_mqtt_publisher.py
```

## 📋 Požadavky

### Hardware
- MPP Solar PIP5048MG měnič
- USB kabel (připojený jako HID zařízení)
- Linux systém s přístupem k `/dev/hidraw*`

### Software
```bash
# Instalace mpp-solar knihovny
pip install --user mpp-solar

# Pro MQTT publisher
pip install --user paho-mqtt

# Oprávnění k HID zařízení
sudo chmod 666 /dev/hidraw2
```

## 📁 Soubory

- **`show_current_data.py`** - Kompletní zobrazení všech dat
- **`quick_monitor.py`** - Rychlý kontinuální monitor  
- **`mpp_mqtt_publisher.py`** - MQTT publisher pro HA
- **`mpp_solar_integration.py`** - Komplexní integrace s GUI
- **`home_assistant_mpp_solar.yaml`** - HA konfigurace
- **`README_MPP_Solar.md`** - Detailní dokumentace

## 🏠 Home Assistant integrace

### Automatická konfigurace
1. Spusťte `mpp_mqtt_publisher.py`
2. Všechny senzory se automaticky objeví v HA
3. Najdete je v **Settings → Devices & Services → MQTT**

### Dostupné entity
```
sensor.mpp_solar_pv_input_power        # PV výkon
sensor.mpp_solar_battery_capacity      # Kapacita baterie  
sensor.mpp_solar_ac_output_power       # AC výkon
binary_sensor.mpp_solar_scc_charging   # SCC nabíjení
```

### Ukázka Dashboard
```yaml
type: entities
title: MPP Solar
entities:
  - sensor.mpp_solar_pv_input_power
  - sensor.mpp_solar_battery_capacity
  - sensor.mpp_solar_ac_output_power
  - sensor.mpp_solar_inverter_temperature
  - binary_sensor.mpp_solar_scc_charging
```

## ⚙️ Konfigurace

### MQTT nastavení
V souboru `mpp_mqtt_publisher.py`:
```python
BROKER_HOST = '192.168.1.100'  # IP vašeho HA
BROKER_PORT = 1883
USERNAME = None                 # MQTT username
PASSWORD = None                 # MQTT password
INTERVAL = 30                   # Sekund mezi updates
```

### HID zařízení
Pokud se číslo HID zařízení liší od `/dev/hidraw2`, upravte v skriptech:
```python
device_path = '/dev/hidrawX'  # X = vaše číslo
```

## 🛠️ Řešení problémů

### MPP Solar se nepřipojí
```bash
# Najděte HID zařízení
ls -la /dev/hidraw*

# Test komunikace
mpp-solar -p /dev/hidraw2 -c QPI

# Oprávnění
sudo chmod 666 /dev/hidraw2
```

### MQTT nepracuje
- Zkontrolujte IP adresu MQTT broker
- Ověřte přihlašovací údaje
- Zkontrolujte firewall na portu 1883

## 📈 Příklad výstupu

```
================================================================================
                      MPP SOLAR PIP5048MG - AKTUALNI DATA                       
                            Cas: 2025-06-24 18:52:47                            
================================================================================

⚡ HLAVNI STATUS (QPIGS):
--------------------------------------------------
Solarni panely:
  Napeti:           237.2 V
  Proud:              3.0 A  
  Vykon (calc):     711.6 W

Baterie:
  Napeti:            53.0 V
  Kapacita:            58 %
  Nabijeni:             3 A

AC Vystup:
  Napeti:           229.9 V
  Vykon:                3 W
  Zatizeni:             0 %

System:
  Teplota:             47 °C

Stavy:
  ✓ SCC nabijeni
  ✓ Zatizeni zapnuto
```

## 📄 Licence

MIT License - Volně použitelné

## 🤝 Přispívání

Návrhy a pull requesty jsou vítány!

---

**⚡ Vytvořeno pro efektivní monitoring MPP Solar systémů**