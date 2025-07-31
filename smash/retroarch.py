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

import os
import socket
import subprocess
import time
from pathlib import Path

from absl import logging
from image import process_image

ROM_EXTENSIONS = (".z64", ".n64", ".v64", ".sfc", ".gba", ".gb")
CORE_EXTENSIONS = (".so",)

# TODO: Instead of hard-coding these, try e.g. GET_CONFIG_PARAM.
DEFAULT_CORES_DIR = os.path.expanduser("~/.var/app/org.libretro.RetroArch/config/retroarch/cores")
DEFAULT_SCREENSHOTS_DIR = os.path.expanduser("~/.var/app/org.libretro.RetroArch/config/retroarch/screenshots")
DEFAULT_ROMS_DIR = os.path.expanduser("~/var/roms")


class RetroArchController:

    def __init__(self, ipaddr="127.0.0.1", portnum=55355):
        """Initializes a connection to RetroArch's UDP network interface.

        :param ipaddr: IP address where RetroArch is running (default:
        localhost). :param portnum: UDP port number (default: 55355).
        """
        self.ipaddr = ipaddr
        self.portnum = portnum
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_command(self, command, expect_response=True):
        """Sends a command to RetroArch and optionally waits for a response.

        :param command: Command to send (e.g., 'GET_STATUS', 'LOAD_STATE').
        :param expect_response: If True, waits for a response from RetroArch.
        Defaults to True.
        :return: Response from RetroArch if expect_response is True; otherwise
        None.
        """
        try:
            # Send the command
            self.socket.sendto(f"{command}\n".encode("utf-8"), (self.ipaddr, self.portnum))
            logging.info(f"Command sent: {command}")

            if expect_response:
                # Wait for a response
                self.socket.settimeout(2)  # Timeout for receiving a response
                response, _ = self.socket.recvfrom(1024)
                return response.decode("utf-8").strip()

            return None
        except socket.timeout:
            logging.warning(f"Command '{command}' sent, but no response received (timeout).")
            return None
        except Exception as e:
            logging.error(f"Failed to send command '{command}': {e}")
            return None
        finally:
            self.socket.settimeout(None)  # Restore the default timeout

    def load_state(self):
        """Sends the `LOAD_STATE` command to RetroArch to load the currently-selected savestate."""
        self.send_command("LOAD_STATE", expect_response=False)

    def get_status(self):
        """Sends the `GET_STATUS` command to RetroArch to get the current game status.

        :return: Parsed status information, or None if the command fails.
        """
        return self.send_command("GET_STATUS")

    def take_screenshot(self, screenshot_dir=DEFAULT_SCREENSHOTS_DIR):
        try:
            # Cache existing files
            existing_files = set(Path(screenshot_dir).glob("*.png"))

            # Send the command
            self.send_command("SCREENSHOT")
            logging.info("Sent SCREENSHOT command. Checking for new screenshot...")

            # Allow some time for the file to appear
            time.sleep(1)

            # Look for a new file
            new_files = set(Path(screenshot_dir).glob("*.png")) - existing_files
            if new_files:
                latest_file = max(new_files, key=lambda x: x.stat().st_mtime)
                logging.info(f"New screenshot found: {latest_file}")
                return str(latest_file)

            logging.warning("No new screenshots found in the directory.")
            return None

        except Exception as e:
            logging.error(f"Failed to locate screenshot: {e}")
            return None

    def is_alive(self, retries=5, delay=1):
        """Sends a test command to verify if RetroArch is responding.

        Retries multiple times if the initial attempts fail.

        :param retries: Number of retries before giving up.
        :param delay: Delay in seconds between retries.
        :return: True if RetroArch responds; False otherwise.
        """
        for attempt in range(retries):
            try:
                response = self.send_command("VERSION")
                if response:
                    logging.info(f"RetroArch Version: {response}")
                    return True
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1}/{retries}: RetroArch not responding" f" ({e})")
                time.sleep(delay)

        logging.error("RetroArch did not respond after multiple attempts.")
        return False


class DirectoryNotFoundError(Exception):
    """Custom exception for non-existent directories."""

    pass


