#!/usr/bin/env python3
# Copyright 2024 Google LLC
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

import base64
import io
import json
import logging
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, field
from os.path import join
from signal import pause
from typing import Callable
from urllib.parse import urlencode, urlunparse

import adafruit_dotstar as dotstar
import board
import google.auth
import requests
import webcolors
from absl import app
from google.auth.transport.requests import Request
from gpiozero import Button
from pydub import AudioSegment

import params


def get_rgb(color: str) -> tuple[int, int, int]:
    rgb = webcolors.name_to_rgb(color)
    return (rgb.red, rgb.green, rgb.blue)


@contextmanager
def set_dot(dots: dotstar.DotStar, index: int, color: str) -> None:
    dots[index] = color
    try:
        yield
    finally:
        dots[index] = get_rgb("black")


def make_dots() -> dotstar.DotStar:
    num_pixels = 3

    return dotstar.DotStar(
        board.D6,
        board.D5,
        num_pixels,
        brightness=0.2,
    )


@dataclass
class State:
    arecord: subprocess.Popen = None
    dots: dotstar.DotStar = make_dots()
    recording: str = None


def make_record(state: State) -> Callable[[], None]:
    """Returns a function with a state-closure for recording audio."""

    def record() -> None:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            state.recording = f.name
            logging.info(f"Recording to {state.recording}.")
            state.arecord = subprocess.Popen(
                ["parecord", "--channels=1", state.recording]
            )
        state.dots[0] = get_rgb("red")

    return record


def make_stop(state: State) -> Callable[[], None]:
    """Returns a function with a state-closure for transcribing audio."""

    def stop() -> None:
        state.arecord.terminate()
        state.arecord.wait()
        state.dots[0] = get_rgb("black")

        with set_dot(state.dots, 1, get_rgb("green")):
            transcription = transcribe_audio(state.recording)
            logging.info(f"{transcription=}")

        with set_dot(state.dots, 2, get_rgb("blue")):
            gemini = get_gemini_response(transcription)
            logging.info(f"{gemini=}")

        with set_dot(state.dots, 1, get_rgb("green")):
            synthesis = generate_audio(gemini)
            # Prime the bluetooth device with a second a silence; to
            # avoid the bump, consider concatenating.
            subprocess.run(["paplay", "silence.wav"], check=True)
            subprocess.run(["paplay", synthesis], check=True)

    return stop


@dataclass
class URLComponents:
    scheme: str = "https"
    netloc: str = ""
    path: list[str] = field(default_factory=list)
    params: str = ""
    query: dict[str] = field(default_factory=dict)
    fragment: str = ""

    def to_tuple(self) -> tuple:
        return (
            self.scheme,
            self.netloc,
            join(*self.path),
            self.params,
            urlencode(self.query),
            self.fragment,
        )


def get_gemini_response(query: str) -> str:
    headers = {
        "Content-Type": "application/json",
    }

    url = urlunparse(
        URLComponents(
            netloc="generativelanguage.googleapis.com",
            path=["v1beta", "models", "gemini-pro:generateContent"],
            query={"key": params.GOOGLE_API_KEY},
        ).to_tuple()
    )

    data = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": "You are a helpful and hilarious bot embedded "
                        "in a Raspberry Pi. Answer in one sentence only; but "
                        "inject some disfluencies to sound more human."
                    }
                ],
            },
            {"role": "model", "parts": [{"text": "Ok!"}]},
            {"role": "user", "parts": [{"text": query}]},
        ],
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ],
        "generationConfig": {
            "temperature": 1.0,
        },
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    logging.debug(response.text)

    # Arbitrary return the first response (assuming it exists).
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


def encode_audio(file: str) -> str:
    # Read the audio file in binary mode
    with open(file, "rb") as audio:
        audio_data = audio.read()

    # Encode the binary data to base64
    base64_encoded_data = base64.b64encode(audio_data)

    # Convert bytes to string for JSON serialization
    base64_encoded_string = base64_encoded_data.decode("utf-8")

    return base64_encoded_string


def get_token() -> str:
    # Attempt to obtain the default credentials
    credentials, project = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    # Ensure credentials are valid and have a token
    if credentials.requires_scopes:
        credentials = credentials.with_scopes(
            ["https://www.googleapis.com/auth/cloud-platform"]
        )

    if credentials.valid is False:
        credentials.refresh(Request())

    return credentials.token


def transcribe_audio(file: str) -> str:
    # Use the credentials to authenticate your API request
    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json",
    }

    # Speech recognition API endpoint
    url = urlunparse(
        URLComponents(
            netloc="speech.googleapis.com",
            path=["v1", "speech:recognize"],
        ).to_tuple()
    )

    # Sample request data
    data = {
        "config": {"languageCode": "en-US"},
        "audio": {"content": encode_audio(file)},
    }

    # Make the API request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    return response.json()["results"][0]["alternatives"][0]["transcript"]


def generate_audio(text: str) -> str:
    # Use the credentials to authenticate your API request
    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json",
    }

    # Speech recognition API endpoint
    url = urlunparse(
        URLComponents(
            netloc="texttospeech.googleapis.com",
            path=["v1", "text:synthesize"],
        ).to_tuple()
    )

    # Sample request data
    data = {
        "audioConfig": {
            "audioEncoding": "LINEAR16",
        },
        "input": {"text": text},
        "voice": {"languageCode": "en-US", "name": "en-US-Journey-F"},
    }

    # Make the API request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    audio_data = base64.b64decode(response.json()["audioContent"])

    segment = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
    # Inject a little silence at the beginning to prime the bluetooth
    # device; otherwise, first few words get truncated.
    silence = AudioSegment.silent(duration=500)

    # pydub can also play without forcing recourse to serialization;
    # cost-benefit?
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        logging.info(f"Synthesizing to {f.name}.")
        (silence + segment).export(f.name, format="wav")
        return f.name


def main(argv):
    state = State()
    # Reset the LEDs
    state.dots.fill(get_rgb("black"))

    button = Button(17)  # Set up pin 17 for the button

    button.when_pressed = make_record(state)
    button.when_released = make_stop(state)

    logging.info("Ready to talk!")

    pause()


if __name__ == "__main__":
    app.run(main)
