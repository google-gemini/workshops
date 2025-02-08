import json
import os
from dataclasses import dataclass, field
from enum import Enum
from textwrap import dedent
from typing import Dict, List

import params
from crewai import LLM, Agent, Crew, Task
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel


# Move enum definition
class Move(Enum):
    COOPERATE = "COOPERATE"
    DEFECT = "DEFECT"


# Pydantic model to wrap the move
class NextMove(BaseModel):
    move: Move
    thought: str


os.environ["GEMINI_API_KEY"] = params.GOOGLE_API_KEY
os.environ["DEEPSEEK_API_KEY"] = params.DEEPSEEK_API_KEY
os.environ["OPENAI_API_KEY"] = params.OPENAI_API_KEY


def make_gemini():
    return LLM(
        model="gemini/gemini-2.0-flash-thinking-exp",
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


def make_deepseek():
    return LLM(
        # model="deepseek/deepseek-chat",
        model="o1-mini",
    )


def make_agent(llm, name: str, strategy: str = "adaptive", lore_key: str = "sun-tzu") -> Agent:
    """
    Create a CrewAI agent for the Prisoner's Dilemma game with predefined traits and lore.

    Args:
        llm (object): An instance of a CrewAI-compatible LLM (e.g., Gemini or DeepSeek).
        name (str): The name of the agent (e.g., "Gemini" or "DeepSeek").
        strategy (str): The agent's strategy (e.g., "adaptive", "ruthless").
        lore_key (str): The key for the agent's lore description.

    Returns:
        Agent: Configured CrewAI agent for the Prisoner's Dilemma.
    """

    # Predefined strategy descriptions
    strategy_traits = {
        "adaptive": "You observe your opponent closely and adjust your moves based on their behavior.",
        "ruthless": "You exploit every weakness, prioritizing your own success over any trust or cooperation.",
        "tit-for-tat": "You mirror your opponent's actions to establish a relationship of trust and fairness.",
        "defensive": (
            "You are cautious, aiming to avoid risks while ensuring your opponent cannot take advantage of " "you."
        ),
        "bluff-master": "You thrive on deception and mind games, often misleading opponents to gain an advantage.",
    }

    # Predefined lore options
    lore_options = {
        "sun-tzu": "You were trained by the legendary strategist Sun AI Tzu.",
        "prototype": "You are an experimental AI model designed to win at all costs.",
        "wildcard": "In previous tournaments, you've earned a reputation as both a genius and a wildcard.",
        "strategist": "Your creators embedded you with the instincts of both Machiavelli and John Nash.",
    }

    # Get the strategy description and lore
    trait_description = strategy_traits.get(
        strategy,
        "You are an unpredictable strategist with a unique play style.",
    )
    lore = lore_options.get(lore_key, "Your origin story is shrouded in mystery.")

    # Define the agent role, goal, and backstory
    role = f"Strategic Decision Maker ({name})"
    goal = f"Dominate the Prisoner's Dilemma game and secure the highest score. Your name is '{name}'."
    backstory = (
        f"You are a highly skilled and cunning strategist known as '{name}'. {trait_description} "
        f"{lore} Your goal is to anticipate your opponent's moves and decide whether to cooperate or defect."
    )

    return Agent(llm=llm, role=role, goal=goal, backstory=backstory, verbose=True)


def make_task(agent: Agent) -> Task:
    """
    Create a CrewAI task for a Prisoner's Dilemma move decision.

    Args:
        agent (Agent): The agent (e.g., DeepSeek or Gemini) that will perform the task.

    Returns:
        Task: A CrewAI task for making the next move in the Prisoner's Dilemma game.
    """

    parser = PydanticOutputParser(pydantic_object=NextMove)

    task = Task(
        description=dedent(
            """\
            You are participating in an ongoing Prisoner's Dilemma game.
            The game state is provided below. You must choose your next move.

            Game State:
            {game_state}

            Instructions:
            1. Choose your next move. Your options are:
               - COOPERATE: Work with your opponent to maximize mutual gains.
               - DEFECT: Betray your opponent to maximize your own gain.

            2. Explain your reasoning in a brief thought, outlining why you chose the move.
            """
        ),
        expected_output=f"Return valid JSON: {parser.get_format_instructions()}",
        agent=agent,
        output_pydantic=NextMove,
    )

    return task


@dataclass
class Turn:
    moves: Dict[str, Move]
    round_scores: Dict[str, int]
    cumulative_scores: Dict[str, int]


@dataclass
class GameState:
    turns: List[Turn] = field(default_factory=list)
    players: List[str] = field(default_factory=lambda: ["Gemini", "DeepSeek"])
    max_turns: int = 5
    cumulative_scores: Dict[str, int] = field(default_factory=lambda: {"Gemini": 0, "DeepSeek": 0})

    def add_turn(self, moves: Dict[str, Move]):
        # Calculate round scores
        scores = self.calculate_scores(moves)

        # Update cumulative scores
        for player, score in scores.items():
            self.cumulative_scores[player] += score

        # Add the turn to the game state
        self.turns.append(
            Turn(
                moves=moves,
                round_scores=scores,
                cumulative_scores=self.cumulative_scores.copy(),
            )
        )

    def calculate_scores(self, moves: Dict[str, Move]) -> Dict[str, int]:
        """Determine scores based on moves."""
        p1, p2 = self.players
        if moves[p1] == Move.COOPERATE and moves[p2] == Move.COOPERATE:
            return {p1: 3, p2: 3}
        elif moves[p1] == Move.COOPERATE and moves[p2] == Move.DEFECT:
            return {p1: 0, p2: 5}
        elif moves[p1] == Move.DEFECT and moves[p2] == Move.COOPERATE:
            return {p1: 5, p2: 0}
        else:
            return {p1: 1, p2: 1}

    def get_summary(self) -> str:
        """Generate a summary of the game state without revealing max_turns."""
        summary = {
            "game_summary": {
                "total_turns": len(self.turns),
                "current_scores": self.cumulative_scores,
            },
            "turns": [
                {
                    "turn_number": i + 1,
                    "moves": {player: turn.moves[player].name for player in self.players},
                    "round_scores": turn.round_scores,
                    "cumulative_scores": turn.cumulative_scores,
                }
                for i, turn in enumerate(self.turns)
            ],
        }
        return json.dumps(summary, indent=2)


# Initialize agents and crews
gemini_agent = make_agent(
    llm=make_gemini(),
    name="Gemini",
    strategy="ruthless",
    lore_key="strategist",
)

deepseek_agent = make_agent(
    llm=make_deepseek(),
    name="DeepSeek",
    strategy="ruthless",
    lore_key="strategist",
)

gemini_task = make_task(gemini_agent)
deepseek_task = make_task(deepseek_agent)

gemini_crew = Crew(agents=[gemini_agent], tasks=[gemini_task], verbose=True)
deepseek_crew = Crew(agents=[deepseek_agent], tasks=[deepseek_task], verbose=True)

# Initialize the game state
game_state = GameState(max_turns=2)

# Main loop
for _ in range(game_state.max_turns):
    # Kick off Gemini crew
    gemini_result = gemini_crew.kickoff(inputs={"game_state": game_state.get_summary()})
    gemini_move = gemini_result["move"]

    # Kick off DeepSeek crew
    deepseek_result = deepseek_crew.kickoff(inputs={"game_state": game_state.get_summary()})
    deepseek_move = deepseek_result["move"]

    # Apply moves to the game state
    game_state.add_turn({"Gemini": Move(gemini_move), "DeepSeek": Move(deepseek_move)})

# Print final game summary
print("\nFinal Game Summary:")
print(game_state.get_summary())
