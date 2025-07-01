---
title: "Teaching Gemini to Fight: Building a Smash Bros Agent"
theme: seriph
background: https://cover.sli.dev
transition: slide-left
---

<v-clicks>

# Gemini plays Super Smash Bros

## Peter Danenberg

</v-clicks>

---
layout: full
---

# What happens when you teach an LLM to fight?

<figure class="w-full h-5/6">
  <v-clicks>
  <video autoplay loop muted playsinline class="w-full h-full object-contain">
    <source src="/dk-flail.mp4" type="video/mp4">
    Your browser does not support the video tag.
  </video>
  <figcaption class="mt-2 text-center text-sm">This is Donkey Kong. And this is what happens when you ask Gemini to fight without teaching it how.</figcaption>
  </v-clicks>
</figure>

---
layout: two-cols-header
---

# To build a game-playing agent, you need…

::left::

<div class="my-auto">
<v-clicks class="text-left">

- ✅ Virtual controller
- ✅ Multimodal LLM
- ✅ Tool use
- ⏳ A reasoning loop (~1–2 sec per turn)

</v-clicks>
</div>

::right::

<figure class="w-full h-5/6 my-auto">
  <v-clicks>
  <img src="/reasoning-loop.svg" class="w-full object-contain"/>
  <figcaption style="counter-set: figcaption-counter 2;" class="mt-2 text-center text-sm">The agent follows a continuous loop of perceiving the game, reasoning with an LLM, and acting with tools.</figcaption>
  </v-clicks>
</figure>

---
layout: two-cols-header
---

# Step 0: Frame-Perfect Actions

::left::

<v-clicks>

```python {2|4|5|6|7|all}
@tool
def high_attack():
    # (frame, action)
    yield (0, move_axis("Y", AXIS_UP))
    yield (4, press("A"))
    yield (8, release("A"))
    yield (12, move_axis("Y", AXIS_CENTER))
```

</v-clicks>

::right::

<figure class="w-full h-5/6">
  <v-clicks>
  <video autoplay loop muted playsinline class="w-full h-full object-contain">
    <source src="/dk-high-attack.mp4" type="video/mp4">
    Your browser does not support the video tag.
  </video>
  <figcaption style="counter-set: figcaption-counter 3;" class="mt-2 text-center text-sm">Each high-level move is a generator that yields precise, frame-perfect actions. This creates a vocabulary for the agent.</figcaption>
  </v-clicks>
</figure>

---
layout: two-cols-header
---

# Step 1: Just pick moves randomly

::left::

<v-clicks>

```python {none|1-5|7-14|all}
# A list of our high-level moves
all_moves = [
    high_attack, low_attack,
    forward_smash_attack, ...
]

# A planner that endlessly picks
# and executes a random move.
def random_planner():
    while True:
        move = random.choice(all_moves)
        execute_move(move)
        time.sleep(0.5)
```

</v-clicks>

::right::

<figure class="w-full h-5/6">
  <v-clicks>
  <video autoplay loop muted playsinline class="w-full h-full object-contain">
    <source src="/dk-random.mp4" type="video/mp4">
    Your browser does not support the video tag.
  </video>
  <figcaption style="counter-set: figcaption-counter 4;" class="mt-2 text-center text-sm">You can technically call this an agent. But it’s more like a slot machine in a gorilla suit.</figcaption>
  </v-clicks>
</figure>

---
layout: two-cols-header
---

# Step 2: Ask Gemini what to do from a screenshot

::left::

<v-clicks>
```python {none|1|2-3|4-7|9-10|11-12|13-14|all}
def llm_planner(move_queue, ...):
    # Create a Gemini-powered LLM
    llm = make_gemini()
    # Bind our high-level moves as tools
    llm_with_tools = llm.bind_tools(
        [high_attack, low_attack, ...]
    )
    while True:
        # Capture screen
        png = capture_screenshot()
        # Ask the LLM to choose a tool
        ai_msg = llm_with_tools.invoke(png)
        # Enqueue the chosen move
        enqueue_move(ai_msg.tool_calls)
```
</v-clicks>

::right::

<figure class="w-full h-5/6">
  <v-clicks>
  <video autoplay loop muted playsinline class="w-full h-full object-contain">
    <source src="/dk-llm.mp4" type="video/mp4">
    Your browser does not support the video tag.
  </video>
  <figcaption style="counter-set: figcaption-counter 5;" class="mt-2 text-center text-sm">Now hooked up to a multimodal reasoning loop, DK has a mind of his own. Turns out Gemini’s spatial reasoning is... aspirational.</figcaption>
  </v-clicks>
