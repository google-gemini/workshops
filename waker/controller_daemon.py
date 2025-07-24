#!/usr/bin/env python3
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
    # Shoulders - Xbox style
    'L': uinput.BTN_TL,  # Left bumper (LB)
    'R': uinput.BTN_TR,  # Right bumper (RB)
    'Z': uinput.BTN_TR,  # Map Z to RB as requested
    'LT': uinput.BTN_TL2,  # Left trigger
    'RT': uinput.BTN_TR2,  # Right trigger
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
        # Analog sticks (0-255 range)
        uinput.ABS_X + (0, 255, 0, 0),
        uinput.ABS_Y + (0, 255, 0, 0),
        uinput.ABS_RX + (0, 255, 0, 0),
        uinput.ABS_RY + (0, 255, 0, 0),
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
    self.virtual.syn()  # Sync all changes

    # Small delay to ensure RetroArch samples the neutral state
    time.sleep(0.1)
    print('Controller initialized to neutral state')

    # Find physical controller
    if physical_device_path:
      self.physical = InputDevice(physical_device_path)
    else:
      self.physical = self.find_controller()

    if self.physical:
      print(f'Found controller: {self.physical.name}')
    else:
      print('Warning: No physical controller found, LLM-only mode')

  def find_controller(self):
    """Find a game controller device"""
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
    return None

  def passthrough_thread(self):
    """Forward all events from physical to virtual controller"""
    if not self.physical:
      return

    print('Starting controller passthrough...')
    print('DIAGNOSTIC MODE: Logging all events to identify mappings')

    # Create mapping for axes we care about
    axis_map = {
        ecodes.ABS_X: uinput.ABS_X,
        ecodes.ABS_Y: uinput.ABS_Y,
        # Right stick - no swap, direct mapping
        ecodes.ABS_RX: uinput.ABS_RY,
        ecodes.ABS_RY: uinput.ABS_RX,
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

    while True:  # Keep trying to reconnect
      try:
        print(f'Connected to {self.physical.name}')

        for event in self.physical.read_loop():
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

            # Always log for now to debug right stick
            if event.code in [
                ecodes.ABS_RX,
                ecodes.ABS_RY,
                ecodes.ABS_Z,
                ecodes.ABS_RZ,
            ]:
              print(
                  f'Right stick/trigger axis: code={event.code},'
                  f' value={event.value}'
              )

            if event.code in axis_map:
              # Convert from signed range to 0-255
              absinfo = self.physical.absinfo(event.code)
              min_val = absinfo.min
              max_val = absinfo.max

              # Special handling for HAT (D-pad) - it's usually -1, 0, 1
              if event.code in [ecodes.ABS_HAT0X, ecodes.ABS_HAT0Y]:
                # Map -1 to 0, 0 to 128, 1 to 255
                if event.value < 0:
                  uinput_value = 0
                elif event.value > 0:
                  uinput_value = 255
                else:
                  uinput_value = 128
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
            print(f'Button: code={event.code}, value={event.value}')

      except OSError as e:
        if e.errno == 19:  # No such device
          print(f'Controller disconnected: {e}')
          print('Waiting for reconnection...')
          time.sleep(2)

          # Try to find and reconnect to controller
          self.physical = self.find_controller()
          if not self.physical:
            print('No controller found, retrying...')
            time.sleep(3)
            continue
        else:
          print(f'Unexpected error: {e}')
          import traceback

          traceback.print_exc()
          time.sleep(5)
      except Exception as e:
        print(f'Passthrough error: {e}')
        import traceback

        traceback.print_exc()
        time.sleep(5)

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
    if self.physical:
      passthrough = threading.Thread(
          target=self.passthrough_thread, daemon=True
      )
      passthrough.start()

    # Run command server in main thread
    try:
      self.command_server()
    except KeyboardInterrupt:
      print('\nShutting down controller daemon...')


if __name__ == '__main__':
  print('Wind Waker Controller Daemon')
  print('Make sure to run with sudo for /dev/uinput access')

  proxy = DumbControllerProxy()
  proxy.run()
