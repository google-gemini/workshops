---
# You can also start simply with 'default'
theme: seriph
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
background: https://cover.sli.dev
# some information about your slides (markdown enabled)
title: Welcome to Slidev
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
---

# LLM super-intelligence

<figure class="p-5" v-click="1">
  <div class="wrapper w-full max-w-xl mx-auto p-5 overflow-visible"> <!-- Set overflow to visible -->
    <AnimatableSvg svgFile="/hockey-stick.svg" />
  </div>
  <figcaption class="mt-2 text-center text-sm text-gray-500" v-click="2">
    <strong>Figure 1</strong>: The "hockey-stick" trajectory would be the equivalent of LLMs achieving <span v-mark.highlight.yellow="{ at: 3 }">runaway self-improvement</span>.
  </figcaption>
</figure>

---

# LLM saturation

<figure class="p-5" v-click="1">
  <div class="wrapper w-full max-w-xl mx-auto p-5 overflow-visible"> <!-- Set overflow to visible -->
    <AnimatableSvg svgFile="/fixed-point.svg" />
  </div>
  <figcaption class="mt-2 text-center text-sm text-gray-500" v-click="2">
    <strong>Figure 2</strong>: This is the scenario where LLMs reach a kind of <span v-mark.highlight.yellow="{ at: 3 }">saturation point</span>—having learned everything they can from human-generated data.
  </figcaption>
</figure>

---

# LLM collapse

<figure class="p-5" v-click="1">
  <div class="wrapper w-full max-w-xl mx-auto p-5 overflow-visible"> <!-- Set overflow to visible -->
    <AnimatableSvg svgFile="/decay.svg" />
  </div>
  <figcaption class="mt-2 text-center text-sm text-gray-500" v-click="2">
    <strong>Figure 3</strong>: This scenario occurs if LLMs start relying heavily on synthetic data, which could lead to <span v-mark.highlight.yellow="{ at: 3 }">model collapse</span>.
  </figcaption>
</figure>
