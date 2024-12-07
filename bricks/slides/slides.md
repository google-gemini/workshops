---
# You can also start simply with 'default'
theme: seriph
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
background: https://cover.sli.dev
# some information about your slides (markdown enabled)
title: Gemini Builds Bricks
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

# Gemini Builds Bricks

<v-clicks>

## The most expensive set in the world

Peter Danenberg

</v-clicks>

<div class="abs-br m-6 flex gap-2">
  <a href="https://github.com/google-gemini/workshops" target="_blank" alt="GitHub" title="Open in GitHub"
    class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon-logo-github />
  </a>
  <a href="https://www.linkedin.com/in/peterdanenberg/" target="_blank" alt="LinkedIn" title="Connect on LinkedIn"
    class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon-logo-linkedin />
  </a>
</div>

<!--
The last comment block of each slide will be treated as slide notes. It will be visible and editable in Presenter Mode along with the slide. [Read more in the docs](https://sli.dev/guide/syntax.html#notes)
-->

---
transition: fade-out
---

# How do you describe sets?

<v-clicks>

```
0 FILE 10001 - model B - main.ldr
0 model B - main
0 Name: 10001 - model B - main.ldr
0 Author: Robert Paciorek [bercik]
0 !LDRAW_ORG Model
0 !LICENSE Redistributable under CCAL version 2.0 : see CAreadme.txt
0 !HISTORY 2018-01-12 [bercik] model B based on model A by Zoltank82
0 !HISTORY 2018-01-08 [bercik] OMR version by Robert Paciorek [bercik] with perrmision of Zoltank82
1 8 162 0 36 1 0 0 0 1 0 0 0 1 2865.DAT
1 8 482 0 36 1 0 0 0 1 0 0 0 1 2865.DAT
1 8 162 0 -1564 1 0 0 0 1 0 0 0 1 2865.DAT
1 8 482 0 -1564 1 0 0 0 1 0 0 0 1 2865.DAT
1 8 798.072021 0 20.628 1 0 0.195 0 1 0 -0.195 0 1 2867.DAT
1 8 1086.457031 0 -98.823997 0.831 0 0.556 0 1 0 -0.556 0 0.831 2867.DAT
1 8 1307.176025 0 -319.542999 0.556 0 0.831 0 1 0 -0.831 0 0.556 2867.DAT
1 8 1426.629028 0 -607.927979 0.195 0 1 0 1 0 -0.981 0 0.195 2867.DAT
1 8 -782.627991 0 -607.927979 0.195 0 -0.981 0 1 0 1 0 0.195 2867.DAT
1 8 -663.176025 0 -319.542999 0.556 0 -0.831 0 1 0 0.831 0 0.556 2867.DAT
1 8 -442.457001 0 -98.823997 0.831 0 -0.556 0 1 0 0.556 0 0.831 2867.DAT
1 8 -154.072006 0 20.629 1 0 -0.195 0 1 0 0.195 0 1 2867.DAT
1 8 1426.628052 0 -920.072021 -0.195 0 1 0 1 0 -0.981 0 -0.195 2867.DAT
```

</v-clicks>

---

# How do they render?

<v-clicks>

<figure class="p-5">
<img src="/render.png" class="mx-auto p-5 max-h-[66vh] max-w-full object-contain" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 1</strong>: A rendered brick set.</figcaption>
</figure>

</v-clicks>

---

# How do you train the model?

<v-clicks>

```json {1|2-11|12-19}
  "var/rendered/10001-1_B-Model-from-Instruction.mpd": {
    "description": "This build is a classic train set featuring a
      sleek, modern locomotive and two accompanying cars. The train is
      primarily black with white and red accents, giving it a stylish,
      streamlined appearance. It runs on an oval track layout, perfect
      for continuous play. The first car appears to be a passenger car
      with windows for realistic detail, while the second is a cargo car
      capable of carrying goods. The set is equipped with small details
      like antennas and lights on top of the train, adding to its
      authenticity. This build invites imaginative journeys across
      miniature landscapes.",
    "queries": [
      "Build a modern train with passenger and cargo cars.",
      "Create a train set with an oval track layout.",
      "Design a sleek locomotive with realistic details.",
      "Craft a concept for transporting goods by rail.",
      "Make a detailed train for miniature adventures."
    ]
  },
```

</v-clicks>

---

# How much does it cost to train the model?

<v-clicks>

- _O(thousands)_ of examples
- Modulo sets > 32,000 tokens
- Times 5 queries each
- <span v-mark.circle.red="{ at: 5 }">$20,000</span>

</v-clicks>

---

# What the hell is this?

<figure class="p-5">
<v-clicks>
<img src="/portrait-temperature-2.png" class="mx-auto p-5 max-h-[66vh] max-w-full object-contain" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 2</strong>: Self-portrait <code>@ temperature = 2</code></figcaption>
</v-clicks>
</figure>

---

# What about this?

<figure class="p-5">
<v-clicks>
<img src="/portrait-temperature-1.png" class="mx-auto p-5 max-h-[66vh] max-w-full object-contain" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 3</strong>: Self-portrait <code>@ temperature = 1</code></figcaption>
</v-clicks>
</figure>

---

# And this?

<figure class="p-5">
<v-clicks>
<img src="/portrait-temperature-0.5.png" class="mx-auto p-5 max-h-[66vh] max-w-full object-contain" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 4</strong>: Self-portrait <code>@ temperature = 0.5</code></figcaption>
</v-clicks>
</figure>

---

# And this?

<figure class="p-5">
<v-clicks>
<img src="/chatgpt.png" class="mx-auto p-5 max-h-[66vh] max-w-full object-contain" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 5</strong>: ChatGPT <code>@ temperature = 1</code></figcaption>
</v-clicks>
</figure>

---

# And this?

<figure class="p-5">
<v-clicks>
<img src="/trump.png" class="mx-auto p-5 max-h-[66vh] max-w-full object-contain" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 6</strong>: Trump serving fries at McDonald's <code>@ temperature = 1</code></figcaption>
</v-clicks>
</figure>

---

# And this?

<figure class="p-5">
<v-clicks>
<img src="/cat.png" class="mx-auto p-5 max-h-[66vh] max-w-full object-contain" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 7</strong>: Cat <code>@ temperature = 1</code></figcaption>
</v-clicks>
</figure>

---

# And this?

<figure class="p-5">
<v-clicks>
<img src="/home-temperature-1.png" class="mx-auto p-5 max-h-[66vh] max-w-full object-contain" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 8</strong>: Home <code>@ temperature = 1</code></figcaption>
</v-clicks>
</figure>

---

# And this?

<figure class="p-5">
<v-clicks>
<img src="/home-temperature-0.5.png" class="mx-auto p-5 max-h-[66vh] max-w-full object-contain" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 9</strong>: Home <code>@ temperature = 0.5</code></figcaption>
</v-clicks>
</figure>

---

# And this?

<figure class="p-5">
<v-clicks>
<img src="/body-temperature-1.png" class="mx-auto p-5 max-h-[66vh] max-w-full object-contain" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 10</strong>: Body <code>@ temperature = 1</code></figcaption>
</v-clicks>
</figure>

---

# And this?

<figure class="p-5">
<v-clicks>
<img src="/body-temperature-0.5.png" class="mx-auto p-5 max-h-[66vh] max-w-full object-contain" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 10</strong>: Body <code>@ temperature = 0.5</code></figcaption>
</v-clicks>
</figure>

---

# And this?

<figure class="p-5">
<v-clicks>
<img src="/mind-temperature-1.png" class="mx-auto p-5 max-h-[66vh] max-w-full object-contain" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 11</strong>: Mind <code>@ temperature = 1</code></figcaption>
</v-clicks>
</figure>

---

# And this?

<figure class="p-5">
<v-clicks>
<img src="/mind-temperature-0.5.png" class="mx-auto p-5 max-h-[66vh] max-w-full object-contain" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 12</strong>: Mind <code>@ temperature = 0.5</code></figcaption>
</v-clicks>
</figure>

---

# And lastly?

<figure class="p-5">
<v-clicks>
<img src="/universe.png" class="mx-auto p-5 max-h-[66vh] max-w-full object-contain" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 12</strong>: Universe <code>@ temperature = 1</code></figcaption>
</v-clicks>
</figure>
