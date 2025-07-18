#!/bin/bash
# Test serial communication with EASUN inverter

PORT="/dev/ttyUSB0"

echo "Setting up serial port..."
stty -F $PORT 2400 cs8 -cstopb -parenb -echo raw

echo "Sending QPIGS command..."
# Send QPIGS with CRC
printf '\x51\x50\x49\x47\x53\xB7\xA9\x0D' > $PORT

echo "Waiting for response..."
sleep 2

echo "Reading response..."
timeout 3 cat $PORT | od -x

echo "Done."