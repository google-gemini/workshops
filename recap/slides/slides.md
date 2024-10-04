---
# You can also start simply with 'default'
theme: seriph
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
background: https://cover.sli.dev
# some information about your slides (markdown enabled)
title: Gemini retrospective
info: |
  ## Slidev Starter Template
  Presentation slides for developers.

  Learn more at [Sli.dev](https://sli.dev)
# apply unocss classes to the current slide
class: text-center
# https://sli.dev/features/drawing
drawings:
  persist: false
# slide transition: https://sli.dev/guide/animations.html#slide-transitions
transition: slide-left
# enable MDC Syntax: https://sli.dev/features/mdc
mdc: true
---

<v-clicks>

# What have we learned from Gemini?

## Lessons from the Wild West

Peter Danenberg

</v-clicks>

<div class="abs-br m-6 flex gap-2">
  <a href="https://github.com/google-gemini/workshops" target="_blank" alt="GitHub" title="Open in GitHub"
    class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon-logo-github />
  </a>
</div>

<!--
The last comment block of each slide will be treated as slide notes. It will be visible and editable in Presenter Mode along with the slide. [Read more in the docs](https://sli.dev/guide/syntax.html#notes)
-->

---
layout: two-cols-header
---

# Join our Gemini workshops!

::left::

<v-clicks>

<div class="relative h-full w-full">
  <div class="">
    <img src="/meetup.png" class="h-full w-full object-cover rounded shadow-lg" style="object-position: top;" />
  </div>
</div>

</v-clicks>

::right::

<figure class="p-5">
  <img src="/meetup-qr.png" class="w-4/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 1</strong>: <a href="https://lu.ma/geminimeetup">lu.ma/geminimeetup</a></figcaption>
</figure>

---
layout: two-cols-header
---

# Nurse triage

::left::

<v-clicks>

- Gemma and Gemini can coexist in the same stack.
- Gemma does triage (cheap) and Gemini formulates final response (expensive).
- Latency for voice interactions relatively high.

</v-clicks>

::right::

<figure class="p-5">
  <img src="/gemma.png" class="w-4/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 2</strong>: <a href="https://github.com/klutometis/hello-gemma">github.com/klutometis/hello-gemma</a></figcaption>
</figure>

---
layout: two-cols-header
---

# Day-trading

::left::

<v-clicks>

- Gemini is great at high-level strategy.
- Also great at parsing unstructured data (10-Qs, etc.).
- Latency too high to execute high-speed trades.

</v-clicks>

::right::

<figure class="p-5">
  <img src="/day-trading.png" class="w-4/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 3</strong>: <a href="https://klutometis.github.io/gemini-trading">klutometis.github.io/gemini-trading</a></figcaption>
</figure>

---
layout: two-cols-header
---

# Persona

::left::

<v-clicks>

- Gemini is great at staying in character.
- Sherlock Holmes still thought he was at Baker Street.
- Don't overdo the training data (100s of examples instead of 10,000s).

</v-clicks>

::right::

<figure class="p-5">
  <img src="/persona.png" class="w-4/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 4</strong>: <a href="https://klutometis.github.io/gemini-persona">klutometis.github.io/gemini-persona</a></figcaption>
</figure>

---
layout: two-cols-header
---

# Multi-player games

::left::

<v-clicks>

- Gemini can develop a theory of mind.
- It learns from data and adjusts strategy in real time.
- It has a finite attention span.

</v-clicks>

::right::

<figure class="p-5">
  <img src="/games.png" class="w-4/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 5</strong>: <a href="https://google-gemini.github.io/workshops/games">google-gemini.github.io/workshops/games</a></figcaption>
</figure>

---
layout: two-cols-header
---

# Vedic matchmaking

::left::

<v-clicks>

- Gemini can process millions of tokens.
- It can implement non-trivial algorithms.
- Requires oversight for sensitive results.

</v-clicks>

::right::

<figure class="p-5">
  <img src="/matchmaking.png" class="w-4/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 6</strong>: <a href="https://github.com/google-gemini/workshops/tree/main/kundali">google-gemini/workshops/tree/main/kundali</a></figcaption>
</figure>

---
layout: two-cols-header
---

# Factuality

::left::

<v-clicks>

- Gemini can stay up-to-date by grounding in search.
- Search helps ensure that results are factual.
- Check against search for ungrounded claims.

</v-clicks>

::right::

<figure class="p-5">
  <img src="/factuality.png" class="w-4/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 7</strong>: <a href="https://klutometis.github.io/factuality">klutometis.github.io/factuality</a></figcaption>
</figure>

---
layout: two-cols-header
---

# Cost

::left::

<v-clicks>

- Gemini is cheaper than GPT is cheaper than open source.
- Vertex AI includes replication, uptime guarantees.
- Won't train on customer data.

</v-clicks>

::right::

<figure class="p-5">
  <img src="/cost.png" class="w-4/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 8</strong>: <a href="https://klutometis.github.io/workshops/cost">klutometis.github.io/workshops/cost</a></figcaption>
</figure>

---
layout: two-cols-header
---

# Video games

::left::

<v-clicks>

- Gemini can generate playable Super Mario Brothers levels.
- The levels get more sophisticated with more data.
- Gemini has the last laugh.

</v-clicks>

::right::

<figure class="p-5">
  <iframe width="560" height="315" src="https://www.youtube.com/embed/6fCr_C1UuCs?si=bXx6-QQky9q55vDq" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 9</strong>: Gemini generates Super Mario Brothers levels.</figcaption>
</figure>

---
layout: two-cols-header
---

# Join our Gemini workshops!

::left::

<v-clicks>

<div class="relative h-full w-full">
  <div class="">
    <img src="/meetup.png" class="h-full w-full object-cover rounded shadow-lg" style="object-position: top;" />
  </div>
</div>

</v-clicks>

::right::

<figure class="p-5">
  <img src="/meetup-qr.png" class="w-4/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 9</strong>: <a href="https://lu.ma/geminimeetup">lu.ma/geminimeetup</a></figcaption>
</figure>
