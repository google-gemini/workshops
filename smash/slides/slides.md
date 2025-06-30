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

<div v-click class="prose my-auto">

> Sounds simple, right? Let’s see how it actually goes.

</div>

---
layout: two-cols-header
---

# Step 0: Frame-Perfect Actions

::left::

<v-clicks>

First, we define a vocabulary of high-level moves. Each move is a Python
generator that `yield`s a sequence of low-level controller actions at precise
frame intervals.

This lets our agent think in terms of “high attack” instead of “move stick up,
wait 4 frames, press A...”.

</v-clicks>

::right::

<v-click at="+1">

```python {2|4|5|6|7|all}
@tool
def high_attack():
    # (frame, action)
    yield (0, move_axis("Y", AXIS_UP))
    yield (4, press("A"))
    yield (8, release("A"))
    yield (12, move_axis("Y", AXIS_CENTER))
```

</v-click>

---

# Step 1: Just press buttons randomly

```python
import random

def random_move():
    return random.choice(["jump", "left", "smash", "roll"])
```

<!-- You can embed a video here of DK flailing -->
<!-- <video src="/dk-flailing.mp4" autoplay loop controls muted class="w-2/3 mx-auto"></video> -->

> “You can technically call this an agent. But it’s more like a slot machine in
> a gorilla suit.”

---

# Step 2: Ask Gemini what to do from a screenshot

> You are Donkey Kong. What move should you make?

<!-- Add video clip of DK walking offstage -->
<!-- <video src="/dk-walks-offstage.mp4" autoplay loop controls muted class="w-2/3 mx-auto"></video> -->

> “Turns out Gemini’s spatial reasoning is... aspirational.”

---

# Step 3: Add a vision model via Roboflow

<div class="grid grid-cols-2 gap-4">
<div>

<!-- Add side-by-side image: original screen + bounding boxes -->

A screenshot with bounding boxes around characters would go here.

</div>
<div>

```python
mario_pos = detect("Mario", screen)
prompt = f"You're Donkey Kong. Mario is {mario_pos}. What do you do?"
```

</div>
</div>

<!-- Add video clip of DK punching Mario -->
<!-- <video src="/dk-punches-mario.mp4" autoplay loop controls muted class="w-2/3 mx-auto"></video> -->

> “This tiny model fixed everything. DK can now _see_ Mario and act
> accordingly.”

---

# Step 4: High-level strategy → Frame-perfect action

<div class="grid grid-cols-2 gap-8">
<div>

### Gemini response

```json
ledge_guard()
```

</div>
<div>

### Frame-timed input chart

<!-- Diagram showing frame-by-frame inputs for each move. -->

</div>
</div>

> “We give Gemini a vocabulary of high-level moves and queue up the
> frame-perfect inputs behind the scenes.”

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
