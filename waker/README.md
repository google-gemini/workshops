# Wind Waker Voice Chat with Controller Support

A real-time AI gaming companion for The Legend of Zelda: Wind Waker that combines voice interaction, visual understanding, and direct game control.

## Features

- **Native Audio Voice Chat**: Real-time conversation using Gemini Live API
- **Visual Game Understanding**: AI can see and analyze the game screen
- **Controller Actuation**: AI can play Wind Waker songs and control the game
- **Episodic Memory**: Remembers your gameplay history and past conversations
- **Walkthrough Integration**: Semantic search over game guides for accurate help

## Prerequisites

- Python 3.11-3.12
- Poetry for dependency management
- PortAudio for audio support
- A gamepad/controller (tested with 8BitDo controllers)

## Installation

1. **Install system dependencies**:
   ```bash
   # For audio support
   brew install portaudio  # macOS
   # or
   sudo apt-get install portaudio19-dev  # Ubuntu/Debian
   ```

2. **Install Python dependencies**:
   ```bash
   cd waker
   poetry install
   ```

3. **Set up controller permissions** (Linux only):
   ```bash
   # Option 1: Run the install script (permanent)
   sudo ./install_controller_permissions.sh
   
   # Option 2: Quick temporary fix (until reboot)
   sudo modprobe uinput
   sudo chmod 666 /dev/uinput
   ```

## Configuration

Set the following environment variables:

```bash
export GOOGLE_API_KEY="your-gemini-api-key"
export MEM0_API_KEY="your-mem0-api-key"  # Optional, for episodic memory
```

## Running the System

### With Controller Support

1. **Start the controller daemon** (Terminal 1):
   ```bash
   cd waker
   poetry run python controller_daemon.py
   ```

2. **Start the voice chat** (Terminal 2):
   ```bash
   cd waker
   ./run_with_controller.sh
   # or directly:
   poetry run python voice_chat.py
   ```

### Voice Chat Only (No Controller)

```bash
cd waker
poetry run python voice_chat.py
```

## Usage

Once running, you can have natural conversations about Wind Waker:

- **"What's on screen?"** - AI analyzes the current game view
- **"What should I do next?"** - Get walkthrough guidance
- **"Where did we leave off?"** - Recall previous gaming sessions
- **"Play Wind's Requiem"** - AI controls the game to play songs

## Controller Daemon

The controller daemon (`controller_daemon.py`) provides:
- Passthrough of physical controller inputs to a virtual controller
- JSON-RPC interface on port 9999 for AI-controlled inputs
- Support for Wind Waker song sequences

## Troubleshooting

### Controller Issues
- **"No such device" error**: Run the permission setup script
- **Controller not detected**: Check device name patterns in `find_controller()`
- **Wrong button mappings**: Adjust mappings in `GC_MAPPING` dict

### Audio Issues
- **ALSA warnings**: Normal on Linux, can be ignored
- **No microphone**: Check PyAudio device detection in `find_pulse_device()`

### Memory Issues
- **MEM0_API_KEY not set**: Episodic memory will be disabled but system still works

## Architecture

- `voice_chat.py`: Main application with Gemini Live integration
- `controller_daemon.py`: Virtual controller passthrough service  
- `walkthrough_embeddings.json`: Pre-computed semantic search index
- Tool functions for game interaction (vision, memory, control)

## Development

To add new controller actions:

1. Define the button sequence in `voice_chat.py`
2. Add a new tool function with `@tool` decorator
3. Update the Gemini tools configuration

Example:
```python
@tool
def play_song_of_passing():
    """Play Song of Passing: Right, Left, Down"""
    commands = [
        {'type': 'button', 'button': 'RIGHT', 'value': 1},
        {'type': 'button', 'button': 'RIGHT', 'value': 0, 'delay': 0.3},
        # ... etc
    ]
    return send_controller_sequence(commands)
```
