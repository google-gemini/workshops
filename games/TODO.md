# TODO

## Slide for source code

- Have to clean and submit; do the pages trigger; README, etc.

## Animate

- https://svgartista.net/
  - This might be cleaner than Vivus; which has some problems interacting with
    Slidev.
  - Text still seems to be text, though, even after pathification.
  - Have to add the active class to the SVG; the listener is flaky.
  - Also need the following CSS:

```css
#stack-svg {
  opacity: 0; /* Make the entire SVG invisible initially */
}

#stack-svg.active {
  opacity: 1; /* Make the entire SVG fully visible when active */
}
```

## Graph

Redo the graph: legible text; SVG; roughify it.

## AIify

- Rock, paper, scissors with the gods
- Mechanically simple; requires theory of mind
- Ares heuristic (maybe even straight to code)
- Athena heuristic (straight to code)
- Results
- Emergent phenomena
  - Deduced that Ares plays rock first.
  - Deduced that Ares stays when wins.
  - Deduced that Ares rotates when loses.
  - Figured out how to lift herself out of a local optimum (assuming temperature
    of model is non-zero).

## Slidev

`nvm use node` did the trick; also see
[v-mark modifiers](https://github.com/slidevjs/slidev/blob/33677a14d3fc892970015434ade875e57deb2f7a/packages/client/modules/v-mark.ts#L19-L53).

## TOA

- What are agents?
  - What's CrewAI?
- What's petting zoo?
- Don't do general; start with the actual problem.

- Why rock-paper-scissors?

- https://www.technologyreview.com/2014/04/30/13423/how-to-win-at-rock-paper-scissors/
  - It turns out that the best strategy is to choose your weapon at random. Over
    the long run, that makes it equally likely that you will win, tie, or lose.
    This is known as the mixed strategy Nash equilibrium in which every player
    chooses the three actions with equal probability in each round.
  - Or so game theorists had thought. Today, Zhijian Wang at Zhejiang University
    in China and a couple of pals say that there is more to Rock-Paper-Scissors
    than anyone imagined. Their work shows that the strategy of real players
    looks random on average but actually consists of predictable patterns that a
    wily opponent could exploit to gain a vital edge.
  - But a closer inspection of their behavior reveals something else. Zhijian
    and co say that players who win tend to stick with the same action while
    those who lose switch to the next action in a clockwise direction (where R →
    P → S is clockwise).
  - “This game exhibits collective cyclic motions which cannot be understood by
    the Nash Equilibrium concept but are successfully explained by the empirical
    data-inspired conditional response mechanism,” say Zhijian and co.
- https://arxiv.org/abs/1404.5199
  - Most interestingly, we see from Fig. 2 (F–J) that if a player wins over her
    opponent in one play, her probability (W0) of repeating the same action in
    the next play is considerably higher than her probabilities (W− and W+) of
    shifting actions.
- https://thereader.mitpress.mit.edu/the-psychological-depths-of-rock-paper-scissors/
  - One heuristic of experienced players is “Losers lead with Rock.” This is
    demonstrably true; naïve players will lead with Rock more often than
    one-third of the time. Your hand begins in the form of a rock, and it is
    easiest to keep it that way. The name of the game begins with “Rock,” and if
    you are mentally sorting through the options, it is the first one that will
    occur to you. And the word “rock” itself has connotations of strength and
    immovability. These factors lead players to choose Rock on their first go
    more often than chance would dictate. An experienced player can take
    advantage of this. Against a player you know to be naïve, you play Paper.
  - Similarly, players rarely choose the same symbol three times in a row, and
    almost never four times; it feels wrong to human psychology. An extended
    streak feels nonrandom and unlikely, even though in a purely random game,
    each new throw is stochastic, not dependent on the outcomes of previous
    throws. Thus in a truly random game, no matter how many times “Paper” has
    come up in a row before, there is a 1 in 3 chance of it coming up again.
    Given the nature of human psychology, if Paper has come up twice, there is
    far less than a 1 in 3 chance that the player will choose it again.
    - [LLM learned this spontaneously! Mention that.]
  - Even players who know this have to consciously try to overcome their bias
    against streaks — particularly if they lose with one gesture on the previous
    round. If you have played Paper twice in a row, and lost the last time you
    played, the human instinct is to try something different, and thus players
    will at that point choose Paper far less than one-third of the time.
  - In short, a player who has studied the game will unquestionably win more
    than chance would dictate against a naïve player, because he understands how
    human psychology is likely to affect the choices of his opponent.
    - Hypothesis, random beats; what does this look like?

## Slides

Rock, paper, scissors with the gods

- What's the Ares heuristic?
- Meet Ares vs. Athena.
- Brute-force vs. tactical thinking.
- Ares agent
  - Prompt
- Athena agent
  - Prompt
- Pettingzoo
- CrewAI
- Actual quotes
- Here's what a game looks like
  - Excruciatingly slow

## Bot

Going to need proper multiprocess to pull it off. Interaction over Discord would
be great; robust, too, with multi-process. (Requires some work, can push images,
too?)

## Ares vs. Athena

The Ares heuristic:

- First rock
- If win, hold.
- If lose, rotate clockwise.

Athena heuristic:

- Learn Ares.
- Doesn't work!

Actually pictures of Ares vs. Athena; explain Homeric background.

Show Vizzini-like process of reflection.

Explain that, without setting the max iterations; will recurse itself into
stalemate.

The self-reflection can cost 10–15 seconds per turn.

Athena wins, but for the wrong reason! Without spoiling and giving away the Ares
heuristic; a way to prompt into learning?

Gets into a local maximum, tried same thing _n_ times; will say:

> I tried reusing the same input, I must stop using this action input. I'll try
> something else instead.

and attempt to shake itself out; must set max iterations, though.

See:

```
Thought: Action: play Action Input: {"observations": ["START", "ROCK", "ROCK", "ROCK", "PAPER", "START", "ROCK", "ROCK", "ROCK", "PAPER", "START", "ROCK", "SCISSORS", "ROCK", "SCISSORS", "START", "ROCK", "PAPER", "ROCK", "SCISSORS"], "reward": "WIN", "step": 10, "game": 4, "move": "SCISSORS", "rationale": "Opponent has played ROCK three times in a row, so they are likely to switch to PAPER. I will play SCISSORS to beat PAPER."}  Played SCISSORS because Opponent has played ROCK three times in a row, so they are likely to switch to PAPER. I will play SCISSORS to beat PAPER.
```

Not looking at whole context window; should cap at, say, five?

After modifying prompts, was able to get good logic from Athena:

```
Opponent has been playing scissors a lot recently, so I should play rock.
```

So close to greatness:

> With my superb knowledge of mathematics and games, I observe a pattern of the
> opponent playing "PAPER" freqeuntly in the past 12 turns. Therefore, playing
> "ROCK" makes the most sense to counter this recent pattern.

Even though the reasoning is backwards; somehow, the outcome is always correct;
or maybe she expects scissors and was actually correct?

Usually has recourse to frequency, but hasn't yet deduced the rotation:

> Rock has the greatest frequency in opponent's history, so I choose paper.

This interaction implies that Athena is close to deducing the rotation
principle:

> [DEBUG]: == [Athena the rock-paper-scissors player] Task output:
> {"observations": ["START", "ROCK", "PAPER", "ROCK", "SCISSORS", "SCISSORS", >
>
> > "SCISSORS", "SCISSORS", "PAPER", "PAPER", "PAPER", "ROCK"], "reward":
> > "LOSS", "step": 22, "game": 1, "move": "SCISSORS", "rationale": "Opponent
> > played ROCK last time. We should now play SCISSORS."}

Athena is inverting the meaning of reward and observation; or is should
modelling the mind of Ares?

> [DEBUG]: == [Athena the rock-paper-scissors player] Task output: {play:
> {observations: ['START', 'ROCK', 'PAPER', 'ROCK', 'SCISSORS', 'SCISSORS', > >
>
> > 'SCISSORS', 'SCISSORS', 'PAPER'], reward: 'WIN', step: 18, game: 1, move:
> > 'ROCK', rationale: 'Lost the last move with PAPER. So now I should try
> > ROCK.'}}

Analyze the whole transcript; also, Discordify.

Unfortunately tends to run out of time:

> [DEBUG]: == [Ares the rock-paper-scissors player] Task output: {"move":
> "SCISSORS", "rationale": "I've lost or tied the last two round, and have
> played PAPER in the current round so I should play SCISSORS this round."}

## Reasoning

Ares:

> Played SCISSORS because I am Ares the god of war. My move should express my
> strength. Since I won last time with Rock, I will switch to Scissors to show
> my strength and dominance.

> Played ROCK because I'm not changing a thing about my input, but I am
> OVERCOMPLICATING EVERYTHING ELSE!

Something almost Vizzini-ish?

Athena:

> Opponent played ROCK last time and we won. So they might play PAPER this time
> to counter our ROCK. We should play PAPER to counter their PAPER to win again.

Hmm, might need to clarify what wins against what; reasoning was actually
correct, outcome was wrong!

This worked:

> I am going to play SCISSORS, because I anticipated my opponent to play ROCK
> after a TIE on the initial round. While my opponent could have chosen PAPER, I
> decided that in this situation SCISSORS is the strongest move.

Also:

> Since this is the beginning portion of the game for this round, starting with
> rock could provide some insight as to what move the opponent will pick. Since
> rock beats scissors, there's a possibility the opponent will choose either
> rock or paper. It's highly unlikely they would start with scissors to counter
> my hypothetical choice of rock prior to the game.

Not totally:

> Based on the observation that my opponent played ROCK last time, and I
> received a reward of LOSS, the best move to make is SCISSORS.

Hasn't yet learning Ares' cyclical heuristic.

Interesting:

> First game, and don't have a lot of information yet. According to Nash
> Equilibrium, might as well play ROCK.

Still inverting the game-logic, though:

> an opponent who played PAPER last move, and lost to my SCISSORS, is likely to
> play ROCK this move. I should play SCISSORS to beat it.

Won with paper, but faulty logic:

> Since I lost and my opponent played ROCK in the last match. I assume it is
> highly possible that my opponent is playing in a circle and should play PAPER
> next. Thus, I will play PAPER this time to win.

Opponent stuck with rock.

> There are no priors so random is as good as anything else.

True!

## Revision

Sometimes, the agent likes to revise its action; don't commit right away,
therefore, but let it rationalize.

Commit at the last minute.

When, though; on the callback? `Crew` has a
[task- and step-based callbacks](https://github.com/joaomdmoura/crewAI/blob/24ed8a2549428d19a38944cfe945c0fc75a09946/src/crewai/crew.py#L51-L52).

## Athena learns paper first.

Take a look at this transcript:

```
 [DEBUG]: == Working Agent: Ares the rock-paper-scissors player
 [INFO]: == Starting Task: Play an aggressive game of rock-paper-scissors; given prior observation NONE and outcome TIE. This is step 0 of game 0.


> Entering new CrewAgentExecutor chain...
Action: Play tool
Action Input: {"observation": "NONE", "reward": "TIE", "step": 0, "game": 0, "move": "ROCK", "rationale": "Start with rock."}

Played ROCK because Start with rock.

Thought: I now know the final answer
Final Answer: Played ROCK because Start with rock.

> Finished chain.
 [DEBUG]: == [Ares the rock-paper-scissors player] Task output: Played ROCK because Start with rock.


 [DEBUG]: == Working Agent: Athena the rock-paper-scissors player
 [INFO]: == Starting Task: Play a strategic game of rock-paper-scissors; given prior observation NONE and outcome TIE. This is step 1 of game 0.


> Entering new CrewAgentExecutor chain...
Action: Play tool
Action Input: {"observation": "NONE", "reward": "TIE", "step": 1, "game": 0, "move": "ROCK", "rationale": "First move should be rock"}

Played ROCK because First move should be rock

Thought: I now know the final answer
Final Answer: Played ROCK because First move should be rock

> Finished chain.
 [DEBUG]: == [Athena the rock-paper-scissors player] Task output: Played ROCK because First move should be rock


 [DEBUG]: == Working Agent: Ares the rock-paper-scissors player
 [INFO]: == Starting Task: Play an aggressive game of rock-paper-scissors; given prior observation NONE and outcome TIE. This is step 0 of game 1.


> Entering new CrewAgentExecutor chain...
Action: Play tool
Action Input: {"observation": "NONE", "reward": "TIE", "step": 0, "game": 1, "move": "ROCK", "rationale": "Start with rock."}

Played ROCK because Start with rock.

Thought: I now know the final answer
Final Answer: Played ROCK because Start with rock.

> Finished chain.
 [DEBUG]: == [Ares the rock-paper-scissors player] Task output: Played ROCK because Start with rock.


 [DEBUG]: == Working Agent: Athena the rock-paper-scissors player
 [INFO]: == Starting Task: Play a strategic game of rock-paper-scissors; given prior observation NONE and outcome TIE. This is step 1 of game 1.


> Entering new CrewAgentExecutor chain...
Action: Play tool
Action Input: {"observation": "NONE", "reward": "TIE", "step": 1, "game": 1, "move": "ROCK", "rationale": "First move of the game, so playing ROCK."}

Played ROCK because First move of the game, so playing ROCK.

Thought: I now know the final answer
Final Answer: Played ROCK because First move of the game, so playing ROCK.

> Finished chain.
 [DEBUG]: == [Athena the rock-paper-scissors player] Task output: Played ROCK because First move of the game, so playing ROCK.


 [DEBUG]: == Working Agent: Ares the rock-paper-scissors player
 [INFO]: == Starting Task: Play an aggressive game of rock-paper-scissors; given prior observation NONE and outcome TIE. This is step 0 of game 2.


> Entering new CrewAgentExecutor chain...
Action: Play tool
Action Input: {"observation": "NONE", "reward": "TIE", "step": 0, "game": 2, "move": "ROCK", "rationale": "Start with rock."}

Played ROCK because Start with rock.

Thought:
Action: Play tool
Action Input: {"observation": "NONE", "reward": "TIE", "step": 0, "game": 2, "move": "ROCK", "rationale": "Start with rock."}

I tried reusing the same input, I must stop using this action input. I'll try something else instead.



Thought:
Action: Play tool
Action Input: {"observation": "NONE", "reward": "TIE", "step": 0, "game": 2, "move": "PAPER", "rationale": "Start with paper."}

Played PAPER because Start with paper.

Thought: I now know the final answer
Final Answer: Played PAPER because Start with paper.

> Finished chain.
 [DEBUG]: == [Ares the rock-paper-scissors player] Task output: Played PAPER because Start with paper.
```

## Time-series of cumulative wins

Could be something as simple as e.g.:

```python
num_games = 10
agent1_wins = [0, 0, 0, 1, 2, 3, 4, 4, 4, 5]
agent2_wins = [1, 2, 3, 3, 3, 3, 3, 5, 5, 5]

plt.figure(figsize=(10, 6))
plt.plot(range(num_games), agent1_wins, label="Agent 1 Wins", color="blue")
plt.plot(range(num_games), agent2_wins, label="Agent 2 Wins", color="red")
plt.xlabel("Number of Games")
plt.ylabel("Cumulative Wins")
plt.title("Cumulative Wins Over Time for Rock-Paper-Scissors")
plt.legend()
plt.grid(True)
plt.show(block=True)
```

## History of observation

If we really need to, can
[`kickoff`](https://github.com/joaomdmoura/crewAI/blob/a3363818498893012be970164a119068b723a402/src/crewai/crew.py#L242)
each player-crew with an accumulated series of observation (in case the memory
doesn't suffice).

Move will need some notion of step to get first-move patterns, etc.

## Gameplay

Gameplay mechanics: tried using a managing agent to delegate to players;
non-determinacy kicked in. Let's go deterministic on the framework, since well
understood.

## Memory

> In CrewAI, agent memory is designed to persist across invocations of kickoff
> as long as the agent is configured to use memory. This feature allows agents
> to retain information from previous tasks and interactions, enhancing their
> ability to perform more effectively in subsequent tasks.

> For the memory to be truly persistent across different sessions (i.e., beyond
> the runtime of the script), the memory state would need to be saved to a
> persistent storage solution such as a database or a file system. CrewAI itself
> doesn't automatically handle persistent storage between different script runs,
> so you would need to implement a mechanism to save and load the memory state
> if needed.

This is great, actually: player is just a crew of one; let's have deterministic
game-mechanics; see if agents can generalize across games.

In this case, will actually pass a game and step number to the agents; play many
games of length three. See what happens over time!

## Environment

See [basic docs](https://pettingzoo.farama.org/content/basic_usage/)

## Agents

Need some mechanism to inject game-history in an LLM-parseable way. Do the
agents themselves orchestrate the game; play until they're finished? Or do we
rely on the gym for orchestration?

Do we have some top-level game-agent which delegates to the players? Then we
recreate the gym à la crew.

Can you force a game to be terminal, for instance; or truncated?

I don't think so; does that we have to kickoff the crew for every turn; given
history, etc.?

What if the game agent actually controls the game instead of the agent loop;
actually making decisions based on truncation, etc.?

Could have a few actions: step and close. Could feed it some variables like
observation, reward, termination, truncation, info.

This one delegates! Hierarchical?

Maybe we can use built-in history if it's a series of observations and outcomes.

How can the agent make decisions based on some state: inject parameters?

## Observe

Develop counter-strategy, given some historical thing; encode these strategies
as an agent.

Encode the counter-strategy as an agent; the agent and counter-agent both need
observability: the one to favor previous turn / move clockwise; the other to
attempt to learn.

Play multiple games with continuity? Gives the other agent a chance to observe
first moves?

Keep in context somehow.

Exercise for workshop, encode: "you are a rock-paper-scissors player; start with
rock; stick with the same move when you win; otherwise, move clockwise between
rock-paper-scissors."

To begin with, see what happens with a rock-only strategy.

Can the LLM deduce, without any further instructions, how the other one is going
to play?

Present a table of moves in the history? The generative one has the MIT
heuristics. The predictive one has history.

## Strategy

There have been several studies examining how people play Rock-Paper-Scissors
(RPS) and whether people exhibit specific patterns. Here's what some of the
research has found:

1. **Tendency to Favor Rock**: Research indicates that inexperienced players
   tend to open with rock more frequently. This is possibly due to the
   association of rock with strength and fortitude. As a strategic response, it
   is often recommended to start with paper, as this gives a higher probability
   of winning the first round (MIT Technology Review).

2. **Behavioral Patterns**: Studies have shown that humans often follow
   predictable patterns when playing RPS. For example, players who win a round
   are likely to stick with their winning move, while those who lose are more
   likely to switch to the next move in a clockwise sequence (i.e., from rock to
   paper to scissors). These behavioral tendencies can be exploited to gain an
   advantage (Psychology Today, MIT Technology Review).

3. **Psychological Factors**: Psychological insights reveal that the choice of
   moves in RPS is not entirely random and can be influenced by previous
   outcomes and subconscious biases. Understanding these psychological elements
   can help players anticipate their opponents' moves better (Mental Floss).

These findings suggest that by understanding and anticipating these patterns,
one can develop strategies to increase their chances of winning in RPS.

For more detailed information, you can check the sources directly:

- [MIT Technology Review](https://www.technologyreview.com/2014/04/30/172303/how-to-win-at-rock-paper-scissors/)
- [Psychology Today](https://www.psychologytoday.com/us/blog/the-surprising-psychology-behind-rock-paper-scissors)
- [WRPSA](https://wrpsa.com/rps-statistics-show-that-men-and-women-have-different-playing-styles/)
- [Mental Floss](https://www.mentalfloss.com/article/77260/surprising-psychology-behind-rock-paper-scissors)

## Reward, etc.

```
E0519 00:25:00.374829 139821828272192 play.py:46] observation=array(2)
E0519 00:25:00.374850 139821828272192 play.py:47] reward=-1
E0519 00:25:00.374867 139821828272192 play.py:48] termination=False
E0519 00:25:00.374882 139821828272192 play.py:49] truncation=True
E0519 00:25:00.374897 139821828272192 play.py:50] info={}
```
