import random
import signal
import sys
import time

import uinput

# Define buttons - these are event codes that will be used directly
# These should be available in the uinput module.
BUTTONS = (
    uinput.BTN_A,
    uinput.BTN_B,
    uinput.BTN_X,
    uinput.BTN_Y,
    uinput.BTN_TL,  # L1 / LB
    uinput.BTN_TR,  # R1 / RB
    uinput.BTN_SELECT,
    uinput.BTN_START,
    uinput.BTN_THUMBL,  # Left stick click
    uinput.BTN_THUMBR,  # Right stick click
)

# Define axes specifications: (event_code, (min_value, max_value, fuzz, flat))
# This structure is for our logic. The device setup will transform it.
AXES_SPECS = (
    (uinput.ABS_X, (0, 255, 0, 0)),  # Left stick X
    (uinput.ABS_Y, (0, 255, 0, 0)),  # Left stick Y
    # Example: Add right stick
    # (uinput.ABS_RX, (0, 255, 0, 0)), # Right stick X
    # (uinput.ABS_RY, (0, 255, 0, 0)), # Right stick Y
)


def reset_device_state(device, buttons_list, axes_specs_list):
    """Resets all buttons to released and axes to center."""
    if not device:
        return
    try:
        print("Resetting controller state...")
        # Center axes
        for axis_code, params in axes_specs_list:
            min_val, max_val, _, _ = params
            center_val = (min_val + max_val) // 2
            device.emit(axis_code, center_val, syn=False)
        # Release all buttons
        for btn_code in buttons_list:
            device.emit(btn_code, 0, syn=False)  # 0 for release

        device.syn()  # Synchronize all state changes at once
        print("Controller state reset and synced.")
        time.sleep(0.05)  # Small delay for states to propagate
    except Exception as e:
        print(f"Error during device state reset: {e}", file=sys.stderr)


def run_controller_loop(device):
    """Runs the main loop of emitting random controller events."""
    try:
        print("Starting event loop. Press Ctrl+C to exit.")
        while True:
            # Choose event type: 70% chance button, 30% chance axis
            if random.random() < 0.7:  # Button event
                if BUTTONS:  # Ensure there are buttons defined
                    button_to_affect = random.choice(BUTTONS)
                    action = random.choice([0, 1])  # 0 for release, 1 for press
                    device.emit(button_to_affect, action)
                    # print(f"Button: {button_to_affect} Action: {action}")
            else:  # Axis event
                if AXES_SPECS:  # Ensure there are axes defined
                    axis_code, params = random.choice(AXES_SPECS)
                    min_val, max_val, _, _ = params
                    value = random.randint(min_val, max_val)
                    device.emit(axis_code, value)
                    # print(f"Axis: {axis_code} Value: {value}")

            # python-uinput's emit() syncs by default (syn=True)
            # No explicit device.syn() needed here for individual events.

            sleep_duration = random.uniform(0.03, 0.20)
            time.sleep(sleep_duration)
            # print(f"Slept for {sleep_duration:.2f}s")

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received in loop. Shutting down...")
        # sys.exit() will be called by the signal handler, or this will propagate up
    finally:
        # This finally block ensures state reset even if loop breaks unexpectedly
        # (though KeyboardInterrupt is handled by signal handler primarily)
        reset_device_state(device, BUTTONS, AXES_SPECS)


def main():
    # Prepare the events tuple for uinput.Device constructor
    # Buttons are added directly.
    # Axes are added as `uinput.ABS_X + (min, max, fuzz, flat)`.
    device_event_capabilities = []
    device_event_capabilities.extend(BUTTONS)
    for axis_code, params_tuple in AXES_SPECS:
        device_event_capabilities.append(axis_code + params_tuple)

    events_tuple = tuple(device_event_capabilities)

    if not events_tuple:
        print("No buttons or axes defined. Exiting.", file=sys.stderr)
        sys.exit(1)

    # Signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print(f"\nSignal {sig} received. Initiating shutdown procedure...")
        # The 'finally' block associated with the 'with uinput.Device'
        # or the 'finally' in run_controller_loop will execute due to sys.exit()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        print("Attempting to create virtual gamepad...")
        name = "Python Virtual Gamepad"
        with uinput.Device(events_tuple, name=name) as device:
            print(f"Virtual gamepad created successfully: {name}")

            # Brief pause for the system to recognize the new device
            time.sleep(1.5)

            run_controller_loop(device)  # Contains its own try/finally for state reset

    except OSError as e:
        print(f"OSError: {e}.", file=sys.stderr)
        print(
            "This might be a permissions issue with /dev/uinput, or the 'uinput'" " kernel module may not be loaded.",
            file=sys.stderr,
        )
        print(
            "Try: sudo modprobe uinput && sudo chmod 666 /dev/uinput",
            file=sys.stderr,
        )
        sys.exit(1)
    except SystemExit:  # Caught when sys.exit() is called by signal_handler
        print("Shutdown initiated by SystemExit. Device cleanup should have occurred.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # This outer finally is mostly for messages post-exit or if 'with' failed early.
        # Device destruction is handled by the 'with' statement.
        # State reset is handled by run_controller_loop's finally.
        print("Application cleanup finished. Exiting.")


if __name__ == "__main__":
    main()
