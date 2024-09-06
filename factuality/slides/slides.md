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
The last comment block of each slide will be treated as slide notes. It will be visible and editable in Presenter Mode along with the slide. [Read more in the docs](https://sli.dev/guide/syntax.html#notes)
-->

---

# What is factual AI?

<v-clicks>

<img src="/gemini.png" class="w-full max-w-2xl mx-auto max-h-96" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 1</strong>: <a href="https://g.co/gemini/share/05b57cf46591">Gemini</a>, retrieved on August 9, 2024</figcaption>

</v-clicks>

---

# What is factual AI (con't)?

<v-clicks>

<img src="/chatgpt.png" class="w-full max-w-2xl mx-auto max-h-96" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 2</strong>: <a href="https://chatgpt.com/share/56509f4c-d8e8-4298-ada3-b64d4a79e177">ChatGPT</a>, retrieved on August 9, 2024</figcaption>

</v-clicks>

---

# What is factual AI (con't)?

<v-clicks>

<img src="/perplexity.png" class="w-full max-w-2xl mx-auto max-h-96" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 3</strong>: <a href="https://www.perplexity.ai/search/who-shot-trump-6Sv32S9TTwu3FrtfVsG_EQ">Perplexity</a>, retrieved on August 9, 2024</figcaption>

</v-clicks>

---

# How would you build a factual AI?

<v-clicks>

<img src="/factuality.svg" class="w-full max-w-2xl mx-auto max-h-96" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 4</strong>: How to build a factuality stack</figcaption>

</v-clicks>

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

</v-clicks>

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

</v-clicks>

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

</v-clicks>

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

</v-clicks>

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

</v-clicks>

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

</v-clicks>
