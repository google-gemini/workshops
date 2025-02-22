import streamlit as st

import roast

st.title("AI Roast Battle App")


def format_history(roast_history):
    return "\n".join(f"{turn['speaker']}: {turn['roast']}" for turn in roast_history)


def main():
    roastee = st.text_input("Enter the name of the roastee", "Elon")

    if st.button("Let the roast begin!"):
        gemini_agent = roast.make_agent(roast.make_gemini(), "Gemini", "Grok", roastee)
        grok_agent = roast.make_agent(roast.make_grok(), "Grok", "Gemini", roastee)
        judge_agent = roast.make_judging_agent(roast.make_chatgpt(), "ChatGPT", ["Gemini", "Grok"])

        gemini_task = roast.make_task(gemini_agent)
        grok_task = roast.make_task(grok_agent)
        judging_task = roast.make_judging_task(judge_agent)

        gemini_crew = roast.Crew(agents=[gemini_agent], tasks=[gemini_task], verbose=True)
        grok_crew = roast.Crew(agents=[grok_agent], tasks=[grok_task], verbose=True)
        judge_crew = roast.Crew(agents=[judge_agent], tasks=[judging_task], verbose=True)

        roast_history = []

        num_turns = 3
        for _ in range(num_turns):
            formatted_roast_only_history = format_history(roast_history)

            gemini_roast = gemini_crew.kickoff(inputs={"roast_history": formatted_roast_only_history})
            roast_history.append({"speaker": "Gemini", "roast": gemini_roast})
            st.write(f"Gemini: {gemini_roast}")

            formatted_roast_only_history = format_history(roast_history)

            grok_roast = grok_crew.kickoff(inputs={"roast_history": formatted_roast_only_history})
            roast_history.append({"speaker": "Grok", "roast": grok_roast})
            st.write(f"Grok: {grok_roast}")

            last_exchange = format_history(roast_history[-2:])
            judge_result = judge_crew.kickoff(
                inputs={
                    "roast_history": formatted_roast_only_history,
                    "last_exchange": last_exchange,
                }
            )

            st.write(
                f"\nJudge's Decision:\nWinner: {judge_result.pydantic.winner}\nThought: {judge_result.pydantic.thought}"
            )

        st.write("\nFinal Roast History:")
        for entry in roast_history:
            st.write(f"{entry['speaker']}: {entry['roast']}")


if __name__ == "__main__":
    main()
