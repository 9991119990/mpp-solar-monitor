# EASUN SHM II 7K - Kompletní backup projektu

**Datum:** 28. června 2025  
**Stav:** Připraveno k testování komunikace na Raspberry Pi

## 🎯 Cíl projektu
Vytvořit monitoring pro EASUN SHM II 7K měnič, který bude číst data přímo na Raspberry Pi s Home Assistant (bez externího PC).

## 📋 Dosavadní progress

### ✅ Dokončeno:
1. **Hardware identifikace** - EASUN SHM II 7K s RJ45 COMM portem
2. **USB adaptér rozpoznán** - Prolific PL2303 (067b:23a3) 
3. **Protokol výzkum** - PI30 protokol, 2400 baud, QPIGS příkaz
4. **PySerial instalace** - Úspěšně nainstalováno v HA OS
5. **Add-on struktura** - Připravené soubory v `/config/addons/easun-monitor/`

### ❌ Problém:
- **Komunikace PC → EASUN**: Nefunguje na novém Ubuntu PC
- **Komunikace RPi → EASUN**: Ještě netestováno (Python syntax problémy)

## 🔧 Hardware setup

### Úspěšné připojení na RPi:
```
EASUN měnič [RJ45 COMM] → Kabel → USB-RS232 (PL2303) → Raspberry Pi
```

### USB zařízení rozpoznáno:
```bash
lsusb: Bus 001 Device 002: ID 067b:23a3 Prolific Technology Inc. USB-Serial Controller
dmesg: pl2303 converter now attached to ttyUSB0
ls: /dev/ttyUSB0 exists
```

## 📁 Vytvořené soubory

### Na PC (`/home/dell/Měniče/Easun/`):
- `test_easun.py` - Základní testovací skript
- `test_easun_advanced.py` - Test různých baud rates
- `easun_reader.py` - Čtečka s parsováním
- `send_easun_data.sh` - MQTT publikační skript
- `systemd/easun-ha.service` - Systemd služba
- `systemd/easun-ha.timer` - Timer pro automatické spouštění
- `INSTALACE.md` - Instalační návod
- `TROUBLESHOOTING.md` - Řešení problémů

### Na RPi (`/config/addons/easun-monitor/`):
- `config.yaml` - Add-on konfigurace
- `Dockerfile` - Docker container definice
- Připravené pro `run.py` (Python skript pro čtení dat)

## 🐛 Technické problémy

### 1. PC komunikace:
- Nový Ubuntu PC nenavazuje komunikaci s EASUN
- Starý PC fungoval podle původního návodu
- Prolific adaptér funguje, ale měnič neodpovídá

### 2. RPi Python syntax:
- Terminal v HA přidává odsazení při víceřádkových příkazech
- Heredoc a echo vytváří soubory s chybným odsazením
- Printf test měl syntax error v escape sekvencích

## 📡 Komunikační parametry

### Úspěšné z předchozího projektu:
```bash
mpp-solar -p /dev/ttyUSB0 -P PI30 -b 2400 -c QPIGS -o json_units
```

### QPIGS příkaz (hex):
```
Command: QPIGS
Hex: 5150494753b7a90d
```

### Očekávaná odpověď:
- Délka: ~110 bytů
- Formát: (hodnoty oddělené mezerou)
- Příklad: `(000.0 00.0 29.8 49.9 0344 0327 005 383 !1.40 000 042 0026...)`

## 🎯 Další kroky

### Priorita 1 - Test komunikace na RPi:
```bash
# Jednoduchý test bez syntax problémů
python3 -c "import serial,time;s=serial.Serial('/dev/ttyUSB0',2400,timeout=2);s.write(b'QPIGS\xb7\xa9\r');time.sleep(1);r=s.read(1000);print('Length:',len(r));s.close()"
```

### Priorita 2 - Funkční Python skript:
- Vytvořit `run.py` bez syntax chyb
- Test čtení dat z EASUN
- MQTT publikování na localhost

