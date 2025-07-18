# Instalace EASUN monitoringu do Home Assistant

## Předpoklady
- ✓ EASUN SHM II 7K měnič s RJ45 COMM portem
- ✓ USB-RS232 převodník s křížený kabelem
- ✓ Ubuntu/Linux PC s přístupem k HA
- ✓ Home Assistant s Mosquitto broker

## Kroky instalace

### 1. Ověření komunikace
```bash
cd /home/dell/Měniče/Easun
source venv/bin/activate
mpp-solar -p /dev/ttyUSB0 -P PI30 -b 2400 -c QPIGS
```

Pokud vidíte data, komunikace funguje!

### 2. Konfigurace MQTT
Upravte soubor `send_easun_data.sh`:
```bash
nano send_easun_data.sh
```

Změňte tyto hodnoty:
- `MQTT_BROKER="192.168.68.250"` - IP vašeho HA
- `MQTT_USER="váš_ha_user"`
- `MQTT_PASS="vaše_ha_heslo"`

### 3. Test odesílání dat
```bash
./send_easun_data.sh
```

### 4. Instalace systemd služby
```bash
# Zkopírovat soubory
sudo cp systemd/easun-ha.service /etc/systemd/system/
sudo cp systemd/easun-ha.timer /etc/systemd/system/

# Načíst a spustit
sudo systemctl daemon-reload
sudo systemctl enable easun-ha.timer
sudo systemctl start easun-ha.timer

# Zkontrolovat stav
systemctl status easun-ha.timer
```

### 5. Home Assistant konfigurace
Přidejte do `configuration.yaml`:

```yaml
mqtt:
  sensor:
    - name: "EASUN AC Output Power"
      state_topic: "easun/inverter/QPIGS"
      value_template: "{{ value_json.ac_output_active_power.value }}"
      unit_of_measurement: "W"
      device_class: power
      state_class: measurement
      unique_id: easun_ac_output_w

    - name: "EASUN Battery Voltage"
      state_topic: "easun/inverter/QPIGS"
      value_template: "{{ value_json.battery_voltage.value }}"
      unit_of_measurement: "V"
      device_class: voltage
      state_class: measurement
      unique_id: easun_battery_v

    - name: "EASUN Battery Capacity"
      state_topic: "easun/inverter/QPIGS"
      value_template: "{{ value_json.battery_capacity.value }}"
      unit_of_measurement: "%"
      device_class: battery
      state_class: measurement
      unique_id: easun_battery_percent

    - name: "EASUN PV Power"
      state_topic: "easun/inverter/QPIGS"
      value_template: "{{ value_json.pv_input_current.value * value_json.pv_input_voltage.value }}"
      unit_of_measurement: "W"
      device_class: power
      state_class: measurement
      unique_id: easun_pv_power

    - name: "EASUN Temperature"
      state_topic: "easun/inverter/QPIGS"
      value_template: "{{ value_json.inverter_heat_sink_temperature.value }}"
      unit_of_measurement: "°C"
      device_class: temperature
      state_class: measurement
      unique_id: easun_temperature

    - name: "EASUN Load"
      state_topic: "easun/inverter/QPIGS"
      value_template: "{{ value_json.output_load_percent.value }}"
      unit_of_measurement: "%"
      state_class: measurement
      unique_id: easun_load_percent
```

### 6. Restart HA
Po přidání senzorů restartujte Home Assistant.

## Ověření funkčnosti

1. **MQTT Explorer**: Zkontrolujte topic `easun/inverter/QPIGS`
2. **HA Developer Tools**: States -> hledejte `sensor.easun_*`
3. **Systemd logs**: `sudo journalctl -u easun-ha.timer -f`

## Řešení problémů
Viz soubor `TROUBLESHOOTING.md`