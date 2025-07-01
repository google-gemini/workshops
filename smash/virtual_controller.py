import base64
import os
import queue
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from textwrap import dedent
from typing import Callable

import mss
import mss.tools
import uinput
from absl import app, logging
from inference_sdk import InferenceHTTPClient
from langchain.globals import set_debug, set_verbose
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.image import ImagePromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import tool
from retroarch import (  # Assuming retroarch.py is accessible
    RetroArchController,
    list_cores,
    list_roms,
    load_rom,
    load_state,
)

from utils import params
from utils.model import make_gemini

# set_verbose(True)
# set_debug(True)

# === Controller Definition ===

BUTTONS = {
    "A": uinput.BTN_A,
    "B": uinput.BTN_X,  # Have to map B to X for special attack
    "X": uinput.BTN_B,  # Vice versa
    "Y": uinput.BTN_Y,
    "TL": uinput.BTN_TL,
    "TR": uinput.BTN_TR,
    "SELECT": uinput.BTN_SELECT,
    "START": uinput.BTN_START,
    "THUMBL": uinput.BTN_THUMBL,
    "THUMBR": uinput.BTN_THUMBR,
    "L": uinput.BTN_TL,  # Aliases for custom buttons; adjust as needed
    "R": uinput.BTN_TR,
    "Z": uinput.BTN_Z,
}
AXES = {
    "X": uinput.ABS_X,
    "Y": uinput.ABS_Y,
}

AXIS_CENTER = 128
AXIS_LEFT = 0
AXIS_RIGHT = 255
AXIS_UP = 0
AXIS_DOWN = 255

TICK = 1 / 60.0

uinput_events = list(BUTTONS.values()) + [
    (uinput.ABS_X + (0, 255, 0, 0)),
    (uinput.ABS_Y + (0, 255, 0, 0)),
]


