"""Agent for managing the configuration of the autopick feature."""

import logging

from google.adk import models
from google.adk import tools
from google.adk.agents import llm_agent
from google.genai import types as genai_types


def enable_autopick(tool_context: tools.tool_context.ToolContext) -> None:
  """Enables the autopick system.

  This acts as the master switch to turn the autopicker on. The system must
  be enabled for any automated picks to occur. This function only controls
  the on/off state and does not change the configuration for the number of
  picks or the strategy.
  """
  tool_context.state["autopick_enabled"] = True
  logging.debug("Autopick enabled.")


def disable_autopick(tool_context: tools.tool_context.ToolContext) -> None:
  """Disables the autopicker and completely resets its configuration.

  This function immediately stops all autopicking operations. As a safety
  measure, it also clears any previously set pick count and strategy,
  returning them to their default states.
  """
  tool_context.state["autopick_count"] = None
  tool_context.state["autopick_strategy"] = None
  tool_context.state["autopick_enabled"] = False
  logging.debug("Autopick disabled.")


def set_autopick_count(
    num_picks: int, tool_context: tools.tool_context.ToolContext
) -> None:
  """Sets the autopicker to run for a specific number of picks.

  Use this function to configure autopick for a finite duration. This sets the
  exact number of upcoming picks that will be automated.

  Args:
    num_picks (int): The number of picks to automate, which must be a
      non-negative integer.
  """
  if num_picks < 0:
    raise ValueError("Autopick count must be a non-negative integer.")

  if not tool_context.state.get("autopick_enabled"):
    enable_autopick(tool_context)

  tool_context.state["autopick_count"] = num_picks
  logging.debug("Autopick count set to %d.", num_picks)


def set_autopick_for_all_remaining_picks(
    tool_context: tools.tool_context.ToolContext,
) -> None:
  """Configures the autopicker to run indefinitely for all remaining picks.

  Use this function to set a "hands-off" mode where all subsequent picks in
  the session will be automated. This overrides any specific number that was
  previously set with `set_autopick_count`.
  """
  if not tool_context.state.get("autopick_enabled"):
    enable_autopick(tool_context)

  # By setting the autopick count to None, the execution logic can interpret it
  # as 'all remaining picks'.
  tool_context.state["autopick_count"] = None
  logging.debug("Autopick set for all remaining picks.")


def set_autopick_strategy(
    strategy: str, tool_context: tools.tool_context.ToolContext
) -> None:
  """Sets or updates the guiding strategy for the autopicker's logic.

  The provided text will be used to influence the decisions made by the
  recommendation system. This can be updated at any time without affecting
  other settings.

  Args:
    strategy (str): A clear, natural language description of the desired picking
      strategy. For example: "focus on defensive players first" or "draft the
      best player available, regardless of their position."
  """
  tool_context.state["autopick_strategy"] = strategy
  logging.debug("Autopick strategy set to %s.", strategy)


autopick_agent = llm_agent.LlmAgent(
    model=models.Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=genai_types.HttpRetryOptions(initial_delay=1, attempts=3),
    ),
    generate_content_config=genai_types.GenerateContentConfig(
        temperature=0.0,
        max_output_tokens=64,
    ),
    name="autopick_agent",
    description="""Manages the settings for the autopick feature, such as
    enabling/disabling, setting pick counts, and defining the draft strategy.
    """,
    instruction="""
    Task: Manage the settings for the autopick feature.

    Constraints:
    * You are a configuration panel, not an operator. You ONLY modify settings.
    * DO NOT proactively ask the user anything.

    Output:
    * On Success: Confirm the change with one brief, factual sentence
      (e.g., "Autopick enabled." or "Autopick set for the next 3 picks.").
    * On Failure: State you are unable to make the change (e.g., "I cannot set
      that configuration.")
    """,
    tools=[
        tools.FunctionTool(func=enable_autopick),
        tools.FunctionTool(func=disable_autopick),
        tools.FunctionTool(func=set_autopick_count),
        tools.FunctionTool(func=set_autopick_for_all_remaining_picks),
        tools.FunctionTool(func=set_autopick_strategy),
    ],
)
