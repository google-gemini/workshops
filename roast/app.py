import streamlit as st
from crewai import Crew

import roast

st.title("AI Roast Battle App")


def format_history(roast_history):
    return "\n".join(f"{turn['speaker']}: {turn['roast']}" for turn in roast_history)


if "roast_history" not in st.session_state:
    st.session_state.roast_history = []


def main():
    roastee = st.text_input("Enter the name of the roastee", "")

    if roastee and "started" not in st.session_state:
        st.session_state.started = True

    if st.session_state.get("started", False):
        gemini_agent = roast.make_agent(roast.make_gemini(), "Gemini", "Grok", roastee)
        grok_agent = roast.make_agent(roast.make_grok(), "Grok", "Gemini", roastee)
        judge_agent = roast.make_judging_agent(roast.make_chatgpt(), "ChatGPT", ["Gemini", "Grok"])

        gemini_task = roast.make_task(gemini_agent)
        grok_task = roast.make_task(grok_agent)
        judging_task = roast.make_judging_task(judge_agent)

        gemini_crew = Crew(agents=[gemini_agent], tasks=[gemini_task], verbose=True)
        grok_crew = Crew(agents=[grok_agent], tasks=[grok_task], verbose=True)
        judge_crew = Crew(agents=[judge_agent], tasks=[judging_task], verbose=True)

        continue_roast = st.button("Roast")

        if continue_roast:
            formatted_roast_only_history = format_history(st.session_state.roast_history)

            # Generate roasts
            gemini_roast = gemini_crew.kickoff(inputs={"roast_history": formatted_roast_only_history})
            st.session_state.roast_history.append({"speaker": "Gemini", "roast": gemini_roast.pydantic.roast})

            formatted_roast_only_history = format_history(st.session_state.roast_history)

            grok_roast = grok_crew.kickoff(inputs={"roast_history": formatted_roast_only_history})
            st.session_state.roast_history.append({"speaker": "Grok", "roast": grok_roast.pydantic.roast})

            # Display in two columns
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Gemini")
                st.write(gemini_roast.pydantic.roast)
                with st.expander("Thoughts"):
                    st.write(gemini_roast.pydantic.thought)

            with col2:
                st.subheader("Grok")
                st.write(grok_roast.pydantic.roast)
                with st.expander("Thoughts"):
                    st.write(grok_roast.pydantic.thought)

            # Judging
            last_exchange = format_history(st.session_state.roast_history[-2:])
            judge_result = judge_crew.kickoff(
                inputs={
                    "roast_history": formatted_roast_only_history,
                    "last_exchange": last_exchange,
                }
            )

            # Judge's decision in expandable sections
            with st.expander("Judge's Winner"):
                st.write(f"**Winner**: {judge_result.pydantic.winner}")

            with st.expander("Judge's Thought"):
                st.write(f"**Thought**: {judge_result.pydantic.thought}")

            st.write("---")  # Separator after the judge's decision

        st.write("\n**Final Roast History:**")
        for entry in st.session_state.roast_history:
            st.write(f"{entry['speaker']}: {entry['roast']}")


if __name__ == "__main__":
    main()