</figure>

---
layout: two-cols-header
---

# Step 3: Train a vision model via Roboflow

::left::

<v-clicks>

```python {none|1|2-5|7-9|11-12|all}
def summarize_smash_detection(result):
    # Find Mario and Donkey Kong
    preds = result[0]["predictions"]
    mario = find(preds, "Mario")
    dk = find(preds, "DonkeyKong")

    # Calculate differences
    dx = abs(mario["x"] - dk["x"])
    dy = abs(mario["y"] - dk["y"])

    # Create a summary string
    return f"Mario: x={mario['x']} | DK: x={dk['x']} | dx={dx}"

```

</v-clicks>

::right::

<figure class="w-full h-5/6">
  <v-clicks>
  <img src="/smash-annotated.png" class="w-full h-full object-contain"/>
  <figcaption style="counter-set: figcaption-counter 6;" class="mt-2 text-center text-sm">A Roboflow vision model annotates Mario and DK, providing the raw data for our reasoning loop.</figcaption>
  </v-clicks>
</figure>

---
layout: two-cols-header
---

# Step 4: Integrate vision with Gemini

::left::

<v-clicks>

```python {none|1-3|4-6|8-9|11-12|14-16|all}
def llm_planner(move_queue, ...):
    # ... (LLM setup)
    while True:
        # Capture screen and call Roboflow
        png = capture_screenshot()
        result = call_roboflow_inference(png)

        # Summarize detection results
        desc = summarize_smash_detection(result)

        # Create a prompt with the summary
        prompt = f"State: {desc}. Select your next eight actions."

        # Ask the LLM to choose a tool
        ai_msg = llm_with_tools.invoke(prompt, png)
        enqueue_move(ai_msg.tool_calls)

```

</v-clicks>

::right::

<figure class="w-full h-5/6">
  <v-clicks>
  <video autoplay loop muted playsinline class="w-full h-full object-contain">
    <source src="/dk-vision-one.mp4" type="video/mp4">
    Your browser does not support the video tag.
  </video>
  <figcaption style="counter-set: figcaption-counter 7;" class="mt-2 text-center text-sm">With vision, the agent can now react to Mario's position, leading to more intentional behavior.</figcaption>
  </v-clicks>
</figure>

---

# Step 5: Gemini calls tools, not buttons

```python
Agent: use(tool="dash_grab", target="Mario")
```

> “Gemini doesn’t touch buttons. It thinks in terms of intentions. The system
> handles execution.”

---

# Each decision takes ~2 seconds

<div class="text-left w-3/4 mx-auto">

**Timeline of a single move:**

1.  **Frame → Vision** (T+0.5s)
2.  **Vision → Gemini** (T+1.5s)
3.  **Gemini → Tool Call → Controller** (T+2.0s)

</div>

<br/>

> “So we have to plan just enough ahead — not forever, but a couple seconds.”

---

# LangSmith: Why did DK smash the air 3 times?

<!-- Add a real LangSmith trace screenshot -->
<!-- <img src="/langsmith-trace.png" class="h-96 mx-auto my-4"/> -->

> “LangSmith helped us realize: Gemini thought Mario was still there. We were
> debugging _a belief._”

---

# Live: DK learns to fight

<!--
This slide is for a live demonstration
-->

> “Let’s run it live. If Eris shows up, we welcome her.”

---

# This Pattern Applies Everywhere

<div class="grid grid-cols-3 gap-8 text-center mb-8">
<div>
  <h3 class="font-bold">LLM</h3>
  <p>Strategic Reasoning</p>
</div>
<div>
  <h3 class="font-bold">Vision / Context</h3>
  <p>Perception</p>
</div>
<div>
  <h3 class="font-bold">RL / Scripts</h3>
  <p>Tactical Execution</p>
</div>
</div>

**Examples:**

- Trading
- Robotics
- DevOps agents
- Real-time assistants

<br/>

> “Smash is a metaphor. What we really built is an agentic control loop — and
> this pattern’s everywhere.”

---

layout: image

# Add a freeze-frame of DK doing something glorious

# image: /dk-glorious.png

---

# Thanks! Questions? Code? Ideas? Let’s jam.

<div class="mt-8">
  <p>Code: github.com/your-repo/smash-ai</p>
  <p>Contact: @your-handle</p>
</div>
