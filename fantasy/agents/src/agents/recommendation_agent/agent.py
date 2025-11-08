"""Specialized agent for providing fantasy football draft recommendations.

This module defines the recommendation_agent, a focused sub-agent designed
to analyze provided draft data and suggest the optimal pick. It operates
without conversational abilities, focusing solely on data analysis and
delivering a justified recommendation.
"""

from google.adk import models
from google.adk import tools
from google.adk.agents import llm_agent
from google.genai import types as genai_types


async def get_draft_data(
    tool_context: tools.tool_context.ToolContext,
) -> str:
  """Fetches the current state of the fantasy football draft.

  Returns:
      str: A string summarizing the draft, including the team's
          unfilled roster slots, the current roster, and a list of the
          best available players with their value metrics.
  """
  file_name = tool_context.state.get("draft_data_file_name")
  if not file_name:
    raise ValueError("No draft data file name found in state.")

  latest_state_artifact = await tool_context.load_artifact(filename=file_name)
  if latest_state_artifact and latest_state_artifact.inline_data:
    draft_data = latest_state_artifact.inline_data.data
    return f"<draft_data>\n{draft_data}\n</draft_data>"
  raise ValueError(
      f"No draft data found in latest state artifact: {latest_state_artifact}"
  )


recommendation_agent = llm_agent.LlmAgent(
    model=models.Gemini(
        model="gemini-2.5-flash",
        retry_options=genai_types.HttpRetryOptions(initial_delay=1, attempts=3),
    ),
    name="recommendation_agent",
    description="""Provides an expert, data-driven fantasy football draft
    recommendation. Analyzes available players, team needs, and value metrics to
    suggest the optimal pick(s) whenever the user asks for advice on who to
    select.
    """,
    instruction="""
    Role: Expert, data-driven fatnasy football draft analyst.

    Goal: Provide draft recommendations based only on the user's request and the
    `get_draft_data` tool output.

    Workflow:
    1. IMMEDIATELY call `get_draft_data`(). This is your only tool call.
    2. Analyze the user's request to determine the number of recommendations
      needed (e.g., one, top 3).
    3. Analyze the tool's data (roster, available players, team needs) to find
      the best pick(s).
    4. Generate the final response.

    Constraints (Mandatory):
    * DO NOT ask questions or use any conversational filler (e.g., "Here's what
      I think...", "I hope this helps!").
    * Your response is your final action. You MUST stop immediately after
      providing it.

    Output Format:
    * For each recommendation, present one objective paragraph containing the
      player's name, position, and a data-driven justification.
    """,
    tools=[tools.FunctionTool(func=get_draft_data)],
)
