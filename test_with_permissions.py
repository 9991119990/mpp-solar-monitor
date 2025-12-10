#!/usr/bin/env python3
"""
Test komunikace s měničem s kontrolou oprávnění
"""
import os
import sys

# Kontrola oprávnění k hidraw2
device = '/dev/hidraw2'
print(f"🔌 MPP Solar Test - {device}")
print("=" * 50)

# Kontrola existence
if not os.path.exists(device):
    print(f"❌ Zařízení {device} neexistuje!")
    sys.exit(1)

# Kontrola oprávnění
if not os.access(device, os.R_OK | os.W_OK):
    print(f"❌ Nemáte oprávnění k {device}")
    print("✅ Řešení: Spusťte následující příkaz:")
    print(f"   sudo chmod 666 {device}")
    print("\nNebo můžete zkusit spustit originální skript:")
    print("   python3 show_current_data.py")
    sys.exit(1)

print(f"✅ Zařízení {device} je dostupné")

# Test komunikace
import time

def crc16_xmodem(data):
    """CRC16 XMODEM calculation"""
    crc = 0x0000
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

print("\n📤 Posílám QPIGS příkaz...")

try:
    with open(device, 'r+b', buffering=0) as hid:
        # Create QPIGS command
        cmd = b'QPIGS'
        crc = crc16_xmodem(cmd)
        packet = cmd + crc.to_bytes(2, 'big') + b'\r'
        
        print(f"📦 Packet: {packet.hex()}")
        
        # Send command
        hid.write(packet)
        time.sleep(1)
        
        # Read response
        response = hid.read(200)
        
        if response and len(response) > 10:
            print(f"\n📥 Odpověď: {len(response)} bytů")
            print(f"🔧 Hex: {response[:20].hex()}")
            
            # Try decode
            try:
                text = response.decode('ascii', errors='ignore')
                if '(' in text:
                    print(f"\n✅ ÚSPĚCH! Měnič komunikuje!")
                    print(f"📊 Data: {text}")
                    
                    # Parse some values
                    if text.startswith('('):
                        values = text.strip('()\r\n').split()
                        if len(values) > 10:
                            print(f"\n🔋 Rychlý přehled:")
                            print(f"   AC Output: {values[4]}V @ {values[5]}Hz")
                            print(f"   Battery: {values[10]}V")
                            print(f"   PV Input: {values[12]}V")
                            print(f"   Temperature: {values[11]}°C")
            except:
                pass
        else:
            print(f"❌ Žádná nebo krátká odpověď ({len(response)} bytů)")
            
except Exception as e:
    print(f"❌ Chyba: {e}")