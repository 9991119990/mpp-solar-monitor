# EASUN SHM II 7K - Řešení problémů s komunikací

## Současný stav
- USB-RS232 adaptér funguje (vidíme /dev/ttyUSB0)
- Uživatel je ve skupině dialout ✓
- Příkazy se odesílají, ale nedostáváme odpověď

## Kontrolní seznam

### 1. Fyzické připojení
Podle návodu potřebuješ:
- **Měnič**: EASUN SHM II 7K s RJ45 COMM portem
- **Kabel**: RJ45 na DB9 samici (female) - ideálně od WiFi loggeru
- **Převodník**: USB na RS232 s DB9 samcem (male)

Zapojení:
```
Měnič [RJ45] -> Kabel [RJ45-DB9F] -> Převodník [DB9M-USB] -> PC [USB]
```

### 2. Pinout RJ45 COMM portu
Podle manuálu:
- Pin 1: TX (měnič vysílá)
- Pin 2: RX (měnič přijímá)  
- Pin 7/8: GND

### 3. Kabel musí být "křížený" (Null Modem)
- RJ45 pin 1 (Měnič TX) -> DB9 pin 2 (PC RX)
- RJ45 pin 2 (Měnič RX) -> DB9 pin 3 (PC TX)
- RJ45 pin 7/8 (GND) -> DB9 pin 5 (GND)

### 4. Co zkontrolovat

1. **Je měnič zapnutý?**
   - Musí být v normálním provozním režimu
   - Některé měniče nekomunikují v standby

2. **Správný kabel?**
   - Pokud používáš kabel od WiFi loggeru, měl by být OK
   - Jinak potřebuješ null modem / křížený kabel

3. **Test kabelu**
   - Můžeš použít multimetr pro kontrolu propojení pinů
   - Nebo zkusit jiný kabel

4. **Nastavení měniče**
   - Některé měniče mají v menu nastavení komunikace
   - Zkontroluj zda není komunikace vypnutá

### 5. Alternativní test
Pokud máš přístup k Windows PC, můžeš zkusit:
- Oficiální software od EASUN
- Nebo jiný terminal program (PuTTY, RealTerm)

### 6. Další kroky
1. Zkontroluj fyzické připojení podle bodů výše
2. Ověř že používáš správný kabel (křížený/null modem)
3. Zkus jiný USB port
4. Restartuj měnič (vypni/zapni)

## Až bude komunikace fungovat
Skript `send_easun_data.sh` je připravený, stačí:
1. Upravit MQTT přihlašovací údaje
2. Spustit: `./send_easun_data.sh`