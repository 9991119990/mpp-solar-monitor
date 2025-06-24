# MPP Solar PIP5048MG - Kompletní řešení pro monitoring

## 📋 Přehled vytvořených nástrojů

### 🔧 Základní skripty

1. **`show_current_data.py`** - Kompletní zobrazení všech dat
   - Zobrazí všechny dostupné parametry měniče
   - Včetně nastavení, varování a vypočítaných hodnot
   ```bash
   python3 show_current_data.py
   ```

2. **`quick_monitor.py`** - Rychlý kontinuální monitor  
   - Zobrazuje jen klíčové hodnoty v reálném čase
   - Refresh každé 2 sekundy
   ```bash
   python3 quick_monitor.py
   ```

3. **`mpp_solar_integration.py`** - Komplexní integrace
   - Plné funkce včetně JSON exportu
   - Generování HA konfigurace
   - Kontinuální monitoring
   ```bash
   python3 mpp_solar_integration.py
   ```

### 🏠 Home Assistant integrace

4. **`mpp_mqtt_publisher.py`** - MQTT Publisher pro HA
   - Automatická MQTT autodiscovery konfigurace
   - Kontinuální publikování dat do HA
   - Připravený pro okamžité použití
   ```bash
   python3 mpp_mqtt_publisher.py
   ```

5. **`home_assistant_mpp_solar.yaml`** - HA konfigurace
   - Předpřipravená konfigurace sensorů
   - MQTT topics a device discovery

## 🚀 Rychlé spuštění

### Zobrazit aktuální data
```bash
python3 /home/dell/show_current_data.py
```

### Rychlý monitoring
```bash
python3 /home/dell/quick_monitor.py
```

### MQTT pro Home Assistant
```bash
# Upravte IP adresu MQTT broker v souboru
nano /home/dell/mpp_mqtt_publisher.py

# Spusťte publisher
python3 /home/dell/mpp_mqtt_publisher.py
```

## 📊 Vyčítané hodnoty

### AC Síť/Výstup
- Vstupní napětí a frekvence  
- Výstupní napětí, frekvence, výkon
- Zatížení v procentech

### Baterie
- Napětí baterie
- Nabíjecí/vybíjecí proud
- Kapacita v procentech
- Vypočítaný výkon baterie

### Solární panely  
- PV napětí a proud
- Vypočítaný PV výkon
- Hardware měřený výkon

### Systém
- Teplota chladiče
- Bus napětí
- Různé statusové indikátory

## 🔗 Home Assistant integrace

### Automatická konfigurace
1. Spusťte `mpp_mqtt_publisher.py`
2. Publisher automaticky vytvoří všechny senzory v HA
3. Najdete je v **Settings → Devices & Services → MQTT**

### Dostupné entity
- `sensor.mpp_solar_*` - Všechny numerické hodnoty
- `binary_sensor.mpp_solar_*` - Statusové indikátory
- Automatické ikony a jednotky

### MQTT Topics
```
mpp_solar/sensor/ac_output_voltage → 230.1
mpp_solar/sensor/battery_voltage → 52.8  
mpp_solar/sensor/pv_input_power → 455
mpp_solar/binary_sensor/is_scc_charging_on → 1
```

## ⚙️ Konfigurace

### MQTT Publisher nastavení
Upravte v souboru `mpp_mqtt_publisher.py`:
```python
BROKER_HOST = '192.168.1.100'  # IP vašeho HA
BROKER_PORT = 1883
USERNAME = 'mqtt_user'          # Pokud je potřeba
PASSWORD = 'mqtt_pass'          # Pokud je potřeba  
INTERVAL = 30                   # Sekund mezi aktualizacemi
```

### HID zařízení
- MPP Solar používá USB HID: `/dev/hidraw2`
- Pokud se číslo změní, upravte v skriptech

## 🛠️ Řešení problémů

### MPP Solar se nepřipojí
```bash
# Zkontrolujte HID zařízení
ls -la /dev/hidraw*

# Nastavte oprávnění  
sudo chmod 666 /dev/hidraw2

# Test komunikace
mpp-solar -p /dev/hidraw2 -c QPI
```

### MQTT se nepřipojí
- Zkontrolujte IP adresu broker
- Ověřte přihlašovací údaje
- Zkontrolujte firewall

### Chybějící data
- Některé hodnoty mohou být `N/A` nebo `0`
- To je normální podle stavu měniče

## 📈 Monitoring v provozu

### Typické hodnoty během dne
- **Ráno**: PV napětí roste, začíná nabíjení
- **Poledne**: Maximální PV výkon, baterie nabíjení
- **Večer**: PV klesá, přechod na baterie
- **Noc**: Běh z baterií

### Klíčové indikátory
- `SCC Charging` = Solární nabíjení aktivní
- `Load On` = Zatížení připojeno  
- `Battery Capacity` = Stav baterie
- `AC Output Load` = Aktuální zatížení

## 🎯 Použití v Home Assistant

### Dashboard karty
```yaml
type: entities
entities:
  - sensor.mpp_solar_pv_input_power
  - sensor.mpp_solar_battery_capacity
  - sensor.mpp_solar_ac_output_power
  - binary_sensor.mpp_solar_scc_charging
```

### Automatizace
```yaml
automation:
  - alias: "Low battery warning"
    trigger:
      platform: numeric_state
      entity_id: sensor.mpp_solar_battery_capacity
      below: 20
    action:
      service: notify.mobile_app
      data:
        message: "Baterie solárního systému je nízká: {{ states('sensor.mpp_solar_battery_capacity') }}%"
```

---

**✅ MPP Solar PIP5048MG je nyní plně integrován!**

Pro spuštění monitoringu stačí spustit jeden ze skriptů podle potřeby.