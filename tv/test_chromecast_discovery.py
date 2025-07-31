#!/usr/bin/env python3
"""Test Chromecast discovery and basic control functionality"""

import time
import pychromecast
import zeroconf


def test_discovery():
    """Test Chromecast discovery"""
    print("🔍 Starting Chromecast discovery...")
    
    # Create discovery browser
    zconf = zeroconf.Zeroconf()
    browser = pychromecast.CastBrowser(
        pychromecast.SimpleCastListener(
            lambda uuid, service: print(f"Found: {browser.devices[uuid].friendly_name}")
        ), 
        zconf
    )
    
    browser.start_discovery()
    
    # Let it run for a few seconds
    print("⏱️ Discovering for 10 seconds...")
    time.sleep(10)
    
    # Show all discovered devices
    print(f"\n📺 Discovered {len(browser.devices)} device(s):")
    for uuid, device in browser.devices.items():
        print(f"  • {device.friendly_name} at {device.host}:{device.port}")
        print(f"    Model: {device.model_name}, Type: {device.cast_type}")
        print(f"    UUID: {uuid}")
        print()
    
    # Clean up
    pychromecast.discovery.stop_discovery(browser)
    zconf.close()
    
    return list(browser.devices.values())


def test_connection(devices):
    """Test connection to first discovered device"""
    if not devices:
        print("❌ No devices found to test connection")
        return None
    
    device = devices[0]
    print(f"🔗 Testing connection to: {device.friendly_name}")
    
    try:
        # Get chromecast by friendly name
        chromecasts, browser = pychromecast.get_listed_chromecasts(
            friendly_names=[device.friendly_name]
        )
        
        if not chromecasts:
            print("❌ Could not connect to device")
            return None
        
        cast = chromecasts[0]
        
        # Wait for connection
        print("⏳ Waiting for cast device to be ready...")
        cast.wait()
        
        print("✅ Connected successfully!")
        print(f"📊 Cast info: {cast.cast_info}")
        print(f"📊 Status: {cast.status}")
        
        # Test media controller
        mc = cast.media_controller
        print(f"📊 Media status: {mc.status}")
        
        # Clean up
        pychromecast.discovery.stop_discovery(browser)
        
        return cast
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None


def test_basic_control(cast):
    """Test basic playback control"""
    if not cast:
        print("❌ No cast device to test")
        return
    
    print("\n🎮 Testing basic control...")
    mc = cast.media_controller
    
    # Test loading a sample video
    sample_url = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    
    try:
        print(f"📺 Loading sample video: {sample_url}")
        mc.play_media(sample_url, 'video/mp4')
        mc.block_until_active()
        
        print("✅ Video loaded successfully!")
        print(f"📊 Media status: {mc.status}")
        
        # Test pause/play
        print("⏸️ Testing pause...")
        mc.pause()
        time.sleep(2)
        
        print("▶️ Testing play...")
        mc.play()
        time.sleep(2)
        
        # Test seek
        print("⏭️ Testing seek to 30 seconds...")
        mc.seek(30)
        time.sleep(2)
        
        print(f"📊 Final status: {mc.status}")
        
        # Leave it playing for demo
        print("💡 Left video playing for further testing")
        
    except Exception as e:
        print(f"❌ Control test failed: {e}")


def main():
    """Run all tests"""
    print("🧪 Chromecast Discovery & Control Test")
    print("=" * 50)
    
    # Test discovery
    devices = test_discovery()
    
    if not devices:
        print("❌ No Chromecasts found. Check that:")
        print("  • Chromecast is powered on and connected to same network")
        print("  • Network allows multicast/discovery (not guest network)")
        print("  • No firewall blocking discovery")
        return
    
    # Test connection
    cast = test_connection(devices)
    
    # Test basic control
    test_basic_control(cast)
    
    print("\n✅ Testing complete!")


if __name__ == "__main__":
    main()
