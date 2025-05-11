import queue
import signal
import sys
import threading
import time
from typing import Callable
from absl import app, logging
import uinput

# === Controller Definition ===

BUTTONS = {
    'A': uinput.BTN_A,
    'B': uinput.BTN_B,
    'X': uinput.BTN_X,
    'Y': uinput.BTN_Y,
    'TL': uinput.BTN_TL,
    'TR': uinput.BTN_TR,
    'SELECT': uinput.BTN_SELECT,
    'START': uinput.BTN_START,
    'THUMBL': uinput.BTN_THUMBL,
    'THUMBR': uinput.BTN_THUMBR,
    'L': uinput.BTN_TL,  # Aliases for custom buttons; adjust as needed
    'R': uinput.BTN_TR,
    'Z': uinput.BTN_SELECT,
}
AXES = {
    'X': uinput.ABS_X,
    'Y': uinput.ABS_Y,
}

AXIS_CENTER = 128
AXIS_LEFT = 0
AXIS_RIGHT = 255
AXIS_UP = 0
AXIS_DOWN = 255

uinput_events = list(BUTTONS.values()) + [
    (uinput.ABS_X + (0, 255, 0, 0)),
    (uinput.ABS_Y + (0, 255, 0, 0)),
]

# === Move Object ===


class Move:

    def __init__(self, name: str, generator: Callable, urgent: bool = False):
        self.name = name
        self.generator = generator
        self.urgent = urgent

    def __iter__(self):
        return iter(self.generator)

    def __repr__(self):
        return f'<Move name={self.name} urgent={self.urgent}>'


# === Action Primitives ===


def press(button):
    def fn(d):
        logging.info(f'Press {button}')
        d.emit(BUTTONS[button], 1)

    fn._desc = f'press({button})'
    return fn


def release(button):
    def fn(d):
        logging.info(f'Release {button}')
        d.emit(BUTTONS[button], 0)

    fn._desc = f'release({button})'
    return fn


def move_axis(axis, value):
    def fn(d):
        logging.info(f'Move axis {axis} -> {value}')
        d.emit(AXES[axis], value)

    fn._desc = f'move_axis({axis}, {value})'
    return fn


def wait(frames):
    for f in range(frames):

        def fn(d):
            logging.info(f'wait({frames}) noop @ frame {f}')

        fn._desc = f'wait({frames})[{f}]'
        yield (f, fn)


# === Move Library (Comprehensive Set) ===


def move_left(frames=8):
    yield (0, move_axis('X', AXIS_LEFT))
    yield (frames, move_axis('X', AXIS_CENTER))


def move_right(frames=8):
    yield (0, move_axis('X', AXIS_RIGHT))
    yield (frames, move_axis('X', AXIS_CENTER))


def jump():
    yield (0, move_axis('Y', AXIS_UP))
    yield (2, move_axis('Y', AXIS_CENTER))


def down(frames=8):
    yield (0, move_axis('Y', AXIS_DOWN))
    yield (frames, move_axis('Y', AXIS_CENTER))


def dash(direction='right', dash_frames=4):
    axis = 'X'
    val = AXIS_RIGHT if direction == 'right' else AXIS_LEFT
    yield (0, move_axis(axis, val))
    yield (dash_frames, move_axis(axis, AXIS_CENTER))


def normal_attack():
    yield (0, press('A'))
    yield (8, release('A'))


def special_attack():
    yield (0, press('B'))
    yield (8, release('B'))


def throw():
    yield (0, press('Z'))
    yield (8, release('Z'))


def taunt():
    yield (0, press('L'))
    yield (8, release('L'))


def guard():
    yield (0, press('Z'))
    yield (8, release('Z'))


def escape_roll(direction='right'):
    yield from guard()
    axis = 'X'
    val = AXIS_RIGHT if direction == 'right' else AXIS_LEFT
    yield (2, move_axis(axis, val))
    yield (8, move_axis(axis, AXIS_CENTER))
    yield (9, release('Z'))


def weak_attack():
    yield from normal_attack()


def strong_attack(direction='right'):
    axis = 'X'
    val = AXIS_RIGHT if direction == 'right' else AXIS_LEFT
    yield (0, move_axis(axis, val))
    yield (2, press('A'))
    yield (8, release('A'))
    yield (9, move_axis(axis, AXIS_CENTER))


