#!/usr/bin/env python3
"""
Přímý test komunikace bez mpp-solar knihovny
"""
import serial
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

def create_command(cmd_str):
    """Create command with CRC"""
    cmd_bytes = cmd_str.encode('ascii')
    crc = crc16_xmodem(cmd_bytes)
    return cmd_bytes + crc.to_bytes(2, 'big') + b'\r'

def test_device(device_path, baud_rate=2400):
    """Test device communication"""
    print(f"\n🔌 Testing: {device_path} @ {baud_rate} baud")
    print("-" * 50)
    
    try:
        ser = serial.Serial(device_path, baud_rate, timeout=3)
        print(f"✅ Connected to {device_path}")
        
        # Clear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Test QPIGS command
        cmd = create_command('QPIGS')
        print(f"📤 Sending: QPIGS (hex: {cmd.hex()})")
        
        ser.write(cmd)
        time.sleep(1)
        
        response = ser.read(200)
        
        if response and len(response) > 10:
            print(f"📥 Response: {len(response)} bytes")
            print(f"🔧 Hex: {response[:20].hex()}")
            
            # Try to decode
            try:
                text = response.decode('ascii', errors='ignore')
                if '(' in text:
                    print(f"📊 Data: {text[:100]}")
                    return True
            except:
                pass
        else:
            print(f"❌ No valid response (got {len(response)} bytes)")
            
        ser.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

# Test all devices
devices = ['/dev/ttyUSB0', '/dev/hidraw0', '/dev/hidraw1', '/dev/hidraw2']
baud_rates = [2400, 9600]

print("🔌 MPP Solar Direct Communication Test")
print("=" * 70)

# Test USB serial first
for baud in baud_rates:
    if test_device('/dev/ttyUSB0', baud):
        print("\n✅ SUCCESS! Working configuration found!")
        break

# Test HID devices if USB failed
for device in ['/dev/hidraw0', '/dev/hidraw1', '/dev/hidraw2']:
    try:
        # For HID devices, we need different approach
        print(f"\n🔌 Testing HID: {device}")
        print("-" * 50)
        
        with open(device, 'r+b', buffering=0) as hid:
            print(f"✅ Opened: {device}")
            
            # Send QPIGS command
            cmd = b'QPIGS\xb7\xa9\r'
            print(f"📤 Sending: QPIGS")
            
            hid.write(cmd)
            time.sleep(1)
            
            response = hid.read(200)
            if response and len(response) > 10:
                print(f"📥 Response: {len(response)} bytes")
                print(f"🔧 Hex: {response[:20].hex()}")
                print("\n✅ SUCCESS! HID device responds!")
                break
                
    except Exception as e:
        print(f"❌ Error: {e}")