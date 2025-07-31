#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple controller passthrough daemon for Wind Waker voice chat.

Forwards physical controller inputs to a virtual controller and
accepts JSON commands over socket for LLM actuation.

Run with: sudo python controller_daemon.py
"""

import json
import socket
import threading
import time
from evdev import InputDevice, categorize, ecodes, list_devices
import uinput

# GameCube controller mapping for Wind Waker
# Updated for Xbox-style controller mapping
GC_MAPPING = {
    # Face buttons
    'A': uinput.BTN_A,
    'B': uinput.BTN_B,
    'X': uinput.BTN_X,
    'Y': uinput.BTN_Y,
    # D-pad (might need to use HAT axes instead)
    'UP': uinput.BTN_DPAD_UP,
    'DOWN': uinput.BTN_DPAD_DOWN,
    'LEFT': uinput.BTN_DPAD_LEFT,
    'RIGHT': uinput.BTN_DPAD_RIGHT,
    # Shoulders - GameCube style
    'L': uinput.ABS_Z,  # Analog left trigger
    'R': uinput.ABS_RZ,  # Analog right trigger
    'Z': uinput.BTN_TR,  # Digital Z button
    # Keep these for compatibility
    'LT': uinput.ABS_Z,  # Left trigger (same as L)
    'RT': uinput.ABS_RZ,  # Right trigger (same as R)
    # Control stick
    'STICK_X': uinput.ABS_X,
    'STICK_Y': uinput.ABS_Y,
    # C-stick/Right stick
    'C_X': uinput.ABS_RX,
    'C_Y': uinput.ABS_RY,
    # Start/Select
    'START': uinput.BTN_START,
    'SELECT': uinput.BTN_SELECT,
}


class DumbControllerProxy:

  def __init__(self, physical_device_path=None):
    # Threading and connection state
    self.physical = None
    self.physical_lock = threading.Lock()
    self.should_stop = threading.Event()

    # Create virtual controller with all possible inputs
    events = [
        # Buttons
        uinput.BTN_A,
        uinput.BTN_B,
        uinput.BTN_X,
        uinput.BTN_Y,
        uinput.BTN_DPAD_UP,
        uinput.BTN_DPAD_DOWN,
        uinput.BTN_DPAD_LEFT,
        uinput.BTN_DPAD_RIGHT,
        uinput.BTN_TL,
        uinput.BTN_TR,
        uinput.BTN_TR2,
        uinput.BTN_START,
        uinput.BTN_SELECT,
        # Analog sticks (0-255 range)
        uinput.ABS_X + (0, 255, 0, 0),
        uinput.ABS_Y + (0, 255, 0, 0),
        uinput.ABS_RX + (0, 255, 0, 0),
        uinput.ABS_RY + (0, 255, 0, 0),
        # Analog triggers (0-255 range)
        uinput.ABS_Z + (0, 255, 0, 0),  # L trigger
        uinput.ABS_RZ + (0, 255, 0, 0),  # R trigger
        # HAT axes for D-pad (-1 to 1 range)
        uinput.ABS_HAT0X + (-1, 1, 0, 0),
        uinput.ABS_HAT0Y + (-1, 1, 0, 0),
    ]

    print('Creating virtual controller...')
    self.virtual = uinput.Device(events, name='WindWaker-Virtual')

    # Initialize all inputs to neutral state
    print('Zeroing out all inputs...')
    # Reset all buttons to unpressed
    for button_name, button_code in GC_MAPPING.items():
      if button_name.endswith('_X') or button_name.endswith('_Y'):
        continue  # Skip axes in this loop
      try:
        self.virtual.emit(button_code, 0)
      except:
        pass  # Some mappings might not be buttons

    # Reset axes to center (128 is center for 0-255 range)
    self.virtual.emit(uinput.ABS_X, 128)
    self.virtual.emit(uinput.ABS_Y, 128)
    self.virtual.emit(uinput.ABS_RX, 128)
    self.virtual.emit(uinput.ABS_RY, 128)
    # Reset triggers to unpressed (0)
    self.virtual.emit(uinput.ABS_Z, 0)
    self.virtual.emit(uinput.ABS_RZ, 0)
    self.virtual.syn()  # Sync all changes

    # Small delay to ensure RetroArch samples the neutral state
    time.sleep(0.1)
    print('Controller initialized to neutral state')

    # Start connection manager thread
    self.connection_thread = threading.Thread(
        target=self.connection_manager, daemon=True
    )
    self.connection_thread.start()
    print('Connection manager started')

  def find_controller(self):
    """Find a game controller device"""
    try:
      devices = [InputDevice(path) for path in list_devices()]
      for device in devices:
        # Look for common controller names
        if any(
            name in device.name.lower()
            for name in [
                'controller',
                'gamepad',
                'joystick',
                'nintendo',
                'gamecube',
            ]
        ):
          return device
    except Exception as e:
      print(f'Error finding controller: {e}')
    return None

  def connection_manager(self):
    """Continuously manage controller connection state"""
    while not self.should_stop.is_set():
      with self.physical_lock:
        if self.physical is None:
          # Try to connect
          print('Searching for controller...')
          controller = self.find_controller()
          if controller:
            self.physical = controller
            print(f'✓ Connected to: {controller.name}')
          else:
            # Don't spam the console too much
            pass
        else:
          # Check if still connected
          try:
            # Try to read device info to check connection
            _ = self.physical.name
          except (OSError, AttributeError):
            print('✗ Controller disconnected!')
            self.physical = None
            continue

      # Sleep longer when no controller to reduce CPU usage
      if self.physical is None:
        time.sleep(3)
      else:
        time.sleep(0.5)

  def passthrough_thread(self):
    """Forward all events from physical to virtual controller"""
    print('Starting controller passthrough...')

    # Create mapping for axes we care about
    axis_map = {
        ecodes.ABS_X: uinput.ABS_X,
        ecodes.ABS_Y: uinput.ABS_Y,
        # Right stick - no swap, direct mapping
        ecodes.ABS_RX: uinput.ABS_RX,
        ecodes.ABS_RY: uinput.ABS_RY,
        # Analog triggers
        ecodes.ABS_Z: uinput.ABS_Z,  # L trigger
        ecodes.ABS_RZ: uinput.ABS_RZ,  # R trigger
        # Add HAT axes for D-pad
        ecodes.ABS_HAT0X: uinput.ABS_HAT0X,
        ecodes.ABS_HAT0Y: uinput.ABS_HAT0Y,
    }

    # Button mapping - evdev to uinput
    # Updated for Xbox-style mapping
    button_map = {}
    for name in [
        'BTN_A',
        'BTN_B',
        'BTN_X',
        'BTN_Y',
        'BTN_TL',
        'BTN_TR',
        'BTN_TL2',
        'BTN_TR2',
        'BTN_START',
        'BTN_SELECT',
    ]:
      if hasattr(ecodes, name) and hasattr(uinput, name):
        button_map[getattr(ecodes, name)] = getattr(uinput, name)

    # Track what we've seen for diagnostics
    seen_axes = set()
    seen_buttons = set()

    while not self.should_stop.is_set():
      # Get current controller with lock
      with self.physical_lock:
        device = self.physical

      if not device:
        time.sleep(0.1)  # Wait for connection
        continue

      try:
        # Read events from the controller
        for event in device.read_loop():
          # Check if we should stop
          if self.should_stop.is_set():
            break
          # Skip sync events
          if event.type == ecodes.EV_SYN:
            continue

          # Log ALL axis events for diagnostics
          if event.type == ecodes.EV_ABS:
            if event.code not in seen_axes:
              seen_axes.add(event.code)
              # Find the name of this axis
              axis_name = 'UNKNOWN'
              for name in dir(ecodes):
                if (
                    name.startswith('ABS_')
                    and getattr(ecodes, name) == event.code
                ):
                  axis_name = name
                  break
              print(f'NEW AXIS DISCOVERED: {axis_name} (code={event.code})')


            if event.code in axis_map:
              # Convert from signed range to 0-255
              absinfo = self.physical.absinfo(event.code)
              min_val = absinfo.min
              max_val = absinfo.max

              # Special handling for HAT (D-pad) - it's usually -1, 0, 1
              if event.code in [ecodes.ABS_HAT0X, ecodes.ABS_HAT0Y]:
                # HAT axes should pass through directly as -1, 0, 1
                hat_axis_name = (
                    'HAT0X' if event.code == ecodes.ABS_HAT0X else 'HAT0Y'
                )
                print(f'HAT {hat_axis_name}: {event.value} (raw)')
                self.virtual.emit(axis_map[event.code], event.value)
              else:
                # Normal axis mapping
                normalized = (event.value - min_val) / (max_val - min_val)
                uinput_value = int(normalized * 255)
                uinput_value = max(0, min(255, uinput_value))


                self.virtual.emit(axis_map[event.code], uinput_value)

          # Log ALL button events for diagnostics
          elif event.type == ecodes.EV_KEY:
            if event.code not in seen_buttons:
              seen_buttons.add(event.code)
              # Find the name of this button
              button_name = 'UNKNOWN'
              for name in dir(ecodes):
                if (
                    name.startswith('BTN_')
                    and getattr(ecodes, name) == event.code
                ):
                  button_name = name
                  break
              print(f'NEW BUTTON DISCOVERED: {button_name} (code={event.code})')

            if event.code in button_map:
              self.virtual.emit(button_map[event.code], event.value)
              # Find button name for clearer logging
              button_name = 'UNKNOWN'
              for name, code in button_map.items():
                if code == button_map[event.code]:
                  for btn_name in dir(ecodes):
                    if getattr(ecodes, btn_name, None) == event.code:
                      button_name = btn_name
                      break
                  break
              print(f'Button {button_name}: {event.value}')
            else:
              print(f'Unmapped button: code={event.code}, value={event.value}')

      except OSError as e:
        # Device disconnected, connection manager will handle reconnection
        with self.physical_lock:
          self.physical = None
        print(f'Controller read error: {e}')
        time.sleep(0.5)
      except Exception as e:
        print(f'Passthrough error: {e}')
        import traceback

        traceback.print_exc()
        time.sleep(1)

  def command_server(self, port=9999):
    """Accept JSON commands and execute immediately"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', port))
    server.listen(1)
    print(f'Command server listening on port {port}')

    while True:
      try:
        conn, addr = server.accept()
        data = conn.recv(4096)

        if data:
          cmd = json.loads(data.decode())
          self.execute_command(cmd)

        conn.close()
      except Exception as e:
        print(f'Command server error: {e}')

  def execute_command(self, cmd):
    """Execute a controller command"""
    try:
      if cmd['type'] == 'button':
        button_code = GC_MAPPING.get(cmd['button'])
        if button_code:
          self.virtual.emit(button_code, cmd['value'])
          print(f"Button {cmd['button']} = {cmd['value']}")
      elif cmd['type'] == 'axis':
        axis_code = GC_MAPPING.get(cmd['axis'])
        if axis_code:
          self.virtual.emit(axis_code, cmd['value'])
          print(f"Axis {cmd['axis']} = {cmd['value']}")
      self.virtual.syn()  # Sync events
    except Exception as e:
      print(f'Command execution error: {e}')

  def run(self):
    """Run both passthrough and command server"""
    # Start passthrough in background thread
    passthrough = threading.Thread(target=self.passthrough_thread, daemon=True)
    passthrough.start()

    # Run command server in main thread
    try:
      self.command_server()
    except KeyboardInterrupt:
      print('\nShutting down controller daemon...')
      self.should_stop.set()
      time.sleep(0.5)  # Give threads time to clean up


if __name__ == '__main__':
  print('Wind Waker Controller Daemon')
  print('Make sure to run with sudo for /dev/uinput access')

  proxy = DumbControllerProxy()
  proxy.run()
