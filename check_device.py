#!/usr/bin/env python3
"""
Kontrola zařízení a návod na oprávnění
"""
import os
import subprocess

print("🔌 MPP Solar - Kontrola připojení")
print("=" * 70)

# Najdeme USB zařízení
print("\n📱 USB zařízení:")
result = subprocess.run(['lsusb'], capture_output=True, text=True)
for line in result.stdout.splitlines():
    if 'Cypress' in line or '0665:5161' in line:
        print(f"✅ NALEZEN MĚNIČ: {line}")

# Zkontrolujeme hidraw zařízení
print("\n📁 HID zařízení:")
hidraw_devices = []
for i in range(5):
    device = f'/dev/hidraw{i}'
    if os.path.exists(device):
        stat = os.stat(device)
        perms = oct(stat.st_mode)[-3:]
        print(f"   {device} - oprávnění: {perms}")
        hidraw_devices.append(device)

# Najdeme správné zařízení
print("\n🔍 Hledám měnič...")
device_found = None
for device in hidraw_devices:
    if device == '/dev/hidraw2':  # Podle dokumentace
        device_found = device
        print(f"✅ Pravděpodobný měnič: {device}")
        break

if device_found:
    print(f"\n⚙️ Instrukce pro zprovoznění:")
    print(f"1. Nastavte oprávnění (vyžaduje sudo heslo):")
    print(f"   sudo chmod 666 {device_found}")
    print(f"\n2. Pak spusťte test:")
    print(f"   python3 show_current_data.py")
    print(f"\n3. Nebo rychlý monitor:")
    print(f"   python3 quick_monitor.py")
    
    # Ukážeme jak vypadá správná komunikace
    print(f"\n📊 Očekávaný výstup při funkční komunikaci:")
    print("   AC Output: 230.0V @ 50.0Hz")
    print("   Battery: 54.0V 68%")
    print("   PV Input: 250.0V 800W")
    print("   Temperature: 49°C")
else:
    print("❌ Měnič nebyl nalezen!")