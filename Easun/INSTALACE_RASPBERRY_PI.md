# Instalace EASUN monitoru na Raspberry Pi s Home Assistant

## 1. Příprava Raspberry Pi

### Kontrola sériového portu
```bash
# Zjistit název USB převodníku
ls -la /dev/ttyUSB* /dev/hidraw*

# Nebo pro GPIO serial port
ls -la /dev/ttyAMA* /dev/serial*
```

### Oprávnění pro sériový port
```bash
# Přidat uživatele do skupiny dialout
sudo usermod -a -G dialout $USER

# DŮLEŽITÉ: Odhlásit se a znovu přihlásit!

# Ověřit skupiny
groups
```

## 2. Instalace závislostí

### Na Raspberry Pi OS
```bash
sudo apt update
sudo apt install python3-pip python3-serial python3-paho-mqtt
```

### Nebo přes pip
```bash
pip3 install pyserial paho-mqtt
```

## 3. Konfigurace skriptů

### Upravit konfiguraci v `send_easun_data_ha.sh`:
```bash
# Serial port - zkontrolovat správný port!
export EASUN_PORT="/dev/ttyUSB0"  

# MQTT - upravit podle vaší HA konfigurace
export MQTT_BROKER="localhost"     # nebo IP adresa HA
export MQTT_USER="homeassistant"   # váš HA uživatel
export MQTT_PASS="your_password"   # ZMĚNIT na vaše heslo!
```

## 4. Test komunikace

### 1. Test sériového portu
```bash
# Kontrola, že port existuje a máme práva
ls -la /dev/ttyUSB0
```

### 2. Test čtení dat
```bash
cd /home/dell/Měniče/Easun
./send_easun_data_ha.sh --test
```

Měli byste vidět:
```
✓ EASUN communication successful!
Battery: 52.1V (85%)
PV: 120.5V × 2.3A = 277.2W
AC Output: 250W (15% load)
Temperature: 38°C
```

### 3. Test MQTT spojení
```bash
# Nainstalovat mosquitto klienta
sudo apt install mosquitto-clients

# Test připojení
mosquitto_sub -h localhost -u homeassistant -P "your_password" -t "easun/#" -v
```

## 5. Automatické spouštění

### Systemd služba
Vytvořit `/etc/systemd/system/easun-ha.service`:
```ini
[Unit]
Description=EASUN to Home Assistant Bridge
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/dell/Měniče/Easun
ExecStart=/home/dell/Měniče/Easun/send_easun_data_ha.sh
Restart=on-failure
RestartSec=30s

[Install]
WantedBy=multi-user.target
```

### Timer pro periodické spouštění
Vytvořit `/etc/systemd/system/easun-ha.timer`:
```ini
[Unit]
Description=Run EASUN monitor every 30 seconds

[Timer]
OnBootSec=30s
OnUnitActiveSec=30s
Unit=easun-ha.service

[Install]
WantedBy=timers.target
```

### Aktivace
```bash
sudo systemctl daemon-reload
sudo systemctl enable easun-ha.timer
sudo systemctl start easun-ha.timer

# Kontrola stavu
systemctl status easun-ha.timer
journalctl -u easun-ha.service -f
```

## 6. Home Assistant konfigurace

V `configuration.yaml`:
```yaml
mqtt:
  sensor:
    - name: "EASUN Battery Voltage"
      state_topic: "easun/inverter/QPIGS"
      value_template: "{{ value_json.battery_voltage.value }}"
      unit_of_measurement: "V"
      device_class: voltage
      
    - name: "EASUN Battery Capacity"
      state_topic: "easun/inverter/QPIGS"
      value_template: "{{ value_json.battery_capacity.value }}"
      unit_of_measurement: "%"
      device_class: battery
      
    - name: "EASUN PV Power"
      state_topic: "easun/inverter/QPIGS"
      value_template: "{{ value_json.pv_input_power.value }}"
      unit_of_measurement: "W"
      device_class: power
      
    - name: "EASUN AC Output Power"
      state_topic: "easun/inverter/QPIGS"
      value_template: "{{ value_json.ac_output_active_power.value }}"
      unit_of_measurement: "W"
      device_class: power
      
    - name: "EASUN Temperature"
      state_topic: "easun/inverter/QPIGS"
      value_template: "{{ value_json.inverter_temperature.value }}"
      unit_of_measurement: "°C"
      device_class: temperature
```

## 7. Řešení problémů

### Port se neotevírá
- Zkontrolovat oprávnění: `ls -la /dev/ttyUSB0`
- Zkusit jako root: `sudo ./send_easun_data_ha.sh --test`
- Restartovat USB: odpojit a připojit kabel

### Žádná odpověď z měniče
- Zkontrolovat kabel (null modem/crossover)
- Zkusit jiný baud rate v `easun_raspberry_ha.py` (9600)
- Zkontrolovat DTR signál je nastaven na True

### MQTT nepřijímá data
- Ověřit přihlašovací údaje
- Zkontrolovat firewall/porty
- Test: `mosquitto_pub -h localhost -u user -P pass -t test -m "hello"`

### Raspberry Pi specifické problémy
- Vypnout serial console: `sudo raspi-config` → Interface Options → Serial
- Zkusit GPIO serial port místo USB: `/dev/ttyAMA0` nebo `/dev/serial0`
- Přidat do `/boot/config.txt`: `enable_uart=1`