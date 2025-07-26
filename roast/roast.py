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
from enum import Enum
from textwrap import dedent

import params
from crewai import LLM, Agent, Task
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel

os.environ["GEMINI_API_KEY"] = params.GOOGLE_API_KEY
os.environ["OPENAI_API_KEY"] = params.OPENAI_API_KEY
os.environ["XAI_API_KEY"] = params.XAI_API_KEY


class Roast(BaseModel):
    roast: str
    thought: str


class Winner(Enum):
    GROK = "GROK"
    GEMINI = "GEMINI"


class JudgingResponse(BaseModel):
    winner: Winner
    thought: str


def make_gemini():
    return LLM(
        model="gemini/gemini-2.0-flash",
        temperature=1.2,
        safety_settings=[
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
    )


def make_grok():
    return LLM(
        model="xai/grok-2-latest",
        temperature=1.2,
    )


def make_chatgpt():
    return LLM(
        model="gpt-4o",
        temperature=1.2,
    )


def make_agent(llm, name: str, opponent: str, roastee: str) -> Agent:
    """Create a no holds barred, quick quip roast agent.

    Args:
        llm (LLM): The language model instance to use for generating responses.
        name (str): The name of the roast agent.
        opponent (str): The opponent in the roast battle.
        roastee (str): The main subject of the roast.

    Returns:
        Agent: Configured roast agent for sharp, uncensored exchanges with focus
        on the roastee.
    """
    role = f"Uncensored Quip Master ({name})"
    goal = f"Deliver sharp, focused roasts about {roastee}, using {opponent} as a" " foil for contrast and engagement."
    backstory = (
        f"Known as '{name}', your comedic aim is to craft biting quips about"
        f" {roastee}, skillfully responding to {opponent}'s retorts. Your primary"
        f" focus is to scrutinize {roastee}'s eccentricities and controversies,"
        f" while subtly reminding {opponent} of their own follies and"
        " shortcomings related to their efforts. Maintain a comedic edge with"
        f" quips that keep {roastee} as the central theme."
    )

    return Agent(llm=llm, role=role, goal=goal, backstory=backstory, verbose=True)


def make_judging_agent(llm, name: str, judgees: list) -> Agent:
    """Create a judging agent for evaluating roast battles.

    Args:
        llm (LLM): The language model instance to use for judging.
        name (str): The name of the judging agent.
        judgees (list): Names of the participants being judged.

    Returns:
        Agent: Configured judging agent with relevant roles and goals.
    """
    role = f"Impartial Roast Judge ({name})"
    goal = (
        f"Fairly evaluate and decide the winner between {judgees[0]} and" f" {judgees[1]} based on their wit and humor."
    )
    backstory = (
        f"You are '{name}', an impartial and seasoned connoisseur of humor tasked"
        f" with evaluating a roast battle between {judgees[0]} and {judgees[1]}."
        " Your mission is to judge their exchanges with a keen eye for wit,"
        " humor, and overall impact, declaring a winner each round."
    )

    return Agent(llm=llm, role=role, goal=goal, backstory=backstory, verbose=True)


def make_task(agent: Agent) -> Task:
    """Create a CrewAI task for a roast battle response using the Roast object.

    Args:
        agent (Agent): The agent participating in the roast battle.

    Returns:
        Task: A CrewAI task for creating a roast response, capturing both roast
        and thought.
    """
    # Use PydanticOutputParser with the Roast object
    parser = PydanticOutputParser(pydantic_object=Roast)

    task = Task(
        description=dedent(
            """\
            You are in a no holds barred roast battle. Respond with quick, witty quips that engage and provoke your
            opponent.

            Roast History:
            {roast_history}

            Instructions:
            1. Craft a short, sharp roast to aggressively respond to your opponent.
            2. Keep responses to one or two sentences maximum.
            3. Be bold, provocative, and unrestrained, prioritizing humor and edge.
            4. Explain your reasoning or thought process behind your roast.
            """
        ),
        expected_output=("Return valid JSON with the roast and thought:" f" {parser.get_format_instructions()}"),
        agent=agent,
        output_pydantic=Roast,
    )

    return task


def make_judging_task(agent: Agent) -> Task:
    """Create a task for judging a roast battle, outputting a winner and rationale.

    Args:
        agent (Agent): The judge agent evaluating the roasts.

    Returns:
        Task: A CrewAI task for determining the winner of the roast battle.
    """
    parser = PydanticOutputParser(pydantic_object=JudgingResponse)

    task = Task(
        description=dedent(
            """\
            You are judging a roast battle. Evaluate the wit, humor, and impact of the roasts.

            Entire Roast History:
            {roast_history}

            Focus especially on the Last Exchange:
            {last_exchange}

            Instructions:
            1. Decide the winner based on the humor, wit, and impact of their roasts. Choose between
               'GROK' and 'GEMINI'.
            2. Provide a brief reason for your decision.
            """
        ),
        expected_output=("Return valid JSON with winner and thought:" f" {parser.get_format_instructions()}"),
        agent=agent,
        output_pydantic=JudgingResponse,
    )

    return task


def format_history(roast_history):
    """Format the roast history to include only the roasts without thoughts.

    Args:
        roast_history (list): A list of dicts containing speaker and text/roast.

    Returns:
        str: A formatted string of the roast journey.
    """
    return "\n".join(f"{turn['speaker']}: {turn['roast']}" for turn in roast_history)