def image_to_base64(png_file: str) -> str:
    with open(png_file, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# === Move Object ===


class Move:

    def __init__(self, name: str, generator: Callable, urgent: bool = False):
        self.name = name
        self.generator = generator
        self.urgent = urgent

    def __iter__(self):
        return iter(self.generator)

    def __repr__(self):
        return f"<Move name={self.name} urgent={self.urgent}>"


# === Action Primitives ===


def press(button):
    def fn(d):
        logging.info(f"Press {button}")
        d.emit(BUTTONS[button], 1)

    fn._desc = f"press({button})"
    return fn


def release(button):
    def fn(d):
        logging.info(f"Release {button}")
        d.emit(BUTTONS[button], 0)

    fn._desc = f"release({button})"
    return fn


def move_axis(axis, value):
    def fn(d):
        logging.info(f"Move axis {axis} -> {value}")
        d.emit(AXES[axis], value)

    fn._desc = f"move_axis({axis}, {value})"
    return fn


def wait(frames):
    for f in range(frames):

        def fn(d):
            logging.info(f"wait({frames}) noop @ frame {f}")

        fn._desc = f"wait({frames})[{f}]"
        yield (f, fn)


@tool
def move_left():
    """Performs a leftward movement along the X-axis.

    The character moves left immediately and returns to the center
    position on the X-axis after `frames` duration.
    """
    yield (0, move_axis("X", AXIS_LEFT))
    yield (8, move_axis("X", AXIS_CENTER))


@tool
def move_right():
    """Performs a rightward movement along the X-axis.

    The character moves right immediately and returns to the center
    position on the X-axis after `frames` duration.
    """
    yield (0, move_axis("X", AXIS_RIGHT))
    yield (8, move_axis("X", AXIS_CENTER))


@tool
def jump():
    """Performs a jump action.

    This action consists of an immediate upward movement along the Y-axis,
    followed by a return to the center position on the Y-axis after a short
    delay.
    """
    yield (0, move_axis("Y", AXIS_UP))
    yield (2, move_axis("Y", AXIS_CENTER))


@tool
def down(frames=8):
    """Performs a downward movement along the Y-axis (e.g., crouching).

    The character moves down immediately and returns to the center
    position on the Y-axis after `frames` duration.
    """
    yield (0, move_axis("Y", AXIS_DOWN))
    yield (frames, move_axis("Y", AXIS_CENTER))


@tool
def dash(direction="right", dash_frames=6):
    """Performs a dash action in the specified direction.

    The character dashes horizontally (left or right) and returns
    to the center X-axis position after `dash_frames`.
    `direction` can be 'left' or 'right'.
    """
    axis = "X"
    val = AXIS_RIGHT if direction == "right" else AXIS_LEFT
    yield (0, move_axis(axis, val))
    yield (dash_frames, move_axis(axis, AXIS_CENTER))


@tool
def normal_attack():
    """Performs a normal attack.

    This action consists of pressing the 'A' button and releasing it
    after a short delay (8 frames).
    """
    yield (0, press("A"))
    yield (8, release("A"))


@tool
def special_attack():
    """Performs a special attack.

    This action consists of pressing the 'B' button and releasing it
    after a short delay (8 frames). This is a generic special attack,
    often a neutral special when performed on the ground.
    """
    yield (0, press("B"))
    yield (8, release("B"))


@tool
def throw():
    """Performs a throw action.

    This action typically involves pressing the 'Z' button (often grab)
    and releasing it after a short delay (8 frames).
    Assumes a grab has already connected or is part of a grab input.
    """
    yield (0, press("Z"))
    yield (8, release("Z"))


@tool
def taunt():
    """Performs a taunt action.

    This action consists of pressing the 'L' button and releasing it
    after a short delay (8 frames).
    """
    yield (0, press("L"))
    yield (8, release("L"))


@tool
def guard():
    """Performs a guard or shield action.

    This action consists of pressing the 'Z' button (often shield/guard)
    and releasing it after a short delay (8 frames).
    Note: In many games, guard is held. This simulates a brief guard press.
    """
    yield (0, press("Z"))
    yield (8, release("Z"))


@tool
def escape_roll(direction="right"):
    """Performs an escape roll in the specified direction.

    The character presses 'Z' (guard), moves in the specified `direction`
    ('left' or 'right'), returns to center X-axis, and then releases 'Z'.
    """
    yield (0, press("Z"))
    axis = "X"
    val = AXIS_RIGHT if direction == "right" else AXIS_LEFT
    yield (2, move_axis(axis, val))
    yield (8, move_axis(axis, AXIS_CENTER))
    yield (9, release("Z"))


@tool
def weak_attack():
    """Performs a weak attack.

    This is an alias for `normal_attack()`, involving a quick press
    and release of the 'A' button.
    """
    yield from normal_attack.invoke({})


@tool
def strong_attack(direction="right"):
    """Performs a strong attack in the specified direction (tilt attack).

    The character moves in the `direction` ('left' or 'right'),
    presses 'A', releases 'A', and then returns to the center X-axis.
    Typically a forward tilt or side tilt attack.
    """
    axis = "X"
    val = AXIS_RIGHT if direction == "right" else AXIS_LEFT
    yield (0, move_axis(axis, val))
    yield (4, press("A"))
    yield (8, release("A"))
    yield (12, move_axis(axis, AXIS_CENTER))


@tool
def high_attack():
    """Performs a high attack (up tilt attack).

    The character moves briefly up along the Y-axis, presses 'A',
    releases 'A', and then returns to the center Y-axis.
    """
    yield (0, move_axis("Y", AXIS_UP))
    yield (4, press("A"))
    yield (8, release("A"))
    yield (12, move_axis("Y", AXIS_CENTER))


@tool
def low_attack():
    """Performs a low attack (down tilt attack).

    The character moves briefly down along the Y-axis (crouch),
    presses 'A', releases 'A', and then returns to the center Y-axis.
    """
    yield (0, move_axis("Y", AXIS_DOWN))
    yield (4, press("A"))
    yield (8, release("A"))
    yield (12, move_axis("Y", AXIS_CENTER))


@tool
def dashing_attack(direction="right"):
    """Performs a dashing attack in the specified direction.

    The character first performs a dash in the `direction` ('left' or 'right')
    for 5 frames, then presses 'A' and releases it.
    """
    yield from dash.invoke({"direction": direction, "dash_frame": 6})
    yield (10, press("A"))
    yield (14, release("A"))


@tool
def jumping_attack():
    """Performs a jumping attack (neutral air attack).

    The character first performs a jump action, then presses 'A'
    and releases it while in the air.
    """
    yield from jump.invoke({})
    yield (4, press("A"))
    yield (8, release("A"))


@tool
def forward_attack(direction="right"):
    """Performs a forward attack (directional aerial or ground attack).

    The character moves in the specified `direction` ('left' or 'right')
    along the X-axis, presses 'A', releases 'A', and then returns to
    the center X-axis. Can represent a forward air or forward tilt.
    """
    axis = "X"
    val = AXIS_RIGHT if direction == "right" else AXIS_LEFT
    yield (0, move_axis(axis, val))
    yield (4, press("A"))
    yield (8, release("A"))
    yield (12, move_axis(axis, AXIS_CENTER))


@tool
def backward_attack(direction="left"):
    """Performs a backward attack.

    This is an alias for `forward_attack(direction='left')`.
    The character moves left (or specified `direction`), presses 'A',
    releases 'A', and returns to center X-axis.
    """
    yield from forward_attack.invoke({"direction": direction})


@tool
def upward_attack():
    """Performs an upward attack (up air or up tilt).

    The character moves briefly up along the Y-axis, presses 'A',
    releases 'A', and then returns to the center Y-axis.
    """
    yield (0, move_axis("Y", AXIS_UP))
    yield (4, press("A"))
    yield (13, release("A"))
    yield (14, move_axis("Y", AXIS_CENTER))


@tool
def downward_attack():
    """Performs a downward attack (down air or down tilt).

    The character moves briefly down along the Y-axis, presses 'A',
    releases 'A', and then returns to the center Y-axis.
    """
    yield (0, move_axis("Y", AXIS_DOWN))
    yield (4, press("A"))
    yield (13, release("A"))
    yield (14, move_axis("Y", AXIS_CENTER))


@tool
def forward_smash_attack(direction="right"):
    """Performs a forward smash attack.

    The character tilts in the specified `direction` ('left' or 'right'),
    briefly returns to center X-axis (simulating smash input charge-up),
    presses 'A' for an extended duration, releases 'A', and then
    returns to the center X-axis.
    """
    axis = "X"
    val = AXIS_RIGHT if direction == "right" else AXIS_LEFT
    yield (0, move_axis(axis, val))
    yield (3, move_axis(axis, AXIS_CENTER))
    yield (6, press("A"))
    yield (12, release("A"))
    yield (15, move_axis(axis, AXIS_CENTER))


@tool
def high_smash_attack():
    """Performs a high smash attack (up smash).

    The character tilts up along the Y-axis, briefly returns to center
    Y-axis (simulating smash input charge-up), presses 'A' for an
    extended duration, releases 'A', and then returns to the center Y-axis.
    """
    yield (0, move_axis("Y", AXIS_UP))
    yield (3, move_axis("Y", AXIS_CENTER))
    yield (6, press("A"))
    yield (12, release("A"))
    yield (15, move_axis("Y", AXIS_CENTER))


@tool
def low_smash_attack():
    """Performs a low smash attack (down smash).

    The character tilts down along the Y-axis, briefly returns to center
    Y-axis (simulating smash input charge-up), presses 'A' for an
    extended duration, releases 'A', and then returns to the center Y-axis.
    """
    yield (0, move_axis("Y", AXIS_DOWN))
    yield (3, move_axis("Y", AXIS_CENTER))
    yield (6, press("A"))
    yield (23, release("A"))
    yield (24, move_axis("Y", AXIS_CENTER))


@tool
def special_attack_ground():
    """Performs a special attack on the ground (neutral special).

    This action consists of pressing the 'B' button and releasing it
    after a short delay (8 frames). Equivalent to a neutral special move
    when performed on the ground.
    """
    yield (0, press("B"))
    yield (8, release("B"))


@tool
def special_attack_air():
    """Performs a special attack in the air (neutral air special).

    The character first performs a jump action, then presses 'B'
    and releases it while in the air.
    """
    yield from jump.invoke({})
    yield (4, press("B"))
    yield (14, release("B"))


@tool
def up_special():
    """Performs an up special attack.

    The character moves up along the Y-axis, presses 'B', releases 'B'
    after a duration, and then returns to the center Y-axis.
    Often used for recovery.
    """
    yield (0, move_axis("Y", AXIS_UP))
    yield (4, press("B"))
    yield (16, release("B"))
    yield (17, move_axis("Y", AXIS_CENTER))


@tool
def down_special():
    """Performs a down special attack.

    The character moves down along the Y-axis, presses 'B', releases 'B'
    after a duration, and then returns to the center Y-axis.
    """
    yield (0, move_axis("Y", AXIS_DOWN))
    yield (4, press("B"))
    yield (16, release("B"))
    yield (17, move_axis("Y", AXIS_CENTER))


@tool
def left_special():
    """Performs a left special attack (side special to the left).

    The character moves left along the X-axis, presses 'B', releases 'B'
    after a duration, and then returns to the center X-axis.
    """
    yield (0, move_axis("X", AXIS_LEFT))
    yield (4, press("B"))
    yield (16, release("B"))
    yield (17, move_axis("X", AXIS_CENTER))


@tool
def right_special():
    """Performs a right special attack (side special to the right).

    The character moves right along the X-axis, presses 'B', releases 'B'
    after a duration, and then returns to the center X-axis.
    """
    yield (0, move_axis("X", AXIS_RIGHT))
    yield (4, press("B"))
    yield (16, release("B"))
    yield (17, move_axis("X", AXIS_CENTER))


@tool
def jump_attack():
    """Performs a jumping attack (neutral air attack).

    The character first performs a jump action, then presses 'A'
    and releases it while in the air. This is functionally identical
    to `jumping_attack`.
    """
    yield from jump.invoke({})
    yield (4, press("A"))
    yield (14, release("A"))


@tool
def attack_only():
    """Performs a basic attack by pressing and releasing 'A'.

    This action consists of pressing the 'A' button and releasing it
    after a short delay (8 frames). Similar to `normal_attack`.
    """
    yield (0, press("A"))
    yield (8, release("A"))


# === Instrumented Planner Queue Helpers ===


class InstrumentedQueue(queue.Queue):

    def __init__(self, maxsize=0):
        super().__init__(maxsize)

    def put(self, item, block=True, timeout=None):
        move_name = repr(item)
        logging.info(f"ENQUEUE move {move_name!r} (queue size before: {self.qsize()})")
        super().put(item, block, timeout)
        logging.info(f"Queue size after ENQUEUE: {self.qsize()}")

    def get(self, block=True, timeout=None):
        val = super().get(block, timeout)
        move_name = repr(val)
        logging.info(f"DEQUEUE move {move_name!r} (queue size after: {self.qsize()})")
        return val


# === Enqueue Move Helper ===


def enqueue_move(move, move_queue, cancel_event):
    if getattr(move, "urgent", False):
        with move_queue.mutex:
            move_queue.queue.clear()
        cancel_event.set()
        logging.info("Enqueued URGENT move, cleared queue and canceled current.")
    try:
        move_queue.put(move, block=False)
        logging.info("Enqueued move: %r (queue size: %d)", move, move_queue.qsize())
    except queue.Full:
        logging.warning("Queue full! Dropping move %r", move)


# === Move Scheduler/Event Loop ===


def describe_step(step):
    if hasattr(step, "_desc"):
        return step._desc

    return repr(step)


def control_loop(device, move_queue, cancel_event):
    move_counter = 0
    while True:
        try:
            move = move_queue.get(timeout=0.1)
        except queue.Empty:
            # logging.info(f'Queue idle (len={move_queue.qsize()})')
            time.sleep(TICK)
            continue
        move_counter += 1
        move_name = repr(move)
        logging.info(f"Started MOVE #{move_counter}: {move_name!r}; queue size:" f" {move_queue.qsize()}")
        steps = list(move)
        if not steps:
            logging.info(f"Move {move_name!r} is empty: skipping")
            continue
        for idx, (frame_offset, action) in enumerate(steps):
            stepdesc = getattr(action, "_desc", repr(action))
            logging.info(f"Step {idx}: at frame_offset {frame_offset}, does: {stepdesc}")
        current_frame = 0
        next_idx = 0
        while next_idx < len(steps):
            if cancel_event.is_set():
                logging.info(
                    f"Move #{move_counter} {move_name!r} canceled at frame" f" {current_frame}, step {next_idx}"
                )
                cancel_event.clear()
                break
            frame_offset, action = steps[next_idx]
            if current_frame == frame_offset:
                stepdesc = getattr(action, "_desc", repr(action))
                logging.info(f"Executing step {next_idx}/{len(steps)}: {stepdesc} (frame" f" {current_frame})")
                action(device)
                next_idx += 1
            logging.info(f"Tick {current_frame}, (queue size: {move_queue.qsize()})")
            start = time.perf_counter()
            time.sleep(max(0, TICK - (time.perf_counter() - start)))
            current_frame += 1
        for btn in BUTTONS:
            logging.info(f"Reset {btn} to 0")
            device.emit(BUTTONS[btn], 0, syn=False)
        device.emit(AXES["X"], AXIS_CENTER, syn=False)
        device.emit(AXES["Y"], AXIS_CENTER, syn=False)
        device.syn()
        time.sleep(TICK * 16)
        logging.info(f"Move #{move_counter} ({move_name!r}) COMPLETE")
        logging.info(f"Current queue size (post-move): {move_queue.qsize()}")


# === Example Planner Thread (dummy) ===


def dummy_planner(move_queue, cancel_event):
    # List of all move functions to check
    move_funcs = [
        # move_left,
        # move_right,
        # jump,
        # down,
        # dash,
        # normal_attack,
        # special_attack,
        # throw,
        # taunt,
        # guard,
        # escape_roll,
        # weak_attack,
        # strong_attack,
        high_attack,
        # low_attack,
        # dashing_attack,
        # jumping_attack,
        # forward_attack,
        # backward_attack,
        # upward_attack,
        # downward_attack,
        # forward_smash_attack,
        # high_smash_attack,
        # low_smash_attack,
        # special_attack_ground,
        # special_attack_air,
        # up_special,
        # down_special,
        # left_special,
        # right_special,
        # jump_attack,
        # attack_only,
    ]
    i = 0
    while True:
        for fn in move_funcs:
            logging.error(dir(fn))
            move_name = fn.name
            logging.info(f"Planner: Attempting to enqueue {move_name}()")
            try:
                move = Move(
                    name=move_name,
                    generator=fn.invoke({}),
                    urgent=False,
                )
            except TypeError:
                # Some moves require a direction argument
                if "direction" in fn.__code__.co_varnames:
                    move = Move(
                        name=f"{move_name}_right",
                        generator=fn("right"),
                        urgent=False,
                    )
                else:
                    raise
            enqueue_move(move, move_queue, cancel_event)
        time.sleep(TICK * 120)
        i += 1


def capture_fullscreen_screenshot_to_file(filename="screenshot.png"):
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        with open(filename, "wb") as f:
            f.write(mss.tools.to_png(sct_img.rgb, sct_img.size))
    return filename


def screenshot_window(window_name="RetroArch", out_filename="screenshot.png"):
    # Step 1: Dump window to xwd format
    with tempfile.NamedTemporaryFile(suffix=".xwd", delete=False) as tmp_xwd:
        xwd_path = tmp_xwd.name
    try:
        subprocess.run(
            ["xwd", "-silent", "-name", window_name, "-out", xwd_path],
            check=True,
        )
        # Step 2: Convert xwd to png
        subprocess.run(
            ["convert", xwd_path, out_filename],  # Needs ImageMagick 'convert'
            check=True,
        )
    finally:
        if os.path.exists(xwd_path):
            os.unlink(xwd_path)
    return out_filename


def screenshot_window_or_fallback(window_name, out_filename, retroarch_controller):
    try:
        return screenshot_window(window_name, out_filename)
    except subprocess.CalledProcessError:
        # Fallback: use RetroArch's screenshot, then move it to desired location
        print("xwd failed; using RetroArch screenshot fallback!")
        fallback_file = retroarch_controller.take_screenshot()
        shutil.move(fallback_file, out_filename)
        return out_filename


def call_roboflow_inference(image_path):
    client = InferenceHTTPClient(
        api_url="https://serverless.roboflow.com",
        api_key=params.ROBOFLOW_API_KEY,
    )
    result = client.run_workflow(
        workspace_name="smash-64-agents",
        workflow_id="detect-count-and-visualize-3",
        images={"image": image_path},
        use_cache=True,
    )
    return result


def summarize_smash_detection(result):
    if not result or not result[0].get("predictions", {}).get("predictions"):
        return "No characters detected."

    preds = result[0]["predictions"]["predictions"]

    mario = next((p for p in preds if p["class"] == "Mario"), None)
    dk = next((p for p in preds if p["class"] == "DonkeyKong"), None)

    if not mario or not dk:
        return "Could not find both Mario and Donkey Kong."

    def classify_platform(y):
        if y < 650:
            return "upper platform"
        elif y < 1000:
            return "main platform"
        return "lower area"

    mario_platform = classify_platform(mario["y"])
    dk_platform = classify_platform(dk["y"])

    if mario["x"] < dk["x"]:
        horizontal = "to the left of"
    else:
        horizontal = "to the right of"

    same_platform = abs(mario["y"] - dk["y"]) < 100
    platform_phrase = "They are on the same platform." if same_platform else "They are on different platforms."

    return f"Mario is on the {mario_platform}, {horizontal} Donkey Kong. " f"{platform_phrase}"


def summarize_smash_detection(result):
    if not result or not result[0].get("predictions", {}).get("predictions"):
        return "No characters detected."

    preds = result[0]["predictions"]["predictions"]

    mario = next((p for p in preds if p["class"] == "Mario"), None)
    dk = next((p for p in preds if p["class"] == "DonkeyKong"), None)

    if not mario or not dk:
        return "Could not find both Mario and Donkey Kong."

    def classify_platform(y):
        if y < 650:
            return "upper platform"
        elif y < 1000:
            return "main platform"
        return "lower area"

    mario_platform = classify_platform(mario["y"])
    dk_platform = classify_platform(dk["y"])

    dx = abs(mario["x"] - dk["x"])
    dy = abs(mario["y"] - dk["y"])

    # Simple thresholds, tune for your game scale!
    if dx < 70 and dy < 50:
        proximity = "close"
    elif dx < 150 and dy < 80:
        proximity = "medium"
    else:
        proximity = "far"

    if mario["x"] < dk["x"]:
        horizontal = "to the left of"
    else:
        horizontal = "to the right of"

    same_platform = abs(mario["y"] - dk["y"]) < 100
    platform_phrase = "They are on the same platform." if same_platform else "They are on different platforms."

    return (
        f"Mario is on the {mario_platform}, {horizontal} Donkey Kong. "
        f"{platform_phrase} "
        f"Horizontal distance: {dx} pixels; vertical distance: {dy} pixels. "
        f"Proximity: {proximity}."
    )


def summarize_smash_detection(result):
    """Summarize character detection results with as little assumption as possible.

    Raw positions and bounding box sizes are reported; no proximity or platform
    inference is made, as pixel-based measurements can be misleading with camera
    zoom.

    Returns a fact-only summary for the LLM.
    """
    if not result or not result[0].get("predictions", {}).get("predictions"):
        return "No characters detected."

    preds = result[0]["predictions"]["predictions"]

    mario = next((p for p in preds if p.get("class") == "Mario"), None)
    dk = next((p for p in preds if p.get("class") == "DonkeyKong"), None)

    if not mario or not dk:
        return "Could not find both Mario and Donkey Kong."

    def get_box_info(p):
        # Some models have width/height, some min_x/min_y/max_x/max_y
        w = p.get("width")
        h = p.get("height")
        if w is not None and h is not None:
            return f"w={w}, h={h}"
        if all(k in p for k in ("x", "y", "max_x", "max_y", "min_x", "min_y")):
            w = float(p["max_x"]) - float(p["min_x"])
            h = float(p["max_y"]) - float(p["min_y"])
            return f"w={w}, h={h}"
        return "size unknown"

    dx = abs(mario["x"] - dk["x"])
    dy = abs(mario["y"] - dk["y"])

    summary = (
        f"Mario: x={mario['x']}, y={mario['y']}, box({get_box_info(mario)}) | "
        f"DonkeyKong: x={dk['x']}, y={dk['y']}, box({get_box_info(dk)}) | "
        f"Horizontal diff: dx={dx} px, Vertical diff: dy={dy} px. "
        "Pixel units only; scale may vary with camera zoom. "
        "Use raw values, do not assume 'close' or 'far'."
    )
    return summary


def capture_fullscreen_screenshot_to_base64() -> str:
    """Captures the primary monitor and returns it as a base64 encoded PNG string."""
    with mss.mss() as sct:
        # Get information of the primary monitor
        monitor = sct.monitors[1]  # sct.monitors[0] is the virtual "all monitors" screen

        # Grab the data
        sct_img = sct.grab(monitor)

        # Create an in-memory bytes buffer for the PNG image
        # mss.tools.to_png returns bytes
        png_bytes = mss.tools.to_png(sct_img.rgb, sct_img.size)

        return base64.b64encode(png_bytes).decode("utf-8")


def llm_planner(move_queue, cancel_event, retroarch):
    logging.info("LLM Planner: Initializing...")

    try:
        llm = make_gemini(model="gemini-1.5-flash-latest")  # Or your preferred model
    except Exception as e:
        logging.error(
            f"LLM Planner: Failed to initialize Gemini model: {e}",
            exc_info=True,
        )
        return
    logging.info("LLM Planner: Gemini model initialized.")

    # --- Define the tools available to the LLM ---
    # These are your @tool decorated action generator functions
    available_tools = [
        normal_attack,
        special_attack,
        # throw,
        # taunt,
        # guard,
        weak_attack,
        high_attack,
        low_attack,
        special_attack_ground,
        special_attack_air,
        up_special,
        down_special,
        jump_attack,
        attack_only,
        # Movement related
        # move_left,
        # move_right,
        # jump,
        # down,
        # dash,
        # escape_roll,
        strong_attack,
        dashing_attack,
        jumping_attack,
        forward_attack,
        backward_attack,
        upward_attack,
        downward_attack,
        forward_smash_attack,
        high_smash_attack,
        low_smash_attack,
        left_special,
        right_special,
    ]

    if not available_tools:
        logging.error("LLM Planner: No tools defined or found. Planner will not run.")
        return

    # Create a dispatch table for easy lookup (optional, but good practice)
    # Tool objects (from @tool) have a .name attribute
    tool_dispatch_table = {t.name: t for t in available_tools}

    llm_with_tools = llm.bind_tools(available_tools)
    logging.info(f"LLM Planner: Tools bound: {[t.name for t in available_tools]}")

    # loop_delay_seconds = 3.0  # How often to query the LLM (adjust as needed)
    loop_delay_seconds = 0  # How often to query the LLM (adjust as needed)

    while not cancel_event.is_set():
        try:
            logging.debug("LLM Planner: Querying LLM for next move...")
            # ai_msg = llm_with_tools.invoke([human_message])
            # png = retroarch.take_screenshot()
            # screenshot_file = retroarch.take_screenshot()
            # ai_msg = chain.invoke(image_to_base64(png))
            # png = capture_fullscreen_screenshot_to_base64()
            screenshot_file = capture_fullscreen_screenshot_to_file("last_screen.png")
            output_image_b64 = image_to_base64(screenshot_file)
            # screenshot_file = screenshot_window_or_fallback(
            #     "RetroArch ParaLLEl N64 2.0-rc2 f860534",
            #     "last_screen.png",
            #     retroarch,
            # )
            # result = call_roboflow_inference(screenshot_file)
            # print(result)
            # time.sleep(2)  # Wait to avoid rate limiting
            # desc = summarize_smash_detection(result)  # your text summary
            desc = "Mario is to the left of Donkey Kong"
            # output_image_b64 = result[0][
            #     "output_image"
            # ]  # base64-encoded jpeg (or png)
            logging.error(f"{output_image_b64=}")
            logging.error(f"{desc=}")

            # prompt_text = (
            #     "You are playing Super Smash Bros. as Donkey Kong. Your goal"
            #     " is to defeat Mario.\nBelow is an automated description of"
            #     f" the inferred game state:\n\n{desc}\n\nBelow is an annotated"
            #     " image with bounding boxes of the"
            #     " characters.\nINSTRUCTIONS:\n- If Donkey Kong is close enough"
            #     " to attack Mario, choose the most effective attack(s).\n- If"
            #     " not, choose a series of movement/action tools to bring"
            #     " Donkey Kong closer and attack.\n- Plan the next 2 seconds"
            #     " (up to 4 actions). Output your choice as a list of tool"
            #     " calls, in the order they should be executed.\n- Only choose"
            #     " up to 4 tools, and only use the action tools provided.\n"
            # )
            prompt_text = dedent(
                f"""
                You are playing Super Smash Bros. as Mario. Your goal is to defeat Donkey Kong.

                Below is an automated description of the inferred game state:

                {desc}

                Below is an annotated image with bounding boxes of the characters.

                INSTRUCTIONS:
                - PLAN AHEAD: Always plan a sequence of eight actions to execute in the next 2 seconds.
                - If Mario is close enough to attack Donkey Kong, choose the most effective attack(s).
                - If not, choose a series of movement/action tools to bring Mario closer and attack.
                - Output your choice as a list of tool calls, in the order they should be executed.
                - Only choose actions from the provided tools.
                - IMPORTANT: Always output exactly eight tool calls in your answer.
            """
            )

            prompt_text = dedent(
                f"""
                You are playing Super Smash Bros. as Mario. Your goal is to defeat Donkey Kong.

                Game state summary:
                {desc}

                INSTRUCTIONS:
                - Plan **exactly eight** actions (tool calls) to execute in the next 2 seconds.
                - You must use a **mix of movement and attack actions**. Never attack more than 4 times in a row, and always position Mario safely first.
                - If Mario is not near Donkey Kong, focus on getting close. Only attack when it's advantageous.
                - Do NOT use forward_smash_attack if Mario is at the edge.
                - Only use tools from this list:
                    (list the subset you want)
                - Output ONLY a list of 8 tool calls **in the exact order** to use.
            """
            )

            prompt_text = dedent(
                f"""
                You are Mario, playing Super Smash Bros.
                Your goal is to defeat Donkey Kong.

                Here is the current state of the characters:
                {desc}

                Select the next eight actions to take from the available tools.
                Output a list of eight tool calls in the order you will use them.
            """
            )

            prompt_text = dedent(
                f"""
                You are Donkey Kong, playing Super Smash Bros.
                Your goal is to defeat Mario.

                Here is the current state of the characters:
                {desc}

                Select the next eight actions to take from the available tools.
                Output a list of eight tool calls in the order you will use them.
            """
            )

            logging.info(prompt_text)

            human_message = HumanMessagePromptTemplate(
                prompt=[
                    PromptTemplate(template=prompt_text),
                    ImagePromptTemplate(
                        input_variables=["image_data"],
                        template={"url": "data:image/jpeg;base64,{image_data}"},
                    ),
                ]
            )

            prompt = ChatPromptTemplate.from_messages([human_message])

            chain = (
                {
                    "image_data": RunnablePassthrough(),
                    # "desc": RunnablePassthrough(),
                }
                | prompt
                | llm_with_tools
            )

            # ai_msg = chain.invoke({"image_data": png, "desc": desc})
            ai_msg = chain.invoke(output_image_b64)
            logging.info(f"LLM Planner: Raw LLM response: {ai_msg}")

            if ai_msg.tool_calls:
                for tool_call in ai_msg.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    logging.info(f"LLM Planner: Gemini chose tool: {tool_name} with" f" args: {tool_args}")

                    # Find the actual tool object (which is our generator function)
                    if tool_name in tool_dispatch_table:
                        actual_tool_function = tool_dispatch_table[tool_name]

                        # Invoke the tool function (our generator) to get the generator instance
                        # Langchain's Tool.invoke() calls the underlying function.
                        # If the function is a generator, .invoke() returns the generator instance.
                        move_generator_instance = actual_tool_function.invoke(tool_args)

                        # Check if we got a generator
                        if hasattr(move_generator_instance, "__iter__") and hasattr(
                            move_generator_instance, "__next__"
                        ):
                            move = Move(
                                name=tool_name,  # Use the tool's name
                                generator=move_generator_instance,
                                urgent=False,  # Or determine urgency based on tool/context
                            )
                            enqueue_move(move, move_queue, cancel_event)
                            logging.info(f"LLM Planner: Enqueued move for '{tool_name}'")
                        else:
                            # This would happen if a @tool function didn't return a generator
                            logging.warning(
                                f"LLM Planner: Tool '{tool_name}' did not"
                                " return a generator. Result was:"
                                f" {move_generator_instance}. Move not"
                                " enqueued."
                            )
                    else:
                        logging.warning(
                            f"LLM Planner: Tool '{tool_name}' chosen by LLM not" " found in dispatch table."
                        )
            else:
                logging.info("LLM Planner: Gemini did not suggest a tool call." f" Response: {ai_msg.content}")

            if cancel_event.is_set():
                break
            time.sleep(loop_delay_seconds)

        except Exception as e:
            logging.error(f"LLM Planner: Error in planning loop: {e}", exc_info=True)
            if not cancel_event.is_set():
                time.sleep(loop_delay_seconds * 2)  # Longer sleep on error

    logging.info("LLM Planner: Shutdown signal received, exiting.")


# === Setup and Main ===


def make_retroarch():
    # --- Step 1: Instantiate a RetroArch controller ---
    logging.info("Instantiating RetroArchController...")
    retro_controller = RetroArchController()  # Uses default IP and port

    # Optional: Check if RetroArch is alive (good practice)
    if not retro_controller.is_alive(retries=2, delay=0.5):  # Quick check
        logging.error("RetroArch is not responding. Please ensure it's running and" " network commands are enabled.")
        # Before trying to load_rom, RetroArch itself needs to be launched if it's not already.
        # The load_rom tool in retroarch.py launches RetroArch if it's not running.
        # So, the is_alive check here is more for pre-existing instances.
        # If load_rom is meant to start RetroArch, this check might be less critical *before* load_rom.
        # return # Exit if not alive and you expect it to be already running

    # --- Define your ROM and Core paths ---
    # You'll need to adjust these paths to match your system.
    # Use list_roms() and list_cores() to find valid paths if unsure.

    # Example ROM (from your 'roms' buffer)
    # Make sure the path is exactly correct.
    # Using os.path.expanduser to handle "~"
    smash_rom_path = os.path.expanduser("~/var/roms/Super Smash Bros. (U) [!].z64")

    # Example Core - you'll need to find the correct .so file for N64
    # Common N64 core name: mupen64plus_next_libretro.so
    # Use list_cores() to find available cores on your system.
    # e.g., print(list_cores())
    n64_core_path = os.path.expanduser(
        "~/.var/app/org.libretro.RetroArch/config/retroarch/cores/parallel_n64_libretro.so"
    )
    # If list_cores() returns something like:
    # ['/home/danenberg/.var/app/org.libretro.RetroArch/config/retroarch/cores/mupen64plus_next_libretro.so']
    # then n64_core_path should be that full path.

    # Verify paths exist (good practice)
    if not os.path.exists(smash_rom_path):
        logging.error(f"ROM file not found: {smash_rom_path}")
        # You can print available ROMs to help debug:
        # logging.info(f"Available ROMs: {list_roms()}")
        return
    if not os.path.exists(n64_core_path):
        logging.error(f"Core file not found: {n64_core_path}")
        # You can print available cores to help debug:
        # logging.info(f"Available cores: {list_cores()}")
        return

    logging.info(f"Attempting to load ROM: {smash_rom_path} with Core: {n64_core_path}")

    # --- Step 2: Load Super Smash Bros ---
    # The load_rom function from retroarch.py is a @tool but can be called directly.
    # It handles launching RetroArch if it's not already running.
    load_rom_result = load_rom(core=n64_core_path, rom=smash_rom_path)
    logging.info(f"Load ROM result: {load_rom_result}")

    if "failed" in load_rom_result.lower():
        logging.error("Failed to load ROM. Exiting.")
        return

    # After loading a ROM, it's good to verify RetroArch is still responsive via network commands
    # because the new RetroArch instance started by load_rom needs its network commands active.
    # The default RetroArch config usually has this enabled.
    if not retro_controller.is_alive():
        logging.error(
            "RetroArch became unresponsive after attempting to load ROM, or"
            " network commands are not enabled in the newly launched instance."
        )
        return

    # --- Step 3: Load state ---
    # The load_state function from retroarch.py is also a @tool.
    # Assumes you have a savestate in the default slot (or the slot RetroArch is set to load).
    logging.info("Attempting to load state...")
    load_state_result = load_state()
    logging.info(f"Load state result: {load_state_result}")

    if "failed" in load_state_result.lower():
        logging.error("Failed to load state.")
    else:
        logging.info("Successfully initiated load state command.")

    logging.info("Script finished. Check RetroArch.")

    return retro_controller


def main(argv):
    del argv
    retroarch = make_retroarch()
    time.sleep(2)  # Wait a couple seconds for rom to load, etc.

    print("Starting virtual controller. Press Ctrl-C to exit.")
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    move_queue = InstrumentedQueue(maxsize=8)
    cancel_event = threading.Event()
    try:
        with uinput.Device(uinput_events, name="gemma") as device:
            # Reset axes to neutral immediately after device creation
            device.emit(AXES["X"], AXIS_CENTER, syn=False)
            device.emit(AXES["Y"], AXIS_CENTER, syn=False)
            device.syn()
            # Optionally sleep a moment to ensure emulator samples center
            time.sleep(0.1)

            planner_thread = threading.Thread(
                target=dummy_planner,
                args=(move_queue, cancel_event),
                daemon=True,
            )
            # planner_thread = threading.Thread(
            #     target=llm_planner,
            #     args=(move_queue, cancel_event, retroarch),
            #     daemon=True,
            # )
            planner_thread.start()
            control_loop(device, move_queue, cancel_event)
    except OSError as e:
        logging.error("uinput error: %s", e)
        logging.error("Try: sudo modprobe uinput && sudo chmod 666 /dev/uinput")
        sys.exit(1)


if __name__ == "__main__":
    app.run(main)