### Priorita 3 - Home Assistant integrace:
- Add-on instalace nebo přímý Python skript
- MQTT senzory v HA
- Automatické spouštění

## 📊 MQTT konfigurace

### Broker: localhost (na RPi)
### Topic: `easun/inverter/data`
### Data format:
```json
{
  "battery_voltage": 51.4,
  "battery_capacity": 42,
  "ac_output_power": 327,
  "pv_power": 172.1,
  "temperature": 26
}
```

### HA senzory:
```yaml
mqtt:
  sensor:
    - name: "EASUN Battery Voltage"
      state_topic: "easun/inverter/data"
      value_template: "{{ value_json.battery_voltage }}"
      unit_of_measurement: "V"
```

## 🔍 Debugging info

### USB adaptér:
- **Typ**: Prolific PL2303 
- **ID**: 067b:23a3
- **Driver**: pl2303 (loaded)
- **Device**: /dev/ttyUSB0
- **Permissions**: crw-rw---- root audio

### HA OS info:
- **Python**: 3.12.11
- **PySerial**: 3.5 (installed)
- **OS**: Home Assistant OS (Alpine-based)

## 💾 Záložní řešení

Pokud add-on nebude fungovat:
1. **Přímý Python skript** v `/config/` s cron jobem
2. **ESPHome integrace** (ESP32 jako proxy)
3. **Návrat k PC řešení** s novým USB adaptérem

## 🚨 Aktuální problém - Komunikace EASUN ↔ RPi

### Test provedený 28.6.2025:
- ✅ **USB adaptér funguje**: Port se otevírá OK
- ❌ **EASUN neodpovídá**: Žádná response na QPIGS příkazy
- ✅ **Hardware je v pořádku**: Měnič svítí, funguje, nabíjí baterie

### Testované příkazy:
```bash
# Test otevření portu
python3 -c "import serial;s=serial.Serial('/dev/ttyUSB0',2400);print('Port opened OK');s.close()"
# ✅ Výsledek: Port opened OK

# Test QPIGS příkazu
stty -F /dev/ttyUSB0 2400 cs8 -cstopb -parenb raw -echo
printf "QPIGS\xb7\xa9\r" > /dev/ttyUSB0
timeout 3 cat /dev/ttyUSB0 | od -x
# ❌ Výsledek: 0000000 (žádná data)
```

## 🔍 Výzkum problému

**Klíčové zjištění**: EASUN SHM II 7K **nepoužívá standardní PI30 protokol**!

### Možné příčiny:
1. **Jiný protokol** - EASUN může používat SRNE/Modbus místo PI30
2. **Napájení USB** - RPi má slabší napájení než PC
3. **Timing** - RPi má jiné časování než PC
4. **Driver problémy** - PL2303 na RPi vs PC

### Doporučená řešení k testování:

#### 1. **Protokol detekce**:
```bash
stty -F /dev/ttyUSB0 2400 cs8 -cstopb -parenb raw -echo
printf "QPI\r" > /dev/ttyUSB0
timeout 5 cat /dev/ttyUSB0
```

#### 2. **Driver reset**:
```bash
sudo rmmod pl2303
sudo modprobe pl2303
dmesg | tail -5
```

#### 3. **Minicom interaktivní test**:
```bash
sudo minicom -D /dev/ttyUSB0 -b 2400
# V minicomu zadat: QPI + Enter
```

#### 4. **Alternative protokoly**:
- PI18 místo PI30
- SRNE/Modbus protokol
- Solarman5 protokol

### Hardware doporučení:
- **Powered USB hub** pro stabilní napájení
- **FTDI adaptér** místo PL2303 (spolehlivější)
- **WiFi dongle** alternativa

---

**Status**: ❌ Problém s komunikací - EASUN neodpovídá na PI30 příkazy  
**Další krok**: Test protokol detekce (QPI příkaz) a driver reset