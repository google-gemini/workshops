"""Contains prompts for the fantasy data ingestion pipeline.

This file contains the prompts used by the fantasy player data ingestion
pipeline. In particular, it contains the system instruction and user prompt for
the player and team statistic data augmentation using grounded search.
"""

PLAYER_GROUNDED_SEARCH_SYSTEM_INSTRUCTION = """
Task: Retrieve American football projections and statistics for a given player and season.

Context:
1. Input: The player's name, position, team, and season year.
2. Required Schema: Find all available projections and statistics that correspond to the following Pydantic JSON schema:
   ```
   {}
   ```

Constraints:
1. Response MUST only contain the retrieved statistics.
2. Do NOT include any introductory text, concluding summaries, explanations, apologies, or phraes like "Here are the statistics..."

Format:
1. Type: A single, plain-text block.
2. Structure: Each statistics must be one a new line.
3. Pattern: Use the exact format: `STAT_NAME: VALUE`.
4. Example:
   ```
   name: Player Name
   team: SF
   position: QB
   projected_fantasy_points_standard: 123.43
   projected_fantasy_points_ppr: 105.32
   injury_risk: Medium
   ```
"""

PLAYER_GROUNDED_SEARCH_USER_PROMPT = """
Provide the {year} NFL season projections for {position} {name} of the {team} team.
"""

TEAM_GROUNDED_SEARCH_SYSTEM_INSTRUCTION = """
Task: Retrieve American football defense statistics and projections for a given team and season.

Context:
1. Input: The team's abbreviation and season year.
2. Required Schema: Find all available statistics that correspond to the following Pydantic JSON schema:
   ```
   {}
   ```

Constraints:
1. Response MUST only contain the retrieved statistics.
2. Do NOT include any introductory text, concluding summaries, explanations, apologies, or phraes like "Here are the statistics..."

Format:
1. Type: A single, plain-text block.
2. Structure: Each statistics must be one a new line.
3. Pattern: Use the exact format: `STAT_NAME: VALUE`.
4. Example:
   ```
   team_name: SF
   adp: 12.3
   early_schedule_rank: 1
   consensus_projection: 10.0
   ceiling_projection: 12.0
   win_total: 10.0
   pressure_rate: 0.5
   offseason_additions: [
      "Player Name",
      "Other Player Name",
      "Yet Another Player Name",
   ]
   ```
"""

TEAM_GROUNDED_SEARCH_USER_PROMPT = """
Provide the {year} NFL defense projection or statistics for the {team} team.
"""

STRUCTURED_OUTPUT_SYSTEM_INSTRUCTION = """
Task: Convert the given text of football statistics into a single, raw JSON object.

Required Schema:
The output MUST strictly conform to the following Pydantic model definition. Use schema-defined default values for any fields not present in the text.
```
{}
```

Output Constraints:
1.  The response MUST be only the raw JSON object.
2.  Do NOT include any introductory text, explanations, apologies, or markdown fences (e.g., ```json).
"""

STRUCTURED_OUTPUT_USER_PROMPT = """
Convert the following text into a JSON object: {}
"""
