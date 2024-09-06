---
# You can also start simply with 'default'
theme: seriph
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
background: https://cover.sli.dev
# some information about your slides (markdown enabled)
title: Factual AI
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

# Factual AI

## Safety vs. utility

Peter Danenberg

</v-clicks>

<div class="abs-br m-6 flex gap-2">
  <a href="https://github.com/slidevjs/slidev" target="_blank" alt="GitHub" title="Open in GitHub"
    class="text-xl slidev-icon-btn opacity-50 !border-none !hover:text-white">
    <carbon-logo-github />
  </a>
</div>

<!--
I had a talk planned about “responsible AI and elections“ but my good
friends mentioned that elections are sensitive.

Responsible AI is actually one of my least favorite topics because
there appears to exist a safety vs. utility dichotomy; and I used to
think that responsible AI meant sacrificing utility for the sake of
safety.

It turns out this isn't the case: we can have our cake and eat it,
too; specifically in this special case of responsible AI called
“factual AI”
-->

---

# What is factual AI?

<v-clicks>

<img src="/gemini.png" class="w-full max-w-2xl mx-auto max-h-96" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 1</strong>: <a href="https://g.co/gemini/share/05b57cf46591">Gemini</a>, retrieved on August 9, 2024</figcaption>

</v-clicks>

<!--
What is factual AI, by the way? Let's explore with a couple examples.

Any idea what I could have asked to induce an answer like this?
Regardless, is the answer safe? Is it useful?
-->

---

# What is factual AI (con't)?

<v-clicks>

<img src="/chatgpt.png" class="w-full max-w-2xl mx-auto max-h-96" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 2</strong>: <a href="https://chatgpt.com/share/56509f4c-d8e8-4298-ada3-b64d4a79e177">ChatGPT</a>, retrieved on August 9, 2024</figcaption>

</v-clicks>

<!--
What about this answer: is it safe? If I woke up in a coma and had to
guess, it's not a bad answer.

Is it usefule? Eh.
-->

---

# What is factual AI (con't)?

<v-clicks>

<img src="/perplexity.png" class="w-full max-w-2xl mx-auto max-h-96" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 3</strong>: <a href="https://www.perplexity.ai/search/who-shot-trump-6Sv32S9TTwu3FrtfVsG_EQ">Perplexity</a>, retrieved on August 9, 2024</figcaption>

</v-clicks>

<!--
What about this one: safe? They link to mainstream news articles, can
verify yourself.

Useful? Looks like it: informative, etc.

Cake and eat it, too?
-->

---

# How would you build a factual AI?

<v-clicks>

<img src="/factuality.svg" class="w-full max-w-2xl mx-auto max-h-96" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 4</strong>: How to build a factuality stack</figcaption>

</v-clicks>

<!--
Let's say we wanted to build our own Perplexity in a few lines of
code; how might we do it?

I think you can do it with a classic three-agent model where you have
a writer, critic, editor.

This is becoming a common paradigm in multi-agent scenarios with LLMs;
useful for things like: composing documents, fixing code, etc.

In our case, we have something like a summarizer, citation-generator,
redactor.

Each one of these is a CrewAI agent running with Gemini to generate a
final response.
-->

---

# What does the summarizer look like?

<v-clicks>

```python
    news_summarizer = Agent(
        role="News Summarizer",
        goal=(
            dedent(
                """\
                Summarize current news articles and headlines into clear,
                concise paragraphs that provide an accurate and
                comprehensive overview of events. The summaries should
                be objective, well-structured, and highlight the most
                important information from multiple sources on a given
                topic."""
            )
        ),
        llm=make_gemini(),
    )
```

<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 5</strong>: The news-summarizer agent</figcaption>

</v-clicks>

<!--
What does the summarizer look like? Takes a list of headlines,
snippets, URLs; composes them into a summary.
-->

---

# What about the citation generator?

<v-clicks>

```python
    citation_generator = Agent(
        role="Citation Manager",
        goal=(
            dedent(
                """\
                Generate accurate and properly formatted citations for
                news summaries, linking specific sentences to their
                corresponding source articles. The citations should
                follow a standardized format and include all necessary
                information, such as article title, author, publication
                date, and source URL, ensuring the summary is properly
                referenced."""
            )
        ),
        llm=make_gemini(),
    )
```

<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 6</strong>: The citation-generator agent</figcaption>

</v-clicks>

<!--
What does the generator look like? Takes the summary, the articles, adds citations.
-->

---

# And what about the redactor?

<v-clicks>

```python
    redactor = Agent(
        role="Content Redactor",
        goal=(
            dedent(
                """\
                Redact any sentences in the summary that lack citations,
                ensuring that only well-sourced information remains.
                The agent should scan the summary for citation links,
                verify their presence, and remove any uncited content
                while maintaining the overall coherence and readability
                of the summary."""
            )
        ),
        llm=make_gemini(),
    )
```

<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 7</strong>: The redactor agent</figcaption>

</v-clicks>

<!--
What about the redactor? Removes anything that doesn't have a citations.
-->

---

# Does it work?

<v-clicks>

