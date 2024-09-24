---
# You can also start simply with 'default'
theme: seriph
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
background: https://cover.sli.dev
# some information about your slides (markdown enabled)
title: LLMs why now?
info: |
  Past, present, future of LLMs
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

# LLMs: Why Now?

## Peter Danenberg

<div class="abs-br m-6 flex gap-2">
  <button @click="$slidev.nav.openInEditor()" title="Open in Editor" class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon:edit />
  </button>
  <a href="https://github.com/slidevjs/slidev" target="_blank" alt="GitHub" title="Open in GitHub"
    class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon-logo-github />
  </a>
</div>

<!--
The last comment block of each slide will be treated as slide notes. It will be visible and editable in Presenter Mode along with the slide. [Read more in the docs](https://sli.dev/guide/syntax.html#notes)
-->

---
transition: fade-out
layout: section
---

# Where did LLMs come from?

<!--
Brief history of LLMs; where they came frame; state of the art.
-->

---

# Timeline of LLMs

<v-clicks>

<div style="width: 100%; max-width: 1200px; margin: 0 auto; overflow: hidden;">
  <iframe
    src='https://cdn.knightlab.com/libs/timeline3/latest/embed/index.html?source=19gFSR7FjiNNvA00PXdJxZRPJYNqdVlEpVQ4V3cMe4Cs&font=Default&lang=en&initial_zoom=2&height=400'
    style="width: 100%; height: 400px; border: none;"
    webkitallowfullscreen
    mozallowfullscreen
    allowfullscreen>
  </iframe>
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 1</strong>: LLMs from paper to production</figcaption>
</div>

</v-clicks>

<!--
Tay was not an LLM; but became a warning for reputational risk
of chatbots.

Transformers paper, paved the way for LLMs; came out in 2017.

Google announces first true LLM, LaMDA, in 2021; what happened in the
mean time? Working on scaling; taking a paper and productionizing a
lot of work: infrastructure, data, efficient training algorithms,
development of new chips, etc.

ChatGPT in 2022; and Gemini in 2023. What a difference a couple months
makes!
-->

---
layout: section
---

# What can LLMs do now?

---

# Medical triage in rural areas

<v-clicks>

- In Turkana County, LLMs can guide rural health workers in diagnosing common
  diseases like malaria via mobile apps, reducing the need for travel to distant
  clinics.

</v-clicks>

<!--
Kenya, 1 doctor for every 65,000 people
-->

---

# Preservation of languages

<v-clicks>

- LLMs trained on Dinka can create educational tools and translations, helping
  preserve the language for future generations.

</v-clicks>

<!--
South Sudan
-->

---

# Multilingual government communication

<v-clicks>

- An LLM can translate voter education materials into Yoruba, Igbo, and Hausa,
  making government information accessible to non-English speakers during
  elections.

</v-clicks>

<!--
Nigeria, 500 languages
-->

---

# Disaster response

<v-clicks>

- LLMs can provide flood warnings and evacuation routes in both Portuguese and
  Umbundu, ensuring rural communities stay informed during the rainy season.

</v-clicks>

<!--
Angola
-->

---

# Agricultural support

<v-clicks>

- In Southern Province, LLMs could provide drought-resistant crop advice in
  Tonga, helping farmers sustain maize production during dry seasons.

</v-clicks>

<!--
Zambia
-->

---

# Education and remote learning

<v-clicks>

- LLMs could offer math and science lessons in Bajan Creole, supporting students
  in rural areas with remote learning resources.

</v-clicks>

<!--
Barbados
-->

---

# Legal document simplification

<v-clicks>

- LLMs could explain land ownership laws in Lozi, helping rural communities
  navigate the process of obtaining legal land titles.

</v-clicks>

<!--
Zambia
-->

---
layout: section
---

# Where are LLMs going?

<!--
Future of LLMs might fall into one of three scenarios, like the future of the universe (perpetually expanding, contracting, or achieving equilibrium).
-->

---

# LLM super-intelligence

<figure class="p-5" v-click="1">
  <div class="wrapper w-full max-w-xl mx-auto p-5 overflow-visible"> <!-- Set overflow to visible -->
    <AnimatableSvg svgFile="/hockey-stick.svg" />
  </div>
  <figcaption class="mt-2 text-center text-sm text-gray-500" v-click="2">
    <strong>Figure 2</strong>: The "hockey-stick" trajectory would be the equivalent of LLMs achieving <span v-mark.highlight.yellow="{ at: 3 }">runaway self-improvement</span>.
  </figcaption>
</figure>

<!--
LLMs achieve super-human intelligence; new physics; inter-planetary travel; etc.
-->

---

# LLM saturation

<figure class="p-5" v-click="1">
  <div class="wrapper w-full max-w-xl mx-auto p-5 overflow-visible"> <!-- Set overflow to visible -->
    <AnimatableSvg svgFile="/fixed-point.svg" />
  </div>
  <figcaption class="mt-2 text-center text-sm text-gray-500" v-click="2">
    <strong>Figure 3</strong>: This is the scenario where LLMs reach a kind of <span v-mark.highlight.yellow="{ at: 3 }">saturation point</span>—having learned everything they can from human-generated data.
  </figcaption>
</figure>

<!--
LLMs peter out after the saturation of training data.
-->

---

# LLM collapse

<figure class="p-5" v-click="1">
  <div class="wrapper w-full max-w-xl mx-auto p-5 overflow-visible"> <!-- Set overflow to visible -->
    <AnimatableSvg svgFile="/decay.svg" />
  </div>
  <figcaption class="mt-2 text-center text-sm text-gray-500" v-click="2">
    <strong>Figure 4</strong>: This scenario occurs if LLMs start relying heavily on synthetic data, which could lead to <span v-mark.highlight.yellow="{ at: 3 }">model collapse</span>.
  </figcaption>
</figure>

<!--
Due to over-reliance on synthetic data, LLMs collapse.
-->

---

# Let's connect!

<figure class="p-5">
  <img src="/linkedin.png" class="w-2/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 5</strong>: <a href="https://www.linkedin.com/in/peterdanenberg/">linkedin.com/in/peterdanenberg</a></figcaption>
</figure>
