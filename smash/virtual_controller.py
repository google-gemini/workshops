import random
import signal
import sys
import time

import uinput
from absl import app, logging

BUTTONS = [
    uinput.BTN_A,
    uinput.BTN_B,
    uinput.BTN_X,
    uinput.BTN_Y,
    uinput.BTN_TL,
    uinput.BTN_TR,
    uinput.BTN_SELECT,
    uinput.BTN_START,
    uinput.BTN_THUMBL,
    uinput.BTN_THUMBR,
]

AXES = [
    (uinput.ABS_X, (0, 255, 0, 0)),
    (uinput.ABS_Y, (0, 255, 0, 0)),
]

held_buttons = {}


def build_device(name="gemma"):
    logging.info("Building device with name: %s", name)
    events = BUTTONS + [axis + params for axis, params in AXES]
    return uinput.Device(events, name=name)


def reset_device(device):
    logging.info("Resetting device")
    for axis, (min_val, max_val, *_rest) in AXES:
        center = (min_val + max_val) // 2
        logging.info("Resetting axis %s to center value %d", axis, center)
        device.emit(axis, center, syn=False)
    for btn in BUTTONS:
        logging.info("Resetting button %s to 0", btn)
        device.emit(btn, 0, syn=False)
    device.syn()


def run_event_loop(device):
    logging.info("Starting event loop")
    try:
        while True:
            if random.random() < 0.7:
                btn = random.choice(BUTTONS)
                if btn in held_buttons:
                    if held_buttons[btn] > 0:
                        held_buttons[btn] -= 1
                    else:
                        logging.info("Releasing button %s", btn)
                        device.emit(btn, 0)
                        del held_buttons[btn]
                else:
                    if random.random() < 0.5:
                        logging.info("Pressing button %s", btn)
                        device.emit(btn, 1)
                        held_buttons[btn] = random.randint(2, 5)
            else:
                axis, (min_val, max_val, *_rest) = random.choice(AXES)
                val = random.randint(min_val, max_val)
                logging.info("Moving axis %s to value %d", axis, val)
                device.emit(axis, val)
            # Slow down the script by increasing the sleep duration
            time.sleep(random.uniform(0.3, 2.0))
    finally:
        reset_device(device)


def main(argv):
    del argv
    logging.info("Setting up signal handlers")
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    try:
        with build_device() as dev:
            logging.info("Device built, sleeping for 1.5 seconds")
            time.sleep(1.5)
            run_event_loop(dev)
    except OSError as e:
        logging.error("uinput error: %s", e)
        logging.error("Try: sudo modprobe uinput && sudo chmod 666 /dev/uinput")
        sys.exit(1)


if __name__ == "__main__":
    app.run(main)
