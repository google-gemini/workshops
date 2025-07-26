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

import absl.app
import absl.flags
from crewai import Crew

import roast

FLAGS = absl.flags.FLAGS
absl.flags.DEFINE_string("roastee", "Unnamed", "The name of the person or entity being roasted.")


def main(_):
    roastee = FLAGS.roastee

    # Initialize agents and crews
    gemini_agent = roast.make_agent(llm=roast.make_gemini(), name="Gemini", opponent="Grok", roastee=roastee)

    grok_agent = roast.make_agent(llm=roast.make_grok(), name="Grok", opponent="Gemini", roastee=roastee)

    # Initialize a judging agent
    judge_agent = roast.make_judging_agent(llm=roast.make_chatgpt(), name="ChatGPT", judgees=["Gemini", "Grok"])

    gemini_task = roast.make_task(gemini_agent)
    grok_task = roast.make_task(grok_agent)
    judging_task = roast.make_judging_task(judge_agent)

    gemini_crew = Crew(agents=[gemini_agent], tasks=[gemini_task], verbose=True)
    grok_crew = Crew(agents=[grok_agent], tasks=[grok_task], verbose=True)
    judge_crew = Crew(agents=[judge_agent], tasks=[judging_task], verbose=True)

    # Initialize roast history as an empty list
    roast_history = []

    # Main roast loop
    num_turns = 3  # Number of turns each agent will take
    for _ in range(num_turns):
        # Format roast history excluding thoughts for input
        formatted_roast_only_history = roast.format_history(roast_history)

        # Kick off Gemini crew with current history
        gemini_roast = gemini_crew.kickoff(inputs={"roast_history": formatted_roast_only_history})
        roast_history.append({"speaker": "Gemini", "roast": gemini_roast})

        # Print Gemini's roast for demonstration
        print(f"Gemini: {gemini_roast}")

        # Update formatted history for Grok's turn
        formatted_roast_only_history = roast.format_history(roast_history)

        # Kick off Grok crew with current history
        grok_roast = grok_crew.kickoff(inputs={"roast_history": formatted_roast_only_history})
        roast_history.append({"speaker": "Grok", "roast": grok_roast})

        # Print Grok's roast for demonstration
        print(f"Grok: {grok_roast}")

        # Judging phase
        last_exchange = f"Gemini: {roast_history[-2]['roast']}\nGrok:" f" {roast_history[-1]['roast']}"
        judge_result = judge_crew.kickoff(
            inputs={
                "roast_history": formatted_roast_only_history,
                "last_exchange": last_exchange,
            }
        )

        # Print judge's decision
        print(
            f"\nJudge's Decision:\nWinner: {judge_result.pydantic.winner}\nThought:" f" {judge_result.pydantic.thought}"
        )

    # Print full roast history
    print("\nFinal Roast History:")
    for entry in roast_history:
        print(f"{entry['speaker']}: {entry['roast']}")


if __name__ == "__main__":
    absl.app.run(main)
