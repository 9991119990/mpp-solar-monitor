# EASUN SHM II 7K Monitoring

Kompletní řešení pro čtení dat z EASUN SHM II 7K měniče a odesílání do Home Assistant přes MQTT.

## Stav projektu

✓ **Vytvořeno**: Všechny skripty a konfigurace  
❌ **Problém**: Komunikace s měničem na PC nefunguje  
✓ **Připraveno**: MQTT odesílání a HA integrace  

## Vytvořené soubory

### Testovací skripty
- `test_easun.py` - Základní test komunikace
- `test_easun_advanced.py` - Test různých baud rates  
- `test_pc_specific.py` - PC specifické testy
- `easun_wrapper.py` - Wrapper pro mpp-solar kompatibilitu
- `test_mqtt_connection.py` - Test MQTT připojení

### Produkční skripty
- `send_easun_data.sh` - Hlavní skript (používá mpp-solar)
- `send_easun_data_wrapper.sh` - Záložní skript (používá wrapper)

### Systemd služby
- `systemd/easun-ha.service` - Systemd služba
- `systemd/easun-ha.timer` - Timer pro automatické spouštění

### Dokumentace
- `INSTALACE.md` - Instalační návod
- `TROUBLESHOOTING.md` - Řešení problémů
- `README.md` - Tento soubor

## Současný problém

Měnič neodpovídá na příkazy když je připojený k PC, přestože stejný setup fungoval na Raspberry Pi.

### Možné příčiny:
1. **USB adaptér** - Prolific PL2303 se chová jinak na PC vs RPi
2. **Ovladače** - Možná potřebuje jiné nastavení na Ubuntu
3. **Napájení** - USB port na PC může mít jiné napájení
4. **Timing** - PC má jiné časování než RPi

### Co zkusit:
1. **Fyzicky odpojit a připojit** USB kabel
2. **Jiný USB port** - zkusit USB 2.0 místo 3.0
3. **Powered USB hub** - externí napájení
4. **Restart měniče** - vypnout/zapnout
5. **Test na RPi** - ověřit že tam stále funguje

## Až bude komunikace fungovat

1. **Upravit MQTT údaje** v `send_easun_data.sh`:
```bash
MQTT_BROKER="192.168.68.250"  # IP vašeho HA
MQTT_USER="váš_ha_user"
MQTT_PASS="vaše_ha_heslo"
```

2. **Test**: `./send_easun_data.sh`

3. **Instalace služby**:
```bash
sudo cp systemd/* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable easun-ha.timer
sudo systemctl start easun-ha.timer
```

4. **HA konfigurace** - viz `INSTALACE.md`

## Hotové pro produkci

Jakmile se vyřeší komunikace, všechno ostatní je připravené:
- ✓ MQTT odesílání
- ✓ JSON formát kompatibilní s HA  
- ✓ Systemd automatizace
- ✓ HA senzory definované
- ✓ Error handling a logování

**Problém je pouze v sériové komunikaci PC ↔ EASUN.**