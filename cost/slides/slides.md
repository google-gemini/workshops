---
# You can also start simply with 'default'
theme: seriph
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
background: https://cover.sli.dev
# some information about your slides (markdown enabled)
title: Cost of LLMs
info: |
  ## Slidev Starter Template
  Gemini vs. GPT vs. Llama3

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

# Cost of popularity?

## Gemini vs. GPT vs. Llama3

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
transition: fade-out
---

# What's reasonably popular?

<v-clicks>

<figure class="p-5">
  <img src="/apps.png" class="w-3/4 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 1</strong>: Distribution of apps by popularity</figcaption>
</figure>

</v-clicks>

---

# Introducing Vedic astrology!

<v-clicks>

- 100,000 daily active users (DAUs)
- ~120 tokens per user per day (basic)
- ~2,000 tokens per user per day (advanced)
- 5% conversion rate

</v-clicks>

---

# How much would Gemini cost (basic)?

<v-clicks>

- **Basic users (Gemini 1.5 Flash)**
  $$95,000\ \mathrm{basic\ users}$$
- **Tokens per day**
  $$95,000 \times 120\ \mathrm{tokens / user / day} = 11,400,000\ \mathrm{tokens / day}$$
- **Cost per day**
  $$\frac{11,400,000\ \mathrm{tokens / day}}{1,000,000} \times 0.30\ \mathrm{USD} = 3.42\ \mathrm{USD / day}$$
- **Cost per month**
  $$3.42\ \mathrm{USD / day} \times 30\ \mathrm{days} = 102.60\ \mathrm{USD/month}$$

</v-clicks>

---

# How much would Gemini cost (advanced)?

<v-clicks>

- **Advanced users (Gemini 1.5 Pro)**
  $$5,000\ \mathrm{advanced\ users}$$
- **Tokens per day**
  $$5,000 \times 1,750\ \mathrm{tokens / user / day} = 8,750,000\ \mathrm{tokens / day}$$
- **Cost per day**
  $$\frac{8,750,000\ \mathrm{tokens / day}}{1,000,000} \times 10.50\ \mathrm{USD} = 91.875\ \mathrm{USD / day}$$
- **Cost per month**
  $$91.875\ \mathrm{USD / day} \times 30\ \mathrm{days} = 2,756.25\ \mathrm{USD/month}$$

</v-clicks>


---

# How do you make money with Gemini?

<v-clicks>

- **Breakeven**
  $$\frac{2,858.85\ \mathrm{USD / month}}{5,000\ \mathrm{premium\ users}} = 0.5718\ \mathrm{USD / user / month}$$
- **Profit ($5 / premium user)**
  $$5,000\ \text{premium users} \times 5\ \text{USD/month} = 25,000 - 2,858.85 = 22,141.15\ \text{USD/month}$$

</v-clicks>

---

# What about GPT (basic)?

<v-clicks>

- **Basic users (GPT-4o mini)**
  $$95,000\ \mathrm{basic\ users}$$
- **Tokens per day**
  $$95,000 \times 120\ \mathrm{tokens / user / day} = 11,400,000\ \mathrm{tokens / day}$$
- **Cost per day**
  $$\frac{11,400,000\ \mathrm{tokens / day}}{1,000,000} \times 0.60\ \mathrm{USD} = 6.84\ \mathrm{USD / day}$$
- **Cost per month**
  $$6.84\ \mathrm{USD / day} \times 30\ \mathrm{days} = 205.2\ \mathrm{USD/month}$$

</v-clicks>

---

# What about GPT (advanced)?

<v-clicks>

- **Advanced users (GPT-4o)**
  $$5,000\ \mathrm{advanced\ users}$$
- **Tokens per day**
  $$5,000 \times 1,750\ \mathrm{tokens / user / day} = 8,750,000\ \mathrm{tokens / day}$$
- **Cost per day**
  $$\frac{8,750,000\ \mathrm{tokens / day}}{1,000,000} \times 15.00\ \mathrm{USD} = 131.25\ \mathrm{USD / day}$$
- **Cost per month**
  $$131.25\ \mathrm{USD / day} \times 30\ \mathrm{days} = 3,937.5\ \mathrm{USD/month}$$

</v-clicks>

---

# How do you make money with GPT?

<v-clicks>

- **Breakeven**
  $$\frac{4142.7\ \mathrm{USD / month}}{5,000\ \mathrm{premium\ users}} = 0.8285\ \mathrm{USD / user / month}$$