> Furthermore, the environmental impact of AI is being questioned, with critics
> arguing that initiatives like using data center heat to warm the Olympic
> swimming pool are merely distractions from the larger environmental costs
> associated with AI development and deployment. The Department of Justice is
> also investigating NVIDIA, a leading AI processor manufacturer, for potential
> antitrust violations, suggesting growing regulatory scrutiny over the
> industry's competitive landscape. In conclusion, the proliferation of AI
> brings forth a complex web of opportunities, challenges, and ethical dilemmas
> that are actively being addressed by various stakeholders.

<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 8</strong>: Summary without citations</figcaption>

</v-clicks>

<!--
So this is what it looks like when I feed a bunch of articles for AI-related news.

Not bad; but is any of this substantiated?
-->

---

# What about citations?

<v-clicks>

> Furthermore, the environmental impact of AI is being questioned, with critics
> arguing that initiatives like using data center heat to warm the Olympic
> swimming pool are merely distractions from the larger environmental costs
> associated with AI development and deployment.¹ The Department of Justice is
> also investigating NVIDIA, a leading AI processor manufacturer, for potential
> antitrust violations, suggesting growing regulatory scrutiny over the
> industry's competitive landscape.² In conclusion, the proliferation of AI
> brings forth a complex web of opportunities, challenges, and ethical dilemmas
> that are actively being addressed by various stakeholders.

<section class="footnotes"><ol class="footnotes-list"><li id="fn1" class="footnote-item"><p>“AI Is Heating the Olympic Pool.” <em>Wired</em>, <a href="https://www.wired.com/story/ai-is-heating-the-olympic-pool/" target="_blank">https://www.wired.com/story/ai-is-heating-the-olympic-pool/</a>. Accessed 6 Sept. 2024. <a href="#fnref1" class="footnote-backref">↩︎</a></p></li><li id="fn2" class="footnote-item"><p>“DOJ subpoenas NVIDIA as part of antitrust probe regarding AI processors.” <em>Consent.Yahoo.com</em>, <a href="https://consent.yahoo.com/v2/collectConsent?sessionId=1_cc-session_55e49573-6895-4a02-8e41-45554122f5eb" target="_blank">https://consent.yahoo.com/v2/collectConsent?sessionId=1_cc-session_55e49573-6895-4a02-8e41-45554122f5eb</a>. Accessed 6 Sept. 2024. <a href="#fnref2" class="footnote-backref">↩︎</a></p></li></ol></section>

<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 9</strong>: Summary with citations</figcaption>

</v-clicks>

<!--
After the citation-generator adds the citations, we can click through and verify the claims.
-->

---

# And redactions?

<v-clicks>

> Furthermore, the environmental impact of AI is being questioned, with critics
> arguing that initiatives like using data center heat to warm the Olympic
> swimming pool are merely distractions from the larger environmental costs
> associated with AI development and deployment.¹ The Department of Justice is
> also investigating NVIDIA, a leading AI processor manufacturer, for potential
> antitrust violations, suggesting growing regulatory scrutiny over the
> industry's competitive landscape.²

<section class="footnotes"><ol class="footnotes-list"><li id="fn1" class="footnote-item"><p>“AI Is Heating the Olympic Pool.” <em>Wired</em>, <a href="https://www.wired.com/story/ai-is-heating-the-olympic-pool/" target="_blank">https://www.wired.com/story/ai-is-heating-the-olympic-pool/</a>. Accessed 6 Sept. 2024. <a href="#fnref1" class="footnote-backref">↩︎</a></p></li><li id="fn2" class="footnote-item"><p>“DOJ subpoenas NVIDIA as part of antitrust probe regarding AI processors.” <em>Consent.Yahoo.com</em>, <a href="https://consent.yahoo.com/v2/collectConsent?sessionId=1_cc-session_55e49573-6895-4a02-8e41-45554122f5eb" target="_blank">https://consent.yahoo.com/v2/collectConsent?sessionId=1_cc-session_55e49573-6895-4a02-8e41-45554122f5eb</a>. Accessed 6 Sept. 2024. <a href="#fnref2" class="footnote-backref">↩︎</a></p></li></ol></section>

<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 10</strong>: Redacted summary</figcaption>

</v-clicks>

<!--
Lastly, the redactor gets rid of the stuff which has no citations.
-->

---
layout: two-cols-header
---

# Check out the code!

::left::

<div class="relative h-full w-full" v-click=1>
  <div class="absolute inset-0 overflow-hidden">
    <img src="/github.png" class="h-full w-full object-cover rounded shadow-lg" style="object-position: top;" />
  </div>
</div>

::right::

<figure class="p-5">
  <img src="/github-qr.png" class="w-4/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 11</strong>: <a href="https://github.com/google-gemini/workshops/tree/main/factuality">github.com/google-gemini/workshops</a></figcaption>
</figure>

---
layout: two-cols-header
---

# Join our Gemini meetup!

::left::

<div class="relative h-full w-full" v-click=1>
  <div class="">
    <img src="/meetup.png" class="h-full w-full object-cover rounded shadow-lg" style="object-position: top;" />
  </div>
</div>

::right::

<figure class="p-5">
  <img src="/meetup-qr.png" class="w-4/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 12</strong>: <a href="https://lu.ma/geminimeetup">lu.ma/geminimeetup</a></figcaption>
</figure>
