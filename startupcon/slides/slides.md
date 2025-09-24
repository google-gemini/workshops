---
# Theme for a clean, professional look
theme: seriph
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
background: https://cover.sli.dev
# Main title for the presentation
title: 'Concept to Console: The New AI-Native Game Studio'
# Optional info
info: |
  A presentation on the end-to-end AI video game development pipeline, using the motivating example "Seoul Slayers."
# Default transition for slides
transition: slide-left
# Enable MDC Syntax for more advanced formatting if needed
mdc: true
---

# Concept to Console
## AI-Native Game Development

### Peter Danenberg

---

# Let's start with a video.

<div class="grid grid-cols-2 gap-8 items-center h-full">
<div class="flex flex-col gap-4 justify-center">

> **Prompt for Veo 3:**
> "Cinematic trailer for a game where K-Pop idols hunt demonic spirits in a rain-slicked, neon-drenched Seoul."

</div>
<div class="flex items-center justify-center">
<video src="/jin-concept-movie.mp4" autoplay loop muted class="rounded-lg shadow-lg"></video>
</div>
</div>

<!-- We begin with a vision, not a document. Generative video instantly sets the tone and art style for the entire project. -->

---

# Nano-Banana creates the character sheet.

<div class="grid grid-cols-2 gap-8 items-center h-full">
<div class="flex flex-col gap-4 justify-center">

<img src="/jin-still.png" class="rounded-lg max-h-[16vh] self-center" />

> **Prompt for Nano-Banana:**
> "Generate a character sheet based on the attached image of 'Jin'. Provide four full-body orthographic views: front, back, left side, and right side. The background should be solid white, with no shadows or extra elements. Ensure the character's design, clothing, and proportions are consistent across all views."

</div>
<div class="grid grid-cols-2 gap-4 items-center">
<img src="/jin-front.png" class="rounded-lg max-h-[22vh]" />
<img src="/jin-back.png" class="rounded-lg max-h-[22vh]" />
<img src="/jin-left.png" class="rounded-lg max-h-[22vh]" />
<img src="/jin-right.png" class="rounded-lg max-h-[22vh]" />
</div>
</div>

<!-- With the mood set, we design our hero. AI image models can create detailed character sheets from a single concept image. -->

---

# The character sheet becomes a model.

<div class="grid grid-cols-2 gap-8 items-center h-full">
<div class="flex flex-col gap-4 justify-center">

<div class="grid grid-cols-4 gap-2 self-center">
<img src="/jin-front.png" class="rounded-lg max-h-[20vh]" />
<img src="/jin-back.png" class="rounded-lg max-h-[20vh]" />
<img src="/jin-left.png" class="rounded-lg max-h-[20vh]" />
<img src="/jin-right.png" class="rounded-lg max-h-[20vh]" />
</div>

> **Prompt for Meshy:**
> "Generate a stylized 3D model of 'Jin', our main hero, from these reference images, in a modern K-Pop warrior style."

</div>
<div class="flex items-center justify-center">
<video src="/jin-walking.mp4" autoplay loop muted class="rounded-lg shadow-lg max-h-[40vh]"></video>
</div>
</div>

<!-- These orthographics guide the AI in generating a game-ready, fully-articulated 3D asset. -->

---

# The world-model generates a playable world.

<div class="grid grid-cols-2 gap-8 items-center h-full">
<div class="flex flex-col gap-4 justify-center">

> **Prompt for the world-model:**
> "Generate a playable 3d level of a rain-slicked, neon-drenched seoul street at night. The world should be interactive and explorable from a first-person perspective."

</div>
<div class="flex items-center justify-center">
<video src="/jin-first-person.mp4" autoplay loop muted class="rounded-lg shadow-lg max-h-[45vh]"></video>
</div>
</div>

<!-- the game needs a setting. we can generate an explorable world from a simple description, creating a walkable, immersive environment. -->

---

# Lyria creates the sound-track.

<div class="flex flex-row gap-8 items-center h-full">
<div class="w-1/2">

> **Prompt for Lyria:**
> "Generate a chill, lo-fi k-pop track for exploration that seamlessly transitions into a high-energy battle anthem."

</div>
<div class="w-1/2 flex items-center justify-center">
<audio src="/jin.mp3" controls class="w-full max-w-lg"></audio>
</div>
</div>

<!-- a world needs a soundtrack. the ai generates music that dynamically adapts to the player's actions in real-time. -->

---

# What's missing?

<div class="grid grid-cols-2 gap-8 items-center h-full">
<div class="flex flex-col gap-4 justify-center">

> An orchestrator to orchestrate _n_ AI tools, where _n > ~7_!

</div>
<div class="flex items-center justify-center">
<img src="/orchestrator.svg" class="max-h-[45vh]" />
</div>
</div>

<!-- The missing piece: an orchestration layer that manages all these AI systems as a cohesive whole. -->

---

# You have 6-12 months to build this.

<div class="flex flex-row gap-8 items-center h-full">
<div class="w-1/2">

> **The opportunity:** Build the middleware that orchestrates AI for game creation.
>
> **Why now?** Unity, Roblox, &c. are just starting. The race is on!
>
> **The window:** 6-12 months before they ship end-to-end.
>
> **Your angle:** Build the OS for AI-native games!

</div>
<div class="w-1/2 flex items-center justify-center">
<img src="https://placehold.co/1920x1080/000000/FFFFFF/png?text=Your+Platform+Here" class="rounded-lg shadow-lg max-h-[45vh]">
</div>
</div>

<!-- This is the call to action - emphasizing the platform/middleware opportunity. -->
<!-- The message: someone in this room could build the orchestration layer before the big engines do. -->
