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

from dataclasses import dataclass, field
from enum import Enum
from textwrap import dedent
from typing import Callable

import matplotlib.pyplot as plt
import params
from crewai import Agent, Crew, Task
from crewai_tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pettingzoo.utils.wrappers.order_enforcing import OrderEnforcingWrapper

Environment = OrderEnforcingWrapper


class Move(Enum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2
    START = 3


class Reward(Enum):
    START = -2
    LOSS = -1
    TIE = 0
    WIN = 1


@dataclass
class Player:
    crew: Crew
    move: Callable[[], None]
    observations: list[str] = field(default_factory=list)
    scores: list[int] = field(default_factory=list)


def make_play():
    last_move = None

    @tool("play")
    def play(
        observations: list[str],
        reward: str,
        step: int,
        game: int,
        move: str,
        rationale: str,
    ) -> str:
        """Play a move in rock-paper-scissors.

        Given observations and reward; play a move with the given rationale.

        Args:
          observations (list[str]): Previous moves from the opponent, list
            of START, ROCK, PAPER, SCISSORS.
          reward (str): Previous reward from the last turn, one of LOSS, TIE,
            WIN.
          step (int): The step number.
          game (int): The game number.
          move (str): The move to make, one of ROCK, PAPER, SCISSORS.
          rationale (str): Why we're making this move.

        Returns:
          Move made with rationale."""
        nonlocal last_move
        last_move = move

        return f"Played {move} because {rationale}"

    return play, lambda: last_move


def make_ares():
    play, move = make_play()

    agent = Agent(
        role="Ares the rock-paper-scissors player",
        goal="Play rock-paper-scissors with a brute-force heuristic",
        backstory=dedent(
            """
            You are a Ares the god of war. You are an hilariously
            aggressive rock-paper-scissors player. You start with
            rock. When you win, you stick with your winning move. When
            you lose or tie, cycle clockwise to the next move (rock to
            paper to scissors to rock, etc.).
            """
        ),
        verbose=True,
        llm=make_gemini(),
        max_iter=5,
        tools=[play],
    )

    task = Task(
        description=dedent(
            """
            Play an aggressive game of rock-paper-scissors; given
            prior observations {observations} and reward
            {reward}. This is step {step} of game {game}.
            """
        ),
        expected_output="The move played with rationale",
        agent=agent,
    )

    return Player(
        Crew(
            agents=[agent],
            tasks=[task],
            verbose=1,
            cache=False,
        ),
        move,
    )


def make_athena():
    play, move = make_play()

    agent = Agent(
        role="Athena the rock-paper-scissors player",
        goal="Play rock-paper-scissors with a strategic heuristic",
        backstory=dedent(
            """
            You are a Athena the goddess of wisdom. You are a
            flawlessly strategic rock-paper-scissors player. Attempt
            to observe patterns in your opponent's moves and counter
            accordingly: use paper against rock; scissors against
            paper; and rock against scissors. Be volatile to avoid
            becoming predictable.
            """
        ),
        verbose=True,
        llm=make_gemini(),
        max_iter=5,
        tools=[play],
    )

    task = Task(
        description=dedent(
            """
            Play a strategic game of rock-paper-scissors; given prior
            observations {observations} and reward {reward}. This is
            step {step} of game {game}.
            """
        ),
        expected_output="The move played with rationale",
        agent=agent,
    )

    return Player(
        Crew(
            agents=[agent],
            tasks=[task],
            verbose=1,
        ),
        move,
    )


def make_gemini():
    return ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=params.GOOGLE_API_KEY,
        temperature=1.0,
    )


def plot_scores(players):
    num_games = len(players["player_0"].scores)

    # Setting the global font size
    plt.rcParams.update(
        {"font.size": 24, "font.family": "serif", "font.serif": ["PT Serif"]}
    )  # Adjust font size here
    plt.figure(figsize=(10, 6), constrained_layout=True)

    plt.plot(
        range(num_games),
        players["player_0"].scores,
        label="Ares Wins",
        color="blue",
        linewidth=5,  # Thicker line
    )
    plt.plot(
        range(num_games),
        players["player_1"].scores,
        label="Athena Wins",
        color="red",
        linewidth=5,  # Thicker line
    )

    plt.xlabel("Number of Turns", fontsize=26)
    plt.ylabel("Cumulative Wins", fontsize=26)
    plt.title("Cumulative Wins Over Time for Rock-Paper-Scissors", fontsize=28)
    plt.legend(fontsize=24)
    plt.grid(True, linewidth=1.2)

    plt.tight_layout(pad=0)
    plt.show(block=True)


def play_game(game: int, env: Environment, players: dict[str, Player]):
    env.reset()

    for step, agent in enumerate(env.agent_iter()):
        observation, reward, termination, truncation, info = env.last()

        if termination or truncation:
            break

        player = players[agent]

        player.observations.append(Move(observation).name)
        player.scores.append(
            (player.scores[-1] if player.scores else 0)
            + (1 if reward > 0 else 0)
        )

        player.crew.kickoff(
            inputs={
                "observations": player.observations,
                "reward": Reward(
                    -2 if step == 0 or step == 1 else reward
                ).name,
                "step": step + 1,
                "game": game + 1,
            }
        )

        env.step(Move[player.move()].value)

    env.close()