def high_attack():
    yield (0, move_axis('Y', AXIS_UP))
    yield (2, press('A'))
    yield (8, release('A'))
    yield (9, move_axis('Y', AXIS_CENTER))


def low_attack():
    yield (0, move_axis('Y', AXIS_DOWN))
    yield (2, press('A'))
    yield (8, release('A'))
    yield (9, move_axis('Y', AXIS_CENTER))


def dashing_attack(direction='right'):
    yield from dash(direction)
    yield (2, press('A'))
    yield (8, release('A'))


def jumping_attack():
    yield from jump()
    yield (2, press('A'))
    yield (8, release('A'))


def forward_attack(direction='right'):
    axis = 'X'
    val = AXIS_RIGHT if direction == 'right' else AXIS_LEFT
    yield (0, move_axis(axis, val))
    yield (2, press('A'))
    yield (8, release('A'))
    yield (9, move_axis(axis, AXIS_CENTER))


def backward_attack(direction='left'):
    yield from forward_attack(direction='left')


def upward_attack():
    yield (0, move_axis('Y', AXIS_UP))
    yield (2, press('A'))
    yield (8, release('A'))
    yield (9, move_axis('Y', AXIS_CENTER))


def downward_attack():
    yield (0, move_axis('Y', AXIS_DOWN))
    yield (2, press('A'))
    yield (8, release('A'))
    yield (9, move_axis('Y', AXIS_CENTER))


def forward_smash_attack(direction='right'):
    axis = 'X'
    val = AXIS_RIGHT if direction == 'right' else AXIS_LEFT
    yield (0, move_axis(axis, val))
    yield (1, move_axis(axis, AXIS_CENTER))
    yield (2, press('A'))
    yield (12, release('A'))
    yield (13, move_axis(axis, AXIS_CENTER))


def high_smash_attack():
    yield (0, move_axis('Y', AXIS_UP))
    yield (1, move_axis('Y', AXIS_CENTER))
    yield (2, press('A'))
    yield (12, release('A'))
    yield (13, move_axis('Y', AXIS_CENTER))


def low_smash_attack():
    yield (0, move_axis('Y', AXIS_DOWN))
    yield (1, move_axis('Y', AXIS_CENTER))
    yield (2, press('A'))
    yield (12, release('A'))
    yield (13, move_axis('Y', AXIS_CENTER))


def special_attack_ground():
    yield (0, press('B'))
    yield (8, release('B'))


def special_attack_air():
    yield from jump()
    yield (2, press('B'))
    yield (10, release('B'))


def up_special():
    yield (0, move_axis('Y', AXIS_UP))
    yield (1, press('B'))
    yield (10, release('B'))
    yield (11, move_axis('Y', AXIS_CENTER))


def down_special():
    yield (0, move_axis('Y', AXIS_DOWN))
    yield (1, press('B'))
    yield (10, release('B'))
    yield (11, move_axis('Y', AXIS_CENTER))


def left_special():
    yield (0, move_axis('X', AXIS_LEFT))
    yield (1, press('B'))
    yield (10, release('B'))
    yield (11, move_axis('X', AXIS_CENTER))


def right_special():
    yield (0, move_axis('X', AXIS_RIGHT))
    yield (1, press('B'))
    yield (10, release('B'))
    yield (11, move_axis('X', AXIS_CENTER))


def jump_attack():
    yield from jump()
    yield (1, press('A'))
    yield (10, release('A'))


def attack_only():
    yield (0, press('A'))
    yield (8, release('A'))


# === Instrumented Planner Queue Helpers ===


class InstrumentedQueue(queue.Queue):

    def __init__(self, maxsize=0):
        super().__init__(maxsize)

    def put(self, item, block=True, timeout=None):
        move_name = repr(item)
        logging.info(
            f'ENQUEUE move {move_name!r} (queue size before: {self.qsize()})'
        )
        super().put(item, block, timeout)
        logging.info(f'Queue size after ENQUEUE: {self.qsize()}')

    def get(self, block=True, timeout=None):
        val = super().get(block, timeout)
        move_name = repr(val)
        logging.info(
            f'DEQUEUE move {move_name!r} (queue size after: {self.qsize()})'
        )
        return val


