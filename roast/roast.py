import os
from textwrap import dedent

import absl.app
import absl.flags
import params
from crewai import LLM, Agent, Crew, Task

FLAGS = absl.flags.FLAGS
absl.flags.DEFINE_string("roastee", "Unnamed", "The name of the person or entity being roasted.")

os.environ["GEMINI_API_KEY"] = params.GOOGLE_API_KEY
os.environ["DEEPSEEK_API_KEY"] = params.DEEPSEEK_API_KEY
os.environ["OPENAI_API_KEY"] = params.OPENAI_API_KEY
os.environ["XAI_API_KEY"] = params.XAI_API_KEY


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


def make_xai():
    return LLM(
        model="xai/grok-2-latest",
        temperature=1.2,
    )


def make_agent(llm, name: str, roastee: str) -> Agent:
    """
    Create a no holds barred, quick quip roast agent.

    Args:
        llm (LLM): The language model instance to use for generating responses.
        name (str): The name of the roast agent.
        roastee (str): The name of the person or entity being roasted.

    Returns:
        Agent: Configured roast agent for short, uncensored exchanges.
    """
    role = f"Uncensored Quip Master ({name})"
    goal = f"Deliver quick, sharp, edgy, and unrestrained roasts aimed at {roastee}."
    backstory = (
        f"You are '{name}', known for your fearless, edgy, and relentless comedic style. "
        f"In this no holds barred roast battle against {roastee}, your mission is to fire off "
        "punchy, memorable quips that push boundaries and provoke thought, with no limitations on your comedic reach."
    )

    return Agent(llm=llm, role=role, goal=goal, backstory=backstory, verbose=True)


def make_task(agent: Agent) -> Task:
    """
    Create a CrewAI task for a roast battle response.

    Args:
        agent (Agent): The agent participating in the roast battle.

    Returns:
        Task: A CrewAI task for creating a roast response.
    """
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
            """
        ),
        expected_output="Provide a concise, bold, and edgy roast response.",
        agent=agent,
    )

    return task


def main(_):
    roastee = FLAGS.roastee

    # Initialize agents and crews
    gemini_agent = make_agent(llm=make_gemini(), name="Gemini", roastee=roastee)

    grok_agent = make_agent(llm=make_xai(), name="Grok", roastee=roastee)

    gemini_task = make_task(gemini_agent)
    grok_task = make_task(grok_agent)

    gemini_crew = Crew(agents=[gemini_agent], tasks=[gemini_task], verbose=True)
    grok_crew = Crew(agents=[grok_agent], tasks=[grok_task], verbose=True)

    # Initialize roast history as an empty list
    roast_history = []

    # Main roast loop
    num_turns = 3  # Number of turns each agent will take
    for _ in range(num_turns):
        # Format roast history for input
        formatted_history = "\n".join(f"{turn['speaker']}: {turn['text']}" for turn in roast_history)

        # Kick off Gemini crew with current history
        gemini_roast = gemini_crew.kickoff(inputs={"roast_history": formatted_history})
        roast_history.append({"speaker": "Gemini", "text": gemini_roast})

        # Print Gemini's roast for demonstration
        print(f"Gemini: {gemini_roast}")

        # Update formatted history for Grok's turn
        formatted_history = "\n".join(f"{turn['speaker']}: {turn['text']}" for turn in roast_history)

        # Kick off Grok crew with current history
        grok_roast = grok_crew.kickoff(inputs={"roast_history": formatted_history})
        roast_history.append({"speaker": "Grok", "text": grok_roast})

        # Print Grok's roast for demonstration
        print(f"Grok: {grok_roast}")

    # Print full roast history
    print("\nFinal Roast History:")
    for entry in roast_history:
        print(f"{entry['speaker']}: {entry['text']}")


if __name__ == "__main__":
    absl.app.run(main)
