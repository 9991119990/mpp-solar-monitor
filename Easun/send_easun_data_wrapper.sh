#!/bin/bash
# EASUN Data Sender using wrapper (backup if mpp-solar doesn't work)

PYTHON_CMD="/home/dell/Měniče/Easun/easun_wrapper.py"
MOSQUITTO_PUB_CMD="/usr/bin/mosquitto_pub"
MQTT_BROKER="192.168.68.250"  # Replace with your HA IP
MQTT_PORT="1883"
MQTT_USER="your_ha_user"      # Replace with your HA username  
MQTT_PASS="your_ha_password"  # Replace with your HA password
MQTT_TOPIC="easun/inverter/QPIGS"

echo "EASUN Data Sender (Wrapper Version)"
echo "====================================="

if [ ! -f "$PYTHON_CMD" ]; then 
    echo "Error: Wrapper script not found"
    exit 1
fi

if [ ! -x "$MOSQUITTO_PUB_CMD" ]; then 
    echo "Error: mosquitto_pub not found"
    exit 1
fi

# Get data from EASUN
echo "Reading data from EASUN..."
JSON_DATA=$(python3 "$PYTHON_CMD")

if [[ -z "$JSON_DATA" || "${JSON_DATA:0:1}" != "{" ]]; then
   echo "Error: Failed to get JSON from EASUN."
   echo "Response: $JSON_DATA"
   exit 1
fi

echo "Data received: $JSON_DATA"

# Send to MQTT
echo "Sending to MQTT..."
echo "$JSON_DATA" | $MOSQUITTO_PUB_CMD -h $MQTT_BROKER -p $MQTT_PORT -u $MQTT_USER -P "$MQTT_PASS" -t "$MQTT_TOPIC" -l

if [ $? -eq 0 ]; then 
    echo "✓ Data sent successfully."
else 
    echo "✗ MQTT publish failed."
    exit 1
fi

exit 0