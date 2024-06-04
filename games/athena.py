#!/usr/bin/env python
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

import threading
import discord
from absl import app
import logging
import params
import play
import re
import pyparsing


def purge_mentions(message: str):
    mentions = pyparsing.Suppress("<@") + pyparsing.SkipTo(">", include=True).suppress()
    return mentions.transform_string(message)


def extract_move(text):
    # Define the pattern to search for 'rock', 'paper', or 'scissors'
    pattern = r"\b(rock|paper|scissors)\b"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(0)
    return None


def main(argv):
    # Define the intents
    intents = discord.Intents.default()

    # Initialize Client
    client = discord.Client(intents=intents)

    # Event listener for when the client has switched from offline to online
    @client.event
    async def on_ready():
        logging.info(f"Logged in as {client.user}")

    player = play.make_athena()
    step = 0
    game = 0
    wins = 0
    plays = 0
    reward = "START"
    last_move = "START"
    lock = threading.Lock()

    # Event listener for when a message is sent to a channel the client is in
    @client.event
    async def on_message(message):
        nonlocal step, game, reward, last_move, wins, plays

        # Don't let the client respond to its own messages
        if message.author == client.user:
            return

        # Check if the client was mentioned in the message
        if client.user.mentioned_in(message) and message.mention_everyone is False:
            if (move := extract_move(purge_mentions(message.content))) == None:
                return await message.channel.send(
                    f"{message.author.mention}, what move are you trying to make?"
                )

            move = move.upper()

            with lock:
                player.observations.append(move)

                # Let's keep observations at 10 for now.
                if len(player.observations) > 10:
                    player.observations.pop(0)

            with lock:
                if step == 0:
                    reward = "START"

            with lock:
                try:
                    response = player.crew.kickoff(
                        inputs={
                            "observations": player.observations,
                            "reward": reward,
                            "step": step,
                            "game": game,
                        }
                    )
                except Exception as e:
                    return await message.channel.send(
                        f"{message.author.mention}, {str(e)}"
                    )

                player_move = player.move()
                reward = 0
                plays = plays + 1

                if move == "ROCK":
                    if player_move == "SCISSORS":
                        reward = "LOSS"
                    elif player_move == "PAPER":
                        reward = "WIN"
                        wins = wins + 1
                elif move == "SCISSORS":
                    if player_move == "PAPER":
                        reward = "LOSS"
                    elif player_move == "ROCK":
                        reward = "WIN"
                        wins = wins + 1
                elif move == "PAPER":
                    if player_move == "ROCK":
                        reward = "LOSS"
                    elif player_move == "SCISSORS":
                        reward = "WIN"
                        wins = wins + 1

                last_move = player_move
                step = step + 1
                if step % 7 == 0:
                    step = 0
                    game = game + 1
                    reward = "START"
                    last_move = "START"

                return await message.channel.send(
                    f"{message.author.mention}, {response} ({wins} / {plays} wins)"
                )

    client.run(params.ATHENA_TOKEN)


if __name__ == "__main__":
    app.run(main)