# === Enqueue Move Helper ===


def enqueue_move(move, move_queue, cancel_event):
    if getattr(move, 'urgent', False):
        with move_queue.mutex:
            move_queue.queue.clear()
        cancel_event.set()
        logging.info(
            'Enqueued URGENT move, cleared queue and canceled current.'
        )
    try:
        move_queue.put(move, block=False)
        logging.info(
            'Enqueued move: %r (queue size: %d)', move, move_queue.qsize()
        )
    except queue.Full:
        logging.warning('Queue full! Dropping move %r', move)


# === Move Scheduler/Event Loop ===


def describe_step(step):
    if hasattr(step, '_desc'):
        return step._desc
    return repr(step)


def control_loop(device, move_queue, cancel_event):
    TICK = 1 / 60.0
    move_counter = 0
    while True:
        try:
            move = move_queue.get(timeout=0.1)
        except queue.Empty:
            logging.info(f'Queue idle (len={move_queue.qsize()})')
            time.sleep(TICK)
            continue
        move_counter += 1
        move_name = repr(move)
        logging.info(
            f'Started MOVE #{move_counter}: {move_name!r}; queue size:'
            f' {move_queue.qsize()}'
        )
        steps = list(move)
        if not steps:
            logging.info(f'Move {move_name!r} is empty: skipping')
            continue
        for idx, (frame_offset, action) in enumerate(steps):
            stepdesc = getattr(action, '_desc', repr(action))
            logging.info(
                f'Step {idx}: at frame_offset {frame_offset}, does: {stepdesc}'
            )
        current_frame = 0
        next_idx = 0
        while next_idx < len(steps):
            if cancel_event.is_set():
                logging.info(
                    f'Move #{move_counter} {move_name!r} canceled at frame'
                    f' {current_frame}, step {next_idx}'
                )
                cancel_event.clear()
                break
            frame_offset, action = steps[next_idx]
            if current_frame == frame_offset:
                stepdesc = getattr(action, '_desc', repr(action))
                logging.info(
                    f'Executing step {next_idx}/{len(steps)}: {stepdesc} (frame'
                    f' {current_frame})'
                )
                action(device)
                next_idx += 1
            logging.info(
                f'Tick {current_frame}, (queue size: {move_queue.qsize()})'
            )
            start = time.perf_counter()
            time.sleep(max(0, TICK - (time.perf_counter() - start)))
            current_frame += 1
        for btn in BUTTONS:
            logging.info(f'Reset {btn} to 0')
            device.emit(BUTTONS[btn], 0, syn=False)
        device.emit(AXES['X'], AXIS_CENTER, syn=False)
        device.emit(AXES['Y'], AXIS_CENTER, syn=False)
        device.syn()
        logging.info(f'Move #{move_counter} ({move_name!r}) COMPLETE')
        logging.info(f'Current queue size (post-move): {move_queue.qsize()}')


# === Example Planner Thread (dummy) ===


def dummy_planner(move_queue, cancel_event):
    i = 0
    while True:
        time.sleep(1.5)
        logging.info(f'Planner: Attempting to enqueue jump_attack()')
        move = Move(
            name='jump_attack',
            generator=jump_attack(),
            urgent=False if i % 2 == 0 else True,
        )
        enqueue_move(move, move_queue, cancel_event)
        time.sleep(0.5)
        i += 1


# === Setup and Main ===


def main(argv):
    del argv
    print('Starting virtual controller. Press Ctrl-C to exit.')
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    move_queue = InstrumentedQueue(maxsize=2)
    cancel_event = threading.Event()
    try:
        with uinput.Device(uinput_events, name='gemma') as device:
            planner_thread = threading.Thread(
                target=dummy_planner,
                args=(move_queue, cancel_event),
                daemon=True,
            )
            planner_thread.start()
            control_loop(device, move_queue, cancel_event)
    except OSError as e:
        logging.error('uinput error: %s', e)
        logging.error('Try: sudo modprobe uinput && sudo chmod 666 /dev/uinput')
        sys.exit(1)


if __name__ == '__main__':
    app.run(main)
