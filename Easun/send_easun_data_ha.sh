#!/bin/bash
# Send EASUN data to Home Assistant via MQTT
# For use on Raspberry Pi running Home Assistant

# Python environment (adjust if needed)
PYTHON_CMD="/usr/bin/python3"

# Script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SCRIPT_PATH="${SCRIPT_DIR}/easun_raspberry_ha.py"

# Serial port configuration
export EASUN_PORT="/dev/ttyUSB0"  # nebo /dev/ttyAMA0 pro GPIO serial

# MQTT configuration - ADJUST THESE!
export MQTT_BROKER="localhost"     # Pokud běží na stejném Raspberry Pi
export MQTT_PORT="1883"
export MQTT_USER="homeassistant"  # Váš HA uživatel
export MQTT_PASS="your_password"  # ZMĚŇTE na vaše HA heslo!
export MQTT_TOPIC="easun/inverter/QPIGS"

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Python script not found at $SCRIPT_PATH"
    exit 1
fi

# Check if serial device exists
if [ ! -e "$EASUN_PORT" ]; then
    echo "Error: Serial device $EASUN_PORT not found"
    echo "Available devices:"
    ls -la /dev/ttyUSB* /dev/ttyAMA* /dev/serial* 2>/dev/null || echo "No serial devices found"
    exit 1
fi

# Check permissions
if [ ! -r "$EASUN_PORT" ] || [ ! -w "$EASUN_PORT" ]; then
    echo "Error: No read/write permissions for $EASUN_PORT"
    echo "Current user: $(whoami)"
    echo "Groups: $(groups)"
    echo "Device permissions: $(ls -la $EASUN_PORT)"
    echo ""
    echo "Fix with: sudo usermod -a -G dialout $(whoami)"
    echo "Then logout and login again"
    exit 1
fi

# Run the Python script
$PYTHON_CMD "$SCRIPT_PATH" "$@"

# Check exit status
if [ $? -eq 0 ]; then
    echo "$(date): Data sent successfully"
else
    echo "$(date): Failed to send data"
    exit 1
fi