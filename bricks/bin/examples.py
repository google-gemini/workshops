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

import json

import params
from absl import app, logging
from vertexai import init
from vertexai.generative_models import GenerativeModel

# Constants
PROJECT_ID = params.PROJECT_ID
LOCATION = params.LOCATION
TOKEN_LIMIT = 32000
DESCRIPTIONS = "var/descriptions.json"
OUTPUT = "var/examples.jsonl"

# Initialize Vertex AI
init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel("gemini-1.5-pro-002")


def read_mpd(file_path: str) -> str:
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        logging.error(f"Error: File {file_path} not found.")
        return ""


def count_tokens(text: str) -> int:
    try:
        response = model.count_tokens(text)
        return response.total_tokens
    except Exception as e:
        logging.error(f"Token count failed: {e}")
        return float("inf")


def generate_example(query: str, mpd_content: str) -> dict:
    return {
        "systemInstruction": {
            "role": "system",
            "parts": [
                {
                    "text": "You generate MPD files for brick builds based on "
                    "user-provided descriptions."
                }
            ],
        },
        "contents": [
            {"role": "user", "parts": [{"text": query}]},
            {"role": "model", "parts": [{"text": mpd_content}]},
        ],
    }


def process_descriptions(input_file: str, output_file: str):
    with open(input_file, "r") as infile:
        data = json.load(infile)

    with open(output_file, "w") as outfile:
        for mpd_path, content in data.items():
            queries = content["queries"]
            mpd_content = read_mpd(mpd_path)

            if not mpd_content:
                continue

            if count_tokens(mpd_content) > TOKEN_LIMIT:
                logging.error(f"Skipping {mpd_path}: exceeds token count")
                continue

            for query in queries:
                example = generate_example(query, mpd_content)
                outfile.write(json.dumps(example) + "\n")
                logging.info(f'Added example for "{query}" to {mpd_path}.')


def main(argv):
    # Truncate output at start
    open(OUTPUT, "w").close()
    process_descriptions(DESCRIPTIONS, OUTPUT)


if __name__ == "__main__":
    app.run(main)
