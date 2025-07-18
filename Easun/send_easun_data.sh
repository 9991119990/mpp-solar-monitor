#!/bin/bash
VENV_PATH="/home/dell/Měniče/Easun/venv"
MPP_SOLAR_CMD="${VENV_PATH}/bin/mpp-solar"
MOSQUITTO_PUB_CMD="/usr/bin/mosquitto_pub"
DEVICE="/dev/ttyUSB0"
PROTOCOL="PI30"
BAUD_RATE="2400"
MQTT_BROKER="192.168.68.250" # IP adresa HA
MQTT_PORT="1883"
MQTT_USER="dell" # HA uživatelské jméno - ZMĚŇ 
MQTT_PASS="tvoje_heslo" # <--- DŮLEŽITÉ: Nahraď tvým HA heslem!
MQTT_TOPIC="easun/inverter/QPIGS"

if [ ! -f "$MPP_SOLAR_CMD" ]; then 
    echo "Error: mpp-solar not found"
    exit 1
fi

if [ ! -x "$MOSQUITTO_PUB_CMD" ]; then 
    echo "Error: mosquitto_pub not found"
    exit 1
fi

source "${VENV_PATH}/bin/activate"
if [ $? -ne 0 ]; then 
    echo "Error: Failed to activate venv"
    exit 1
fi

JSON_DATA=$($MPP_SOLAR_CMD -p $DEVICE -P $PROTOCOL -b $BAUD_RATE -c QPIGS -o json_units)

if [[ -z "$JSON_DATA" || "${JSON_DATA:0:1}" != "{" ]]; then
   echo "Chyba: Nepodařilo se získat JSON z mpp-solar."
   deactivate
   exit 1
fi

echo "Data received: $JSON_DATA"

echo "$JSON_DATA" | $MOSQUITTO_PUB_CMD -h $MQTT_BROKER -p $MQTT_PORT -u $MQTT_USER -P "$MQTT_PASS" -t "$MQTT_TOPIC" -l
if [ $? -eq 0 ]; then 
    echo "Data odeslána."
else 
    echo "Chyba mosquitto_pub."
fi

deactivate
exit 0