def list_roms() -> list[str]:
    """List all ROMs in the default directory.

    Returns:
        list[str]: A list of full paths to the detected ROM files.
    """
    # Use the predefined default ROMs directory
    directory = DEFAULT_ROMS_DIR

    if not os.path.exists(directory):
        raise DirectoryNotFoundError(f"The directory '{directory}' does not exist.")

    # Scan the directory for ROM files
    roms = [
        os.path.join(root, file)
        for root, _, files in os.walk(directory)
        for file in files
        if file.endswith(ROM_EXTENSIONS)
    ]
    return roms


def list_cores() -> list[str]:
    """List all libretro cores in the default directory.

    Returns:
        list[str]: A list of full paths to the detected core files.
    """
    # Use the predefined default cores directory
    directory = DEFAULT_CORES_DIR

    if not os.path.exists(directory):
        raise DirectoryNotFoundError(f"The directory '{directory}' does not exist.")

    # Scan the directory for core files
    cores = [
        os.path.join(root, file)
        for root, _, files in os.walk(directory)
        for file in files
        if file.endswith(CORE_EXTENSIONS)
    ]
    return cores


# Global process handle for RetroArch
retroarch_process = None


def load_rom(core: str, rom: str) -> str:
    """Launch RetroArch with the specified core and ROM as a persistent process in the background.

    RetroArch will run with the provided core and ROM. The caller can manage
    the process as needed.

    :param core: Path to the libretro core.
    :param rom: Path to the ROM file.
    :return: A string indicating success or failure.
    """
    try:
        # Start RetroArch as a background process
        process = subprocess.Popen(
            ["flatpak", "run", "org.libretro.RetroArch", "-L", core, rom],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,  # Detach the process
        )

        # Allow some time for RetroArch to initialize
        time.sleep(2)

        if process.poll() is not None:
            # Process exited unexpectedly; fetch the error details
            stderr = process.stderr.read().decode().strip()
            return f"RetroArch failed to start:\n{stderr}"

        return f"Successfully launched {rom} using {core}. Process ID:" f" {process.pid}"
    except Exception as e:
        return f"Failed to launch {rom} using {core}: {e}"


def describe_retroarch_state(query: str) -> str:
    """Describe the current state of the game in RetroArch, including the screenshot and additional context.

    Args:
        query (str): The user's query to guide the description.

    Returns:
        str: A detailed description of the game's current state, combining image
        analysis and context.
    """
    retroarch_controller = RetroArchController()

    try:
        # Step 1: Check if RetroArch is alive
        if not retroarch_controller.is_alive():
            return "RetroArch is not running or not responding."

        # Step 2: Get additional context using GET_STATUS
        status = retroarch_controller.get_status()
        if not status:
            additional_context = "Could not retrieve game status."
        else:
            additional_context = status

        # Step 3: Take a screenshot
        screenshot_path = retroarch_controller.take_screenshot(DEFAULT_SCREENSHOTS_DIR)
        if not screenshot_path:
            return "Failed to capture a screenshot of the game."

        # Step 4: Process the image with the query and additional context
        description = process_image(query, screenshot_path, additional_context)
        return description

    except Exception as e:
        logging.error(f"Error describing RetroArch state: {e}")
        return f"Failed to describe RetroArch state: {e}"


# Cleanup function to terminate RetroArch at exit
def cleanup_retroarch():
    global retroarch_process
    if retroarch_process and retroarch_process.poll() is None:
        retroarch_process.terminate()
        retroarch_process.wait()


def load_state() -> str:
    """Load the currently selected savestate in RetroArch.

    This tool checks if RetroArch is running and a game is already loaded.
    If RetroArch is running but no game is loaded, it will prompt to load the
    game first.

    Assumptions:
      - RetroArch is running and network commands are enabled.
      - A ROM is already loaded; if not, an appropriate error message is
      returned.

    This tool handles state loading entirely through RetroArch's default
    mechanisms.
    """
    try:
        # Initialize the RetroArch controller
        retroarch = RetroArchController()

        # Check if RetroArch is running
        if not retroarch.is_alive():
            return (
                "RetroArch is not running or not responding. Please ensure it"
                " is running with network commands enabled."
            )

        # Attempt to load the state
        retroarch.load_state()

        # Return success if no exceptions occur
        return "Successfully loaded the savestate."
    except Exception as e:
        # Handle unexpected errors
        return f"Failed to load savestate: {e}"