- **Profit ($5 / premium user)**
  $$5,000\ \text{premium users} \times 5\ \text{USD/month} = 25,000 - 4,142.70 = 20,857.3\ \text{USD/month}$$

</v-clicks>

---

# What about Llama3 (basic)?

<v-clicks>

- **Basic users (two A100s)**
  $$95,000\ \mathrm{basic\ users}$$
- **Tokens per day**
  $$95,000 \times 120\ \mathrm{tokens / user / day} = 11,400,000\ \mathrm{tokens / day}$$
- **Cost per day**
  $$\frac{11,400,000\ \mathrm{tokens / day}}{1,000,000} \times 8.87\ \mathrm{USD} = 101.12\ \mathrm{USD / day}$$
- **Cost per month**
  $$101.12\ \mathrm{USD / day} \times 30\ \mathrm{days} = 3,033.60\ \mathrm{USD/month}$$

</v-clicks>

---

# What about Llama3 (advanced)?

<v-clicks>

- **Advanced users (two A100s)**
  $$5,000\ \mathrm{advanced\ users}$$
- **Tokens per day**
  $$5,000 \times 1,750\ \mathrm{tokens / user / day} = 8,750,000\ \mathrm{tokens / day}$$
- **Cost per day**
  $$\frac{8,750,000\ \mathrm{tokens / day}}{1,000,000} \times 8.87\ \mathrm{USD} = 77.66\ \mathrm{USD / day}$$
- **Cost per month**
  $$77.66\ \mathrm{USD / day} \times 30\ \mathrm{days} = 2,329.80\ \mathrm{USD/month}$$

</v-clicks>

---

# How do you make money with Llama3?

<v-clicks>

- **Breakeven (two A100s)**
  $$\frac{5,363.14\ \mathrm{USD / month}}{5,000\ \mathrm{premium\ users}} = 1.07\ \mathrm{USD / user / month}$$
- **Profit ($5 / premium user)**
  $$5,000\ \text{premium users} \times 5\ \text{USD/month} = 25,000 - 5,363.14 = 19,636.60\ \text{USD/month}$$

</v-clicks>

---

# How do they compare?

<div v-click="1">

<v-clicks at="1">
<caption class="text-center text-gray-500 text-sm mt-2 w-full whitespace-normal"><strong>Table 1</strong>: Gemini vs. GPT vs. Llama3</caption>

<table>
  <thead>
    <tr>
      <th></th>
      <th><strong>Gemini</strong></th>
      <th><strong>GPT</strong></th>
      <th><strong>Llama 3</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr v-click=3>
      <td><strong>Basic (USD / month)</strong></td>
      <td>102.60 (1.5 Flash)</td>
      <td>205.2 (4o mini)</td>
      <td>3,033.60</td>
    </tr>
    <tr v-click=4>
      <td><strong>Advanced (USD / month)</strong></td>
      <td>2,756.25 (1.5 Pro)</td>
      <td>3,937.5 (4o)</td>
      <td>2,329.80</td>
    </tr>
    <tr v-click=5>
      <td><strong>Breakeven (USD / month)</strong></td>
      <td>0.5718</td>
      <td>0.8285</td>
      <td>1.07</td>
    </tr>
    <tr v-click=6>
      <td><strong>Profit @ $5 / advanced (USD / month)</strong></td>
      <td>22,141.15</td>
      <td>20,857.3</td>
      <td>19,636.60</td>
    </tr>
  </tbody>
</table>

</v-clicks>

</div>

<style>
  table {
    width: 95%;
    border-collapse: collapse;
    margin-top: 1rem;
  }
  th {
    @apply font-bold p-2 border-b-2 border-t-2 border-black
  }
  th, td {
    padding: 8px;
  }
  thead th {
    border-bottom: 1px solid black;
    border-top: 2px solid black;
  }
  tbody tr {
    border: none;
  }
  tbody tr:last-child {
    border-bottom: 2px solid black;
  }
  caption {
    display: block; /* Ensure caption spans the whole width */
    white-space: normal; /* Ensure text wraps correctly */
  }
</style>

---

# Why go Llama3, then?

<v-clicks>

- **Recoup two purchased A100s @ $5 / premium user**
  $$\frac{24,333.33\ \mathrm{USD/month}}{24,000\ \mathrm{USD}} \approx 0.99\ \mathrm{months}$$

</v-clicks>
