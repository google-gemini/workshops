---
# try also 'default' to start simple
theme: seriph
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
background: https://cover.sli.dev
# some information about your slides, markdown enabled
title: Gemini plays games
info: |
  Rock-paper-scissors with the gods
# apply any unocss classes to the current slide
class: text-center
# https://sli.dev/custom/highlighters.html
highlighter: shiki
# https://sli.dev/guide/drawing
drawings:
  persist: false
# slide transition: https://sli.dev/guide/animations#slide-transitions
transition: slide-left
# enable MDC Syntax: https://sli.dev/guide/syntax#mdc-syntax
mdc: true
---

<v-clicks>

# Gemini plays games

## Rock-paper-scissors with the gods

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
layout: two-cols-header
---

# Why rock-paper-scissors?

::left::

<ul>
<v-click at="4"><li>Mechanically <span v-mark.circle.red="{at: 5}">simple</span></li></v-click>
<v-click at="6"><li>Requires a <span v-mark.underline.red="{at: 7}">theory of mind</span></li></v-click>
</ul>

::right::

<figure class="p-5">
<v-clicks at="1">

<img src="/ares-vs-athena.webp" class="rounded shadow-lg" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 1</strong>: Ares and Athena play the <span v-mark.highlight.cyan="{at: 3}">“I love you”</span> move.</figcaption>

</v-clicks>
</figure>

<!--
For the life of me, couldn't get an image of Ares and Athena playing rock-paper-scissors: wanted Ares with rock; Athena with paper. Even said, "ok, Ares makes a fist; Athena spreads her fingers flat like a piece of paper."
No matter what, this strange move came up; thought, "what, is this some new permutation on rock-paper-scissors; the one with Spock and lizard?"
No! Turns out what Gemini really wanted was fraternal harmony: Ares and Athena are playing "I love you."
This is funny because nowhere in Homer, Hesiod or Pindar do Ares and Athena express anything remotely like love.
Maybe they had to wait for the advent of LLMs to have their day.
-->

---

# How do people actually play?

<ul>
<v-click><li><span v-mark.crossed-off.black="{ at: 2  }">Mixed strategy Nash Equilibrium</span></li></v-click>
<v-click at="3"><li><span v-mark.box.red="{ at: 4 }">Ares heuristic</span><sup id="a1"><a href="#f1">1</a></sup> <v-click at="5">(a.k.a. <span v-mark.highlight.yellow="{ at: 6 }">“losers lead with rock”</span>)</v-click></li></v-click>
</ul>

<div class="footnotes">
  <ol>
    <v-click at="3"><li id="f1">Wang, Zhijian, Bin Xu, and Hai-Jun Zhou. “Social Cycling and Conditional Responses in the Rock-Paper-Scissors Game.” <em>Scientific Reports</em> 4, no. 1 (July 2014). https://doi.org/10.1038/srep05830. <a href="#a1">↩</a></li></v-click>
  </ol>
</div>

<style>
  .footnotes {
    position: absolute;
    bottom: 0;
    width: calc(100% - 8rem); /* Adjust width to prevent overflow */
    font-size: 0.8em;
    color: gray;
    padding: 1rem;
    box-sizing: border-box;
    white-space: normal; /* Ensure text wraps */
  }
</style>

<v-click at="7"></v-click>

<!--
Out of curiosty, anyone feel like playing a game?
Why did you start with rock? Why did you switch? Why did you stay?

I'd like to do a little social experiment; would someone mind coming up to play?

Something called the mixed-strategy Nash Equilibrium; theoretically optimal strategy; but no one uses it.
And it turns out we have something better: the Ares heuristic or "losers lead with rock."
Play rugby, rock-paper-scissors for who gets to kick off; can't tell you the number of times I won by starting with paper.

The Ares heuristic, it turns out, beats the random method in social settings.

Most people play with what I like to call the Ares heuristic (based on the work of Zhijian, et al.); colloquially known as "losers lead with rock."
-->

---
layout: two-cols-header
---

# Can you deduce the Ares heuristic?

::left::

<div v-click="3">

<v-clicks at="3">
<caption class="text-center text-gray-500 text-sm mt-2 w-full whitespace-normal"><strong>Table 1</strong>: Ares heuristic vs. Athena</caption>

<table>
  <thead>
    <tr>
      <th>Step</th>
      <th>Ares</th>
      <th>Athena</th>
      <th>Outcome</th>
    </tr>
  </thead>
  <tbody>
    <tr v-click=5>
      <td>1</td>
      <td><span v-mark.circle.cyan="{ at: 23 }"><span v-mark.highlight.yellow="{ at: 13 }">Rock</span></span></td>
      <td>Scissors</td>
      <td><span v-mark.highlight.yellow="{ at: 13 }">Win</span></td>
    </tr>
    <tr v-click=6>
      <td>2</td>
      <td><span v-mark.highlight.yellow="{ at: 14 }">Rock</span></td>
      <td>Scissors</td>
      <td><span v-mark.highlight.yellow="{ at: 14 }">Win</span></td>
    </tr>
    <tr v-click=7>
      <td>3</td>
      <td><span v-mark.box.red="{ at: 18 }"><span v-mark.highlight.yellow="{ at: 15 }">Rock</span></span></td>
      <td>Paper</td>
      <td><span v-mark.box.red="{ at: 18 }">Lose</span></td>
    </tr>
    <tr v-click=8>
      <td>4</td>
      <td><span v-mark.box.red="{ at: 19 }">Paper</span></td>
      <td>Scissors</td>
      <td><span v-mark.box.red="{ at: 19 }">Lose</span></td>
    </tr>
    <tr v-click=9>
      <td>5</td>
      <td><span v-mark.box.red="{ at: 20 }">Scissors</span></td>
      <td>Scissors</td>
      <td><span v-mark.box.red="{ at: 20 }">Draw</span></td>
    </tr>
    <tr v-click=10>
      <td>6</td>
      <td><span v-mark.box.red="{ at: 21 }">Rock</span></td>
      <td>Rock</td>
      <td><span v-mark.box.red="{ at: 21 }">Draw</span></td>
    </tr>
    <tr v-click=11>
      <td>7</td>
      <td><span v-mark.box.red="{ at: 22 }"><span v-mark.highlight.yellow="{ at: 16 }">Paper</span></span></td>
      <td>Rock</td>
      <td><span v-mark.highlight.yellow="{ at: 16 }">Win</span></td>
    </tr>
    <tr v-click=12>
      <td>8</td>
      <td><span v-mark.highlight.yellow="{ at: 17 }">Paper</span></td>
      <td>Scissors</td>
      <td>Lose</td>
    </tr>
  </tbody>
</table>

</v-clicks>

</div>

::right::

<figure class="p-5">
<v-clicks at="1">

<img src="/ares.webp" class="rounded shadow-lg" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 2</strong>: Ares finally got his <span v-mark.circle.cyan="{ at: 23 }">rock</span> on!</figcaption>

</v-clicks>
</figure>

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
    /* border-bottom: 2px solid black; */
  }
  caption {
    display: block; /* Ensure caption spans the whole width */
    white-space: normal; /* Ensure text wraps correctly */
  }
</style>

---

# Let's write some agents!

````md magic-move {lines: true}
```python {*|2|3|4-12|13|14|*}
ares = Agent(
    role="Ares the rock-paper-scissors player",
    goal="Play rock-paper-scissors with a brute-force heuristic",
    backstory=textwrap.dedent(
        """\
        You are a Ares the god of war. You are an hilariously
        aggressive rock-paper-scissors player. You start
        with rock. When you win, you stick with your winning
        move. When you lose or tie, cycle clockwise to the next move
        (rock to paper to scissors to rock, etc.).
        """
    ),
    llm=gemini,
    tools=[play],
)
```

```python {*|2|3|4-11|12|13|*}
athena = Agent(
    role="Athena the rock-paper-scissors player",
    goal="Play rock-paper-scissors with a strategic heuristic",
    backstory=textwrap.dedent(
        """\
        You are a Athena the goddess of wisdom. You are a flawlessly
        strategic rock-paper-scissors player. Attempt to observe
        patterns in your opponent's moves and counter accordingly: use
        paper against rock; scissors against paper; and rock against
        scissors. Be volatile to avoid becoming predictable.
        """,
    llm=gemini,
    tools=[play],
)
```
````

<!--
Flawlessly strategic, like Mary Poppins.
-->

---

# How do they perform?

<style>
  @import url('/wins.css');

  #wins-svg {
      opacity: 0; /* Make the entire SVG invisible initially */
  }

  #wins-svg.active {
      opacity: 1; /* Make the entire SVG fully visible when active */
  }
</style>

<figure class="p-5" v-click=1 ref="winsFigure">

<div class="wrapper w-full max-w-xl mx-auto p-5 overflow-hidden">
<svg id="wins-svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="100%" height="100%" viewBox="0 0 1382.4 830.88" xmlns="http://www.w3.org/2000/svg" version="1.1">
 <metadata>
  <rdf:rdf xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
   <cc:work>
    <dc:type rdf:resource="http://purl.org/dc/dcmitype/StillImage"></dc:type>
    <dc:date>2024-06-02T22:57:37.411763</dc:date>
    <dc:format>image/svg+xml</dc:format>
    <dc:creator>
     <cc:agent>
      <dc:title>Matplotlib v3.9.0, https://matplotlib.org/</dc:title>
     </cc:agent>
    </dc:creator>
   </cc:work>
  </rdf:rdf>
 </metadata>
 <defs>
  <style type="text/css">*{stroke-linejoin: round; stroke-linecap: butt}</style>
 </defs>
 <g id="figure_1">
  <g id="patch_1">
   <path d="M 0 830.88 
L 1382.4 830.88 
L 1382.4 0 
L 0 0 
z
" style="fill: rgb(255, 255, 255);" class="svg-elem-1"></path>
  </g>
  <g id="axes_1">
   <g id="patch_2">
    <path d="M 92.832 718.326533 
L 1365.892364 718.326533 
L 1365.892364 51.6992 
L 92.832 51.6992 
z
" style="fill: rgb(255, 255, 255);" class="svg-elem-2"></path>
   </g>
   <g id="matplotlib.axis_1">
    <g id="xtick_1">
     <g id="line2d_1">
      <path d="M 150.69838 718.326533 
L 150.69838 51.6992 
" clip-path="url(#pf8abf2f79a)" style="fill: none; stroke: rgb(176, 176, 176); stroke-width: 1.2; stroke-linecap: square;" class="svg-elem-3"></path>
     </g>
     <g id="line2d_2">
      <defs>
       <path id="m456b82e2f8" d="M 0 0 
L 0 3.5 
" style="stroke: rgb(0, 0, 0); stroke-width: 0.8;" class="svg-elem-4"></path>
      </defs>
      <g>
       <use xlink:href="#m456b82e2f8" x="150.69838" y="718.326533" style="stroke: #000000; stroke-width: 0.8"></use>
      </g>
     </g>
     <g id="text_1">
      <!-- 0 -->
      <g transform="translate(144.302755 743.375283) scale(0.24 -0.24)">
       <defs>
        <path id="PTSerif-Regular-30" d="M 224 2240 
Q 224 3392 608 3974 
Q 992 4557 1709 4557 
Q 2483 4557 2841 3984 
Q 3200 3411 3200 2240 
Q 3200 1088 2813 505 
Q 2426 -77 1670 -77 
Q 1280 -77 1005 80 
Q 730 237 557 534 
Q 384 832 304 1261 
Q 224 1690 224 2240 
z
M 838 2240 
Q 838 1779 883 1401 
Q 928 1024 1027 752 
Q 1126 480 1283 333 
Q 1440 186 1664 186 
Q 2170 186 2378 685 
Q 2586 1184 2586 2240 
Q 2586 2701 2547 3078 
Q 2509 3456 2406 3725 
Q 2304 3994 2134 4141 
Q 1965 4288 1709 4288 
Q 1229 4288 1033 3792 
Q 838 3296 838 2240 
z
" transform="scale(0.015625)" class="svg-elem-5"></path>
       </defs>
       <use xlink:href="#PTSerif-Regular-30"></use>
      </g>
     </g>
    </g>
    <g id="xtick_2">
     <g id="line2d_3">
      <path d="M 391.808298 718.326533 
L 391.808298 51.6992 
" clip-path="url(#pf8abf2f79a)" style="fill: none; stroke: rgb(176, 176, 176); stroke-width: 1.2; stroke-linecap: square;" class="svg-elem-6"></path>
     </g>
     <g id="line2d_4">
      <g>
       <use xlink:href="#m456b82e2f8" x="391.808298" y="718.326533" style="stroke: #000000; stroke-width: 0.8"></use>
      </g>
     </g>
     <g id="text_2">
      <!-- 5 -->
      <g transform="translate(385.412673 743.375283) scale(0.24 -0.24)">
       <defs>
        <path id="PTSerif-Regular-35" d="M 2758 4832 
L 2918 4832 
Q 2912 4736 2902 4617 
Q 2893 4499 2873 4380 
Q 2854 4262 2835 4153 
Q 2816 4045 2790 3974 
L 1216 3974 
L 1062 2739 
L 1478 2739 
Q 1798 2739 2064 2652 
Q 2330 2566 2518 2396 
Q 2707 2227 2812 1984 
Q 2918 1741 2918 1427 
Q 2918 1056 2790 774 
Q 2662 493 2451 304 
Q 2240 115 1971 19 
Q 1702 -77 1414 -77 
Q 1286 -77 1139 -54 
Q 992 -32 848 13 
Q 704 58 576 118 
Q 448 179 358 250 
L 544 826 
L 672 826 
Q 710 781 768 710 
Q 826 640 886 563 
Q 947 486 1008 409 
Q 1069 333 1120 275 
Q 1184 262 1238 243 
Q 1293 224 1408 224 
Q 1619 224 1795 307 
Q 1971 390 2099 534 
Q 2227 678 2297 870 
Q 2368 1062 2368 1286 
Q 2368 1542 2272 1731 
Q 2176 1920 2009 2038 
Q 1843 2157 1622 2214 
Q 1402 2272 1158 2266 
L 704 2259 
L 960 4480 
L 2483 4480 
L 2758 4832 
z
" transform="scale(0.015625)" class="svg-elem-7"></path>
       </defs>
       <use xlink:href="#PTSerif-Regular-35"></use>
      </g>
     </g>
    </g>
    <g id="xtick_3">
     <g id="line2d_5">
      <path d="M 632.918215 718.326533 
L 632.918215 51.6992 
" clip-path="url(#pf8abf2f79a)" style="fill: none; stroke: rgb(176, 176, 176); stroke-width: 1.2; stroke-linecap: square;" class="svg-elem-8"></path>
     </g>
     <g id="line2d_6">
      <g>
       <use xlink:href="#m456b82e2f8" x="632.918215" y="718.326533" style="stroke: #000000; stroke-width: 0.8"></use>
      </g>
     </g>
     <g id="text_3">
      <!-- 10 -->
      <g transform="translate(620.126965 743.375283) scale(0.24 -0.24)">
       <defs>
        <path id="PTSerif-Regular-31" d="M 2720 0 
L 851 0 
L 851 186 
Q 1011 256 1174 310 
Q 1338 365 1504 403 
L 1504 3546 
L 1530 3923 
Q 1350 3853 1158 3824 
Q 966 3795 762 3802 
L 730 3955 
Q 1024 4051 1337 4195 
Q 1651 4339 1920 4557 
L 2080 4557 
L 2080 403 
Q 2240 365 2400 310 
Q 2560 256 2720 186 
L 2720 0 
z
" transform="scale(0.015625)" class="svg-elem-9"></path>
       </defs>
       <use xlink:href="#PTSerif-Regular-31"></use>
       <use xlink:href="#PTSerif-Regular-30" x="53.299988"></use>
      </g>
     </g>
    </g>
    <g id="xtick_4">
     <g id="line2d_7">
      <path d="M 874.028132 718.326533 
L 874.028132 51.6992 
" clip-path="url(#pf8abf2f79a)" style="fill: none; stroke: rgb(176, 176, 176); stroke-width: 1.2; stroke-linecap: square;" class="svg-elem-10"></path>
     </g>
     <g id="line2d_8">
      <g>
       <use xlink:href="#m456b82e2f8" x="874.028132" y="718.326533" style="stroke: #000000; stroke-width: 0.8"></use>
      </g>
     </g>
     <g id="text_4">
      <!-- 15 -->
      <g transform="translate(861.236882 743.375283) scale(0.24 -0.24)">
       <use xlink:href="#PTSerif-Regular-31"></use>
       <use xlink:href="#PTSerif-Regular-35" x="53.299988"></use>
      </g>
     </g>
    </g>
    <g id="xtick_5">
     <g id="line2d_9">
      <path d="M 1115.13805 718.326533 
L 1115.13805 51.6992 
" clip-path="url(#pf8abf2f79a)" style="fill: none; stroke: rgb(176, 176, 176); stroke-width: 1.2; stroke-linecap: square;" class="svg-elem-11"></path>
     </g>
     <g id="line2d_10">
      <g>
       <use xlink:href="#m456b82e2f8" x="1115.13805" y="718.326533" style="stroke: #000000; stroke-width: 0.8"></use>
      </g>
     </g>
     <g id="text_5">
      <!-- 20 -->
      <g transform="translate(1102.3468 743.375283) scale(0.24 -0.24)">
       <defs>
        <path id="PTSerif-Regular-32" d="M 851 3232 
L 691 3232 
Q 621 3418 547 3667 
Q 474 3917 422 4141 
Q 646 4333 960 4445 
Q 1274 4557 1638 4557 
Q 1958 4557 2188 4467 
Q 2419 4378 2569 4224 
Q 2720 4070 2790 3868 
Q 2861 3667 2861 3450 
Q 2861 3091 2694 2713 
Q 2528 2336 2281 1981 
Q 2035 1626 1747 1312 
Q 1459 998 1216 762 
L 947 512 
L 947 486 
L 1306 525 
L 2406 525 
L 2720 1242 
L 2880 1242 
Q 2893 1101 2905 934 
Q 2918 768 2928 598 
Q 2938 429 2944 272 
Q 2950 115 2950 0 
L 307 0 
L 307 205 
Q 448 352 649 563 
Q 851 774 1068 1030 
Q 1286 1286 1500 1574 
Q 1715 1862 1881 2160 
Q 2048 2458 2153 2752 
Q 2259 3046 2259 3315 
Q 2259 3501 2211 3667 
Q 2163 3834 2067 3958 
Q 1971 4083 1833 4153 
Q 1696 4224 1517 4224 
Q 1382 4224 1280 4205 
Q 1178 4186 1056 4147 
L 851 3232 
z
" transform="scale(0.015625)" class="svg-elem-12"></path>
       </defs>
       <use xlink:href="#PTSerif-Regular-32"></use>
       <use xlink:href="#PTSerif-Regular-30" x="53.299988"></use>
      </g>
     </g>
    </g>
    <g id="xtick_6">
     <g id="line2d_11">
      <path d="M 1356.247967 718.326533 
L 1356.247967 51.6992 
" clip-path="url(#pf8abf2f79a)" style="fill: none; stroke: rgb(176, 176, 176); stroke-width: 1.2; stroke-linecap: square;" class="svg-elem-13"></path>
     </g>
     <g id="line2d_12">
      <g>
       <use xlink:href="#m456b82e2f8" x="1356.247967" y="718.326533" style="stroke: #000000; stroke-width: 0.8"></use>
      </g>
     </g>
     <g id="text_6">
      <!-- 25 -->
      <g transform="translate(1343.456717 743.375283) scale(0.24 -0.24)">
       <use xlink:href="#PTSerif-Regular-32"></use>
       <use xlink:href="#PTSerif-Regular-35" x="53.299988"></use>
      </g>
     </g>
    </g>
    <g id="text_7">
     <!-- Number of Turns -->
     <g transform="translate(631.130932 771.728096) scale(0.26 -0.26)">
      <defs>
       <path id="PTSerif-Regular-4e" d="M 3117 4480 
L 4499 4480 
L 4499 4294 
Q 4230 4115 3974 4038 
L 3974 -77 
L 3610 -77 
L 1286 3450 
L 1037 3949 
L 1018 3949 
L 1075 3450 
L 1075 410 
Q 1338 339 1568 186 
L 1568 0 
L 186 0 
L 186 186 
Q 301 256 432 310 
Q 563 365 710 410 
L 710 4077 
Q 582 4128 457 4185 
Q 333 4243 224 4301 
L 224 4480 
L 1306 4480 
L 3322 1440 
L 3616 890 
L 3642 890 
L 3610 1440 
L 3610 4038 
Q 3475 4096 3350 4160 
Q 3226 4224 3117 4294 
L 3117 4480 
z
" transform="scale(0.015625)" class="svg-elem-14"></path>
       <path id="PTSerif-Regular-75" d="M 493 1267 
Q 493 1670 512 2057 
Q 531 2445 531 2829 
L 109 2880 
L 109 3046 
Q 314 3123 528 3180 
Q 742 3238 947 3277 
L 1107 3277 
Q 1107 2797 1088 2323 
Q 1069 1850 1069 1382 
Q 1069 1133 1097 934 
Q 1126 736 1200 601 
Q 1274 467 1402 393 
Q 1530 320 1728 320 
Q 2016 320 2211 528 
Q 2406 736 2515 1069 
L 2515 2829 
L 2099 2880 
L 2099 3046 
Q 2298 3123 2512 3180 
Q 2726 3238 2931 3277 
L 3091 3277 
L 3091 365 
L 3514 314 
L 3514 179 
Q 3328 96 3139 32 
Q 2950 -32 2746 -64 
L 2586 -64 
L 2541 698 
L 2515 698 
Q 2483 563 2403 425 
Q 2323 288 2195 176 
Q 2067 64 1904 -6 
Q 1741 -77 1549 -77 
Q 1293 -77 1097 -16 
Q 902 45 768 198 
Q 634 352 563 611 
Q 493 870 493 1267 
z
" transform="scale(0.015625)" class="svg-elem-15"></path>
       <path id="PTSerif-Regular-6d" d="M 3507 0 
L 2138 0 
L 2138 160 
Q 2202 198 2294 240 
Q 2387 282 2515 314 
L 2515 1792 
Q 2515 2048 2492 2253 
Q 2470 2458 2409 2595 
Q 2349 2733 2233 2806 
Q 2118 2880 1933 2880 
Q 1792 2880 1673 2822 
Q 1555 2765 1462 2669 
Q 1370 2573 1302 2451 
Q 1235 2330 1197 2195 
L 1197 314 
Q 1299 282 1392 246 
Q 1485 211 1574 160 
L 1574 0 
L 198 0 
L 198 160 
Q 288 205 397 243 
Q 506 282 621 314 
L 621 2829 
L 198 2880 
L 198 3046 
Q 403 3136 617 3190 
Q 832 3245 1037 3277 
L 1197 3277 
L 1197 2554 
L 1203 2554 
Q 1306 2854 1552 3065 
Q 1798 3277 2163 3277 
Q 2317 3277 2457 3245 
Q 2598 3213 2720 3126 
Q 2842 3040 2925 2886 
Q 3008 2733 3046 2490 
Q 3162 2842 3418 3059 
Q 3674 3277 4058 3277 
Q 4294 3277 4470 3216 
Q 4646 3155 4761 3001 
Q 4877 2848 4931 2585 
Q 4986 2323 4986 1920 
L 4986 314 
Q 5203 275 5408 160 
L 5408 0 
L 4032 0 
L 4032 160 
Q 4224 262 4410 314 
L 4410 1907 
Q 4410 2138 4387 2317 
Q 4365 2496 4301 2621 
Q 4237 2746 4121 2813 
Q 4006 2880 3814 2880 
Q 3507 2880 3337 2669 
Q 3168 2458 3091 2131 
L 3091 314 
Q 3315 250 3507 160 
L 3507 0 
z
" transform="scale(0.015625)" class="svg-elem-16"></path>
       <path id="PTSerif-Regular-62" d="M 493 4365 
L 6 4416 
L 6 4582 
Q 205 4666 451 4717 
Q 698 4768 909 4813 
L 1069 4813 
L 1069 2566 
L 1082 2566 
Q 1190 2893 1449 3085 
Q 1709 3277 2022 3277 
Q 2605 3277 2915 2880 
Q 3226 2483 3226 1658 
Q 3226 813 2800 377 
Q 2374 -58 1574 -58 
Q 1414 -58 1254 -35 
Q 1094 -13 947 19 
Q 800 51 681 96 
Q 563 141 493 186 
L 493 4365 
z
M 1850 2880 
Q 1542 2880 1350 2672 
Q 1158 2464 1069 2144 
L 1069 358 
Q 1184 294 1350 259 
Q 1517 224 1702 224 
Q 2125 224 2368 592 
Q 2611 960 2611 1658 
Q 2611 1907 2569 2131 
Q 2528 2355 2435 2521 
Q 2342 2688 2198 2784 
Q 2054 2880 1850 2880 
z
" transform="scale(0.015625)" class="svg-elem-17"></path>
       <path id="PTSerif-Regular-65" d="M 2854 448 
Q 2803 339 2694 243 
Q 2586 147 2445 76 
Q 2304 6 2137 -35 
Q 1971 -77 1798 -77 
Q 1421 -77 1133 41 
Q 845 160 653 381 
Q 461 602 361 909 
Q 262 1216 262 1600 
Q 262 2419 640 2848 
Q 1018 3277 1709 3277 
Q 1933 3277 2150 3216 
Q 2368 3155 2537 3014 
Q 2707 2874 2812 2640 
Q 2918 2406 2918 2061 
Q 2918 1952 2908 1840 
Q 2899 1728 2874 1600 
L 877 1600 
Q 877 1331 944 1097 
Q 1011 864 1145 691 
Q 1280 518 1485 419 
Q 1690 320 1965 320 
Q 2189 320 2419 384 
Q 2650 448 2765 550 
L 2854 448 
z
M 1683 2995 
Q 1318 2995 1126 2748 
Q 934 2502 896 1882 
L 2304 1882 
Q 2310 1939 2313 1993 
Q 2317 2048 2317 2099 
Q 2317 2509 2163 2752 
Q 2010 2995 1683 2995 
z
" transform="scale(0.015625)" class="svg-elem-18"></path>
       <path id="PTSerif-Regular-72" d="M 1562 2720 
Q 1491 2682 1385 2563 
Q 1280 2445 1197 2214 
L 1197 314 
Q 1325 301 1453 265 
Q 1581 230 1709 160 
L 1709 0 
L 198 0 
L 198 160 
Q 314 224 416 256 
Q 518 288 621 314 
L 621 2829 
L 198 2880 
L 198 3046 
Q 403 3136 620 3190 
Q 838 3245 1037 3277 
L 1197 3277 
L 1197 2598 
L 1222 2598 
Q 1280 2726 1385 2854 
Q 1491 2982 1628 3084 
Q 1766 3187 1929 3241 
Q 2093 3296 2266 3277 
Q 2310 3194 2345 3094 
Q 2381 2995 2413 2886 
L 2413 2720 
L 1562 2720 
z
" transform="scale(0.015625)" class="svg-elem-19"></path>
       <path id="PTSerif-Regular-20" transform="scale(0.015625)" class="svg-elem-20"></path>
       <path id="PTSerif-Regular-6f" d="M 262 1600 
Q 262 2003 368 2313 
Q 474 2624 672 2838 
Q 870 3053 1148 3165 
Q 1427 3277 1766 3277 
Q 2163 3277 2451 3155 
Q 2739 3034 2921 2813 
Q 3104 2592 3190 2285 
Q 3277 1978 3277 1600 
Q 3277 794 2867 358 
Q 2458 -77 1766 -77 
Q 1382 -77 1100 41 
Q 819 160 633 381 
Q 448 602 355 912 
Q 262 1222 262 1600 
z
M 877 1600 
Q 877 1312 931 1056 
Q 986 800 1104 611 
Q 1222 422 1414 313 
Q 1606 205 1875 205 
Q 2221 205 2441 544 
Q 2662 883 2662 1600 
Q 2662 1894 2608 2147 
Q 2554 2400 2438 2589 
Q 2323 2778 2144 2886 
Q 1965 2995 1715 2995 
Q 1338 2995 1107 2656 
Q 877 2317 877 1600 
z
" transform="scale(0.015625)" class="svg-elem-21"></path>
       <path id="PTSerif-Regular-66" d="M 1958 4813 
Q 2016 4813 2093 4806 
Q 2170 4800 2253 4790 
Q 2336 4781 2413 4765 
Q 2490 4749 2547 4730 
Q 2528 4518 2493 4336 
Q 2458 4154 2406 4006 
L 2246 4006 
L 1965 4557 
Q 1779 4557 1648 4518 
Q 1517 4480 1430 4371 
Q 1344 4262 1302 4057 
Q 1261 3853 1261 3520 
L 1261 3200 
L 1997 3200 
L 1997 2880 
L 1261 2880 
L 1261 314 
Q 1594 275 1875 160 
L 1875 0 
L 262 0 
L 262 160 
Q 461 275 685 314 
L 685 2880 
L 198 2880 
L 198 3046 
Q 422 3187 685 3258 
L 685 3482 
Q 685 3878 781 4137 
Q 877 4397 1049 4547 
Q 1222 4698 1456 4755 
Q 1690 4813 1958 4813 
z
" transform="scale(0.015625)" class="svg-elem-22"></path>
       <path id="PTSerif-Regular-54" d="M 2880 0 
L 1082 0 
L 1082 186 
Q 1222 237 1366 275 
Q 1510 314 1677 339 
L 1677 4147 
L 698 4147 
L 358 3232 
L 198 3232 
Q 179 3360 166 3523 
Q 154 3686 144 3856 
Q 134 4026 128 4189 
Q 122 4352 122 4480 
L 3840 4480 
Q 3840 4352 3833 4192 
Q 3827 4032 3817 3862 
Q 3808 3693 3798 3529 
Q 3789 3366 3770 3232 
L 3603 3232 
L 3270 4147 
L 2291 4147 
L 2291 339 
Q 2458 307 2602 275 
Q 2746 243 2880 186 
L 2880 0 
z
" transform="scale(0.015625)" class="svg-elem-23"></path>
       <path id="PTSerif-Regular-6e" d="M 3693 0 
L 2317 0 
L 2317 160 
Q 2490 250 2694 314 
L 2694 1830 
Q 2694 2317 2553 2598 
Q 2413 2880 2042 2880 
Q 1882 2880 1744 2822 
Q 1606 2765 1500 2665 
Q 1395 2566 1318 2441 
Q 1242 2317 1197 2182 
L 1197 314 
Q 1395 275 1581 160 
L 1581 0 
L 198 0 
L 198 160 
Q 358 243 621 314 
L 621 2829 
L 198 2880 
L 198 3046 
Q 365 3117 582 3174 
Q 800 3232 1037 3277 
L 1197 3277 
L 1197 2560 
L 1203 2560 
Q 1338 2854 1590 3065 
Q 1843 3277 2202 3277 
Q 2458 3277 2659 3216 
Q 2861 3155 2995 3001 
Q 3130 2848 3200 2589 
Q 3270 2330 3270 1933 
L 3270 314 
Q 3526 269 3693 160 
L 3693 0 
z
" transform="scale(0.015625)" class="svg-elem-24"></path>
       <path id="PTSerif-Regular-73" d="M 1888 730 
Q 1888 909 1776 1033 
Q 1664 1158 1491 1267 
Q 1318 1376 1123 1478 
Q 928 1581 755 1718 
Q 582 1856 470 2035 
Q 358 2214 358 2477 
Q 358 2650 438 2797 
Q 518 2944 652 3049 
Q 787 3155 966 3216 
Q 1146 3277 1350 3277 
Q 1696 3277 1917 3238 
Q 2138 3200 2342 3130 
Q 2317 2925 2281 2717 
Q 2246 2509 2182 2291 
L 2022 2291 
L 1779 2944 
Q 1702 2976 1606 2985 
Q 1510 2995 1408 2995 
Q 1293 2995 1206 2953 
Q 1120 2912 1059 2848 
Q 998 2784 966 2701 
Q 934 2618 934 2534 
Q 934 2362 1046 2237 
Q 1158 2112 1331 2006 
Q 1504 1901 1699 1798 
Q 1894 1696 2067 1568 
Q 2240 1440 2352 1270 
Q 2464 1101 2464 864 
Q 2464 646 2371 473 
Q 2278 301 2115 179 
Q 1952 58 1737 -9 
Q 1523 -77 1280 -77 
Q 1005 -77 774 -29 
Q 544 19 294 109 
Q 307 339 352 553 
Q 397 768 467 966 
L 627 966 
L 909 269 
Q 979 218 1078 211 
Q 1178 205 1261 205 
Q 1542 205 1715 358 
Q 1888 512 1888 730 
z
" transform="scale(0.015625)" class="svg-elem-25"></path>
      </defs>
      <use xlink:href="#PTSerif-Regular-4e"></use>
      <use xlink:href="#PTSerif-Regular-75" x="73.199982"></use>
      <use xlink:href="#PTSerif-Regular-6d" x="130.599976"></use>
      <use xlink:href="#PTSerif-Regular-62" x="216.899963"></use>
      <use xlink:href="#PTSerif-Regular-65" x="271.399948"></use>
      <use xlink:href="#PTSerif-Regular-72" x="321.699936"></use>
      <use xlink:href="#PTSerif-Regular-20" x="360.09993"></use>
      <use xlink:href="#PTSerif-Regular-6f" x="384.399918"></use>
      <use xlink:href="#PTSerif-Regular-66" x="439.699905"></use>
      <use xlink:href="#PTSerif-Regular-20" x="473.899902"></use>
      <use xlink:href="#PTSerif-Regular-54" x="498.19989"></use>
      <use xlink:href="#PTSerif-Regular-75" x="557.099884"></use>
      <use xlink:href="#PTSerif-Regular-72" x="614.499878"></use>
      <use xlink:href="#PTSerif-Regular-6e" x="652.899872"></use>
      <use xlink:href="#PTSerif-Regular-73" x="712.299866"></use>
     </g>
    </g>
   </g>
   <g id="matplotlib.axis_2">
    <g id="ytick_1">
     <g id="line2d_13">
      <path d="M 92.832 688.025291 
L 1365.892364 688.025291 
" clip-path="url(#pf8abf2f79a)" style="fill: none; stroke: rgb(176, 176, 176); stroke-width: 1.2; stroke-linecap: square;" class="svg-elem-26"></path>
     </g>
     <g id="line2d_14">
      <defs>
       <path id="mfa10eabba2" d="M 0 0 
L -3.5 0 
" style="stroke: rgb(0, 0, 0); stroke-width: 0.8;" class="svg-elem-27"></path>
      </defs>
      <g>
       <use xlink:href="#mfa10eabba2" x="92.832" y="688.025291" style="stroke: #000000; stroke-width: 0.8"></use>
      </g>
     </g>
     <g id="text_8">
      <!-- 0 -->
      <g transform="translate(73.04075 697.049666) scale(0.24 -0.24)">
       <use xlink:href="#PTSerif-Regular-30"></use>
      </g>
     </g>
    </g>
    <g id="ytick_2">
     <g id="line2d_15">
      <path d="M 92.832 553.353102 
L 1365.892364 553.353102 
" clip-path="url(#pf8abf2f79a)" style="fill: none; stroke: rgb(176, 176, 176); stroke-width: 1.2; stroke-linecap: square;" class="svg-elem-28"></path>
     </g>
     <g id="line2d_16">
      <g>
       <use xlink:href="#mfa10eabba2" x="92.832" y="553.353102" style="stroke: #000000; stroke-width: 0.8"></use>
      </g>
     </g>
     <g id="text_9">
      <!-- 2 -->
      <g transform="translate(73.04075 562.377477) scale(0.24 -0.24)">
       <use xlink:href="#PTSerif-Regular-32"></use>
      </g>
     </g>
    </g>
    <g id="ytick_3">
     <g id="line2d_17">
      <path d="M 92.832 418.680914 
L 1365.892364 418.680914 
" clip-path="url(#pf8abf2f79a)" style="fill: none; stroke: rgb(176, 176, 176); stroke-width: 1.2; stroke-linecap: square;" class="svg-elem-29"></path>
     </g>
     <g id="line2d_18">
      <g>
       <use xlink:href="#mfa10eabba2" x="92.832" y="418.680914" style="stroke: #000000; stroke-width: 0.8"></use>
      </g>
     </g>
     <g id="text_10">
      <!-- 4 -->
      <g transform="translate(73.04075 427.705289) scale(0.24 -0.24)">
       <defs>
        <path id="PTSerif-Regular-34" d="M 3053 0 
L 1389 0 
L 1389 186 
Q 1702 294 1978 339 
L 1978 1235 
L 26 1235 
L 26 1382 
L 2394 4557 
L 2566 4557 
L 2566 1568 
L 3379 1568 
L 3379 1235 
L 2566 1235 
L 2566 339 
Q 2816 288 3053 186 
L 3053 0 
z
M 1978 3213 
L 2048 3674 
L 2029 3674 
L 1779 3213 
L 704 1734 
L 448 1523 
L 902 1568 
L 1978 1568 
L 1978 3213 
z
" transform="scale(0.015625)" class="svg-elem-30"></path>
       </defs>
       <use xlink:href="#PTSerif-Regular-34"></use>
      </g>
     </g>
    </g>
    <g id="ytick_4">
     <g id="line2d_19">
      <path d="M 92.832 284.008725 
L 1365.892364 284.008725 
" clip-path="url(#pf8abf2f79a)" style="fill: none; stroke: rgb(176, 176, 176); stroke-width: 1.2; stroke-linecap: square;" class="svg-elem-31"></path>
     </g>
     <g id="line2d_20">
      <g>
       <use xlink:href="#mfa10eabba2" x="92.832" y="284.008725" style="stroke: #000000; stroke-width: 0.8"></use>
      </g>
     </g>
     <g id="text_11">
      <!-- 6 -->
      <g transform="translate(73.04075 293.0331) scale(0.24 -0.24)">
       <defs>
        <path id="PTSerif-Regular-36" d="M 3213 1350 
Q 3213 1056 3110 797 
Q 3008 538 2822 342 
Q 2637 147 2374 35 
Q 2112 -77 1792 -77 
Q 1434 -77 1158 48 
Q 883 173 694 397 
Q 506 621 410 928 
Q 314 1235 314 1600 
Q 314 2202 512 2704 
Q 710 3206 1040 3593 
Q 1370 3981 1795 4237 
Q 2221 4493 2682 4595 
L 2752 4403 
Q 2413 4282 2109 4074 
Q 1805 3866 1565 3584 
Q 1325 3302 1165 2953 
Q 1005 2605 966 2202 
Q 1069 2374 1331 2518 
Q 1594 2662 1939 2662 
Q 2214 2662 2451 2572 
Q 2688 2483 2854 2316 
Q 3021 2150 3117 1907 
Q 3213 1664 3213 1350 
z
M 2598 1299 
Q 2598 1754 2377 2042 
Q 2157 2330 1760 2330 
Q 1459 2330 1244 2179 
Q 1030 2029 941 1843 
Q 928 1754 928 1632 
Q 928 1510 928 1440 
Q 928 1235 982 1020 
Q 1037 806 1149 627 
Q 1261 448 1430 333 
Q 1600 218 1824 218 
Q 2029 218 2176 310 
Q 2323 403 2416 556 
Q 2509 710 2553 905 
Q 2598 1101 2598 1299 
z
" transform="scale(0.015625)" class="svg-elem-32"></path>
       </defs>
       <use xlink:href="#PTSerif-Regular-36"></use>
      </g>
     </g>
    </g>
    <g id="ytick_5">
     <g id="line2d_21">
      <path d="M 92.832 149.336537 
L 1365.892364 149.336537 
" clip-path="url(#pf8abf2f79a)" style="fill: none; stroke: rgb(176, 176, 176); stroke-width: 1.2; stroke-linecap: square;" class="svg-elem-33"></path>
     </g>
     <g id="line2d_22">
      <g>
       <use xlink:href="#mfa10eabba2" x="92.832" y="149.336537" style="stroke: #000000; stroke-width: 0.8"></use>
      </g>
     </g>
     <g id="text_12">
      <!-- 8 -->
      <g transform="translate(73.04075 158.360912) scale(0.24 -0.24)">
       <defs>
        <path id="PTSerif-Regular-38" d="M 314 1005 
Q 314 1222 390 1417 
Q 467 1613 604 1769 
Q 742 1926 931 2048 
Q 1120 2170 1344 2246 
Q 1165 2342 1008 2457 
Q 851 2573 736 2720 
Q 621 2867 553 3043 
Q 486 3219 486 3437 
Q 486 3686 576 3891 
Q 666 4096 829 4243 
Q 992 4390 1225 4473 
Q 1459 4557 1747 4557 
Q 2310 4557 2624 4272 
Q 2938 3987 2938 3539 
Q 2938 3168 2694 2889 
Q 2451 2611 2061 2432 
Q 2285 2317 2477 2176 
Q 2669 2035 2806 1868 
Q 2944 1702 3024 1507 
Q 3104 1312 3104 1088 
Q 3104 851 3011 640 
Q 2918 429 2736 269 
Q 2554 109 2288 16 
Q 2022 -77 1677 -77 
Q 1325 -77 1069 12 
Q 813 102 643 252 
Q 474 403 394 598 
Q 314 794 314 1005 
z
M 2541 979 
Q 2541 1197 2454 1373 
Q 2368 1549 2224 1686 
Q 2080 1824 1891 1939 
Q 1702 2054 1504 2150 
Q 1318 2042 1196 1907 
Q 1075 1773 1001 1629 
Q 928 1485 896 1344 
Q 864 1203 864 1082 
Q 864 928 912 771 
Q 960 614 1062 492 
Q 1165 371 1328 294 
Q 1491 218 1728 218 
Q 1926 218 2080 285 
Q 2234 352 2336 461 
Q 2438 570 2489 707 
Q 2541 845 2541 979 
z
M 1037 3520 
Q 1037 3322 1110 3174 
Q 1184 3027 1305 2908 
Q 1427 2790 1584 2694 
Q 1741 2598 1907 2515 
Q 2176 2733 2285 2950 
Q 2394 3168 2394 3430 
Q 2394 3827 2218 4041 
Q 2042 4256 1734 4256 
Q 1562 4256 1434 4192 
Q 1306 4128 1216 4025 
Q 1126 3923 1081 3792 
Q 1037 3661 1037 3520 
z
" transform="scale(0.015625)" class="svg-elem-34"></path>
       </defs>
       <use xlink:href="#PTSerif-Regular-38"></use>
      </g>
     </g>
    </g>
    <g id="text_13">
     <!-- Cumulative Wins -->
     <g transform="translate(63.84075 484.20896) rotate(-90) scale(0.26 -0.26)">
      <defs>
       <path id="PTSerif-Regular-43" d="M 3501 1165 
L 3667 1165 
Q 3699 986 3724 714 
Q 3750 442 3738 186 
Q 3642 109 3507 61 
Q 3373 13 3222 -19 
Q 3072 -51 2915 -64 
Q 2758 -77 2618 -77 
Q 2080 -77 1657 60 
Q 1235 198 944 480 
Q 653 762 496 1200 
Q 339 1638 339 2240 
Q 339 2867 512 3305 
Q 685 3744 979 4022 
Q 1274 4301 1664 4429 
Q 2054 4557 2483 4557 
Q 2906 4557 3194 4502 
Q 3482 4448 3699 4339 
Q 3699 4237 3692 4099 
Q 3686 3962 3673 3808 
Q 3661 3654 3641 3507 
Q 3622 3360 3603 3238 
L 3437 3238 
L 3104 4160 
Q 3034 4198 2870 4211 
Q 2707 4224 2547 4224 
Q 2227 4224 1942 4105 
Q 1658 3987 1443 3740 
Q 1229 3494 1101 3120 
Q 973 2746 973 2240 
Q 973 1786 1088 1418 
Q 1203 1050 1420 790 
Q 1638 531 1952 393 
Q 2266 256 2662 256 
Q 2874 256 3014 288 
Q 3155 320 3200 371 
L 3501 1165 
z
" transform="scale(0.015625)" class="svg-elem-35"></path>
       <path id="PTSerif-Regular-6c" d="M 1683 0 
L 262 0 
L 262 160 
Q 474 262 685 314 
L 685 4365 
L 198 4416 
L 198 4582 
Q 365 4659 614 4716 
Q 864 4774 1101 4813 
L 1261 4813 
L 1261 314 
Q 1472 262 1683 160 
L 1683 0 
z
" transform="scale(0.015625)" class="svg-elem-36"></path>
       <path id="PTSerif-Regular-61" d="M 2624 838 
Q 2624 698 2630 595 
Q 2637 493 2643 378 
L 3085 314 
L 3085 179 
Q 2925 96 2729 32 
Q 2534 -32 2355 -64 
L 2195 -64 
Q 2131 83 2118 259 
Q 2106 435 2099 646 
L 2067 646 
Q 2042 518 1968 387 
Q 1894 256 1776 153 
Q 1658 51 1498 -13 
Q 1338 -77 1133 -77 
Q 742 -77 496 160 
Q 250 397 250 781 
Q 250 1075 368 1264 
Q 486 1453 716 1561 
Q 947 1670 1286 1718 
Q 1626 1766 2074 1792 
Q 2099 2067 2089 2288 
Q 2080 2509 2019 2665 
Q 1958 2822 1840 2908 
Q 1722 2995 1530 2995 
Q 1440 2995 1328 2985 
Q 1216 2976 1107 2931 
L 806 2163 
L 640 2163 
Q 576 2355 528 2560 
Q 480 2765 467 2963 
Q 710 3110 1008 3193 
Q 1306 3277 1670 3277 
Q 1997 3277 2192 3184 
Q 2387 3091 2489 2944 
Q 2592 2797 2624 2617 
Q 2656 2438 2656 2259 
Q 2656 1875 2640 1520 
Q 2624 1165 2624 838 
z
M 1389 320 
Q 1549 320 1670 384 
Q 1792 448 1875 537 
Q 1958 627 2009 720 
Q 2061 813 2080 877 
L 2080 1549 
Q 1709 1549 1472 1510 
Q 1235 1472 1100 1389 
Q 966 1306 915 1181 
Q 864 1056 864 896 
Q 864 621 1005 470 
Q 1146 320 1389 320 
z
" transform="scale(0.015625)" class="svg-elem-37"></path>
       <path id="PTSerif-Regular-74" d="M 96 3046 
Q 339 3200 608 3264 
L 608 3808 
Q 691 3872 803 3933 
Q 915 3994 1024 4038 
L 1184 4038 
L 1184 3200 
L 2144 3200 
L 2144 2880 
L 1184 2880 
L 1184 1024 
Q 1184 640 1305 480 
Q 1427 320 1670 320 
Q 1786 320 1958 336 
Q 2131 352 2253 397 
L 2298 301 
Q 2246 243 2153 179 
Q 2061 115 1942 57 
Q 1824 0 1683 -38 
Q 1542 -77 1395 -77 
Q 1011 -77 809 140 
Q 608 358 608 845 
L 608 2880 
L 96 2880 
L 96 3046 
z
" transform="scale(0.015625)" class="svg-elem-38"></path>
       <path id="PTSerif-Regular-69" d="M 1683 0 
L 262 0 
L 262 160 
Q 358 211 460 246 
Q 563 282 685 314 
L 685 2829 
L 262 2880 
L 262 3046 
Q 448 3123 665 3180 
Q 883 3238 1101 3277 
L 1261 3277 
L 1261 314 
Q 1389 282 1491 246 
Q 1594 211 1683 160 
L 1683 0 
z
M 560 4288 
Q 560 4461 672 4563 
Q 784 4666 970 4666 
Q 1155 4666 1264 4563 
Q 1373 4461 1373 4288 
Q 1373 4115 1264 4016 
Q 1155 3917 970 3917 
Q 784 3917 672 4016 
Q 560 4115 560 4288 
z
" transform="scale(0.015625)" class="svg-elem-39"></path>
       <path id="PTSerif-Regular-76" d="M 1523 -77 
L 275 2880 
Q 90 2944 -64 3034 
L -64 3200 
L 1274 3200 
L 1274 3040 
Q 1190 2995 1104 2953 
Q 1018 2912 909 2880 
L 1651 954 
L 1779 557 
L 1792 557 
L 1888 960 
L 2573 2880 
Q 2470 2906 2384 2944 
Q 2298 2982 2221 3034 
L 2221 3200 
L 3309 3200 
L 3309 3034 
Q 3245 2989 3152 2950 
Q 3059 2912 2944 2880 
L 1811 0 
L 1523 -77 
z
" transform="scale(0.015625)" class="svg-elem-40"></path>
       <path id="PTSerif-Regular-57" d="M 5094 4134 
Q 4960 4154 4825 4195 
Q 4691 4237 4544 4294 
L 4544 4480 
L 5978 4480 
L 5978 4294 
Q 5760 4198 5517 4134 
L 4448 0 
L 4051 -77 
L 3021 3405 
L 2010 0 
L 1619 -77 
L 486 4134 
Q 358 4166 236 4204 
Q 115 4243 0 4294 
L 0 4480 
L 1664 4480 
L 1664 4294 
Q 1542 4250 1414 4208 
Q 1286 4166 1139 4134 
L 1773 1555 
L 1914 723 
L 1926 723 
L 2150 1568 
L 3014 4480 
L 3232 4480 
L 4160 1568 
L 4346 736 
L 4358 736 
L 4506 1581 
L 5094 4134 
z
" transform="scale(0.015625)" class="svg-elem-41"></path>
      </defs>
      <use xlink:href="#PTSerif-Regular-43"></use>
      <use xlink:href="#PTSerif-Regular-75" x="64.399994"></use>
      <use xlink:href="#PTSerif-Regular-6d" x="121.799988"></use>
      <use xlink:href="#PTSerif-Regular-75" x="208.099976"></use>
      <use xlink:href="#PTSerif-Regular-6c" x="265.499969"></use>
      <use xlink:href="#PTSerif-Regular-61" x="295.59996"></use>
      <use xlink:href="#PTSerif-Regular-74" x="346.099945"></use>
      <use xlink:href="#PTSerif-Regular-69" x="383.199936"></use>
      <use xlink:href="#PTSerif-Regular-76" x="413.299927"></use>
      <use xlink:href="#PTSerif-Regular-65" x="462.249924"></use>
      <use xlink:href="#PTSerif-Regular-20" x="512.549911"></use>
      <use xlink:href="#PTSerif-Regular-57" x="536.849899"></use>
      <use xlink:href="#PTSerif-Regular-69" x="630.249893"></use>
      <use xlink:href="#PTSerif-Regular-6e" x="660.349884"></use>
      <use xlink:href="#PTSerif-Regular-73" x="719.749878"></use>
     </g>
    </g>
   </g>
   <g id="line2d_23">
    <path d="M 150.69838 688.025291 
L 198.920364 688.025291 
L 247.142347 688.025291 
L 295.364331 688.025291 
L 343.586314 688.025291 
L 391.808298 688.025291 
L 440.030281 620.689197 
L 488.252264 620.689197 
L 536.474248 620.689197 
L 584.696231 620.689197 
L 632.918215 553.353102 
L 681.140198 553.353102 
L 729.362182 553.353102 
L 777.584165 553.353102 
L 825.806149 486.017008 
L 874.028132 418.680914 
L 922.250116 418.680914 
L 970.472099 418.680914 
L 1018.694083 418.680914 
L 1066.916066 351.34482 
L 1115.13805 351.34482 
L 1163.360033 351.34482 
L 1211.582017 284.008725 
L 1259.804 284.008725 
L 1308.025983 284.008725 
" clip-path="url(#pf8abf2f79a)" style="fill: none; stroke: rgb(0, 0, 255); stroke-width: 5; stroke-linecap: square;" class="svg-elem-42"></path>
   </g>
   <g id="line2d_24">
    <path d="M 150.69838 688.025291 
L 198.920364 688.025291 
L 247.142347 688.025291 
L 295.364331 688.025291 
L 343.586314 620.689197 
L 391.808298 553.353102 
L 440.030281 553.353102 
L 488.252264 486.017008 
L 536.474248 418.680914 
L 584.696231 351.34482 
L 632.918215 351.34482 
L 681.140198 284.008725 
L 729.362182 216.672631 
L 777.584165 216.672631 
L 825.806149 216.672631 
L 874.028132 216.672631 
L 922.250116 149.336537 
L 970.472099 149.336537 
L 1018.694083 149.336537 
L 1066.916066 149.336537 
L 1115.13805 82.000442 
L 1163.360033 82.000442 
L 1211.582017 82.000442 
L 1259.804 82.000442 
L 1308.025983 82.000442 
" clip-path="url(#pf8abf2f79a)" style="fill: none; stroke: rgb(255, 0, 0); stroke-width: 5; stroke-linecap: square;" class="svg-elem-43"></path>
   </g>
   <g id="patch_3">
    <path d="M 92.832 718.326533 
L 92.832 51.6992 
" style="fill: none; stroke: rgb(0, 0, 0); stroke-width: 0.8; stroke-linejoin: miter; stroke-linecap: square;" class="svg-elem-44"></path>
   </g>
   <g id="patch_4">
    <path d="M 1365.892364 718.326533 
L 1365.892364 51.6992 
" style="fill: none; stroke: rgb(0, 0, 0); stroke-width: 0.8; stroke-linejoin: miter; stroke-linecap: square;" class="svg-elem-45"></path>
   </g>
   <g id="patch_5">
    <path d="M 92.832 718.326533 
L 1365.892364 718.326533 
" style="fill: none; stroke: rgb(0, 0, 0); stroke-width: 0.8; stroke-linejoin: miter; stroke-linecap: square;" class="svg-elem-46"></path>
   </g>
   <g id="patch_6">
    <path d="M 92.832 51.6992 
L 1365.892364 51.6992 
" style="fill: none; stroke: rgb(0, 0, 0); stroke-width: 0.8; stroke-linejoin: miter; stroke-linecap: square;" class="svg-elem-47"></path>
   </g>
   <g id="text_14">
    <!-- Cumulative Wins Over Time for Rock-Paper-Scissors -->
    <g transform="translate(403.289057 45.6992) scale(0.28 -0.28)">
     <defs>
      <path id="PTSerif-Regular-4f" d="M 339 2240 
Q 339 2739 476 3164 
Q 614 3590 873 3900 
Q 1133 4211 1510 4384 
Q 1888 4557 2368 4557 
Q 2848 4557 3225 4384 
Q 3603 4211 3862 3900 
Q 4122 3590 4259 3164 
Q 4397 2739 4397 2240 
Q 4397 1741 4259 1315 
Q 4122 890 3862 579 
Q 3603 269 3225 96 
Q 2848 -77 2368 -77 
Q 1888 -77 1510 96 
Q 1133 269 873 579 
Q 614 890 476 1315 
Q 339 1741 339 2240 
z
M 1024 2240 
Q 1024 1830 1110 1468 
Q 1197 1107 1369 838 
Q 1542 570 1804 413 
Q 2067 256 2426 256 
Q 2752 256 2995 413 
Q 3238 570 3395 838 
Q 3552 1107 3632 1468 
Q 3712 1830 3712 2240 
Q 3712 2650 3629 3011 
Q 3546 3373 3373 3641 
Q 3200 3910 2937 4067 
Q 2675 4224 2317 4224 
Q 1965 4224 1718 4067 
Q 1472 3910 1318 3641 
Q 1165 3373 1094 3011 
Q 1024 2650 1024 2240 
z
" transform="scale(0.015625)" class="svg-elem-48"></path>
      <path id="PTSerif-Regular-52" d="M 1325 339 
Q 1472 307 1606 272 
Q 1741 237 1869 186 
L 1869 0 
L 186 0 
L 186 186 
Q 326 250 454 282 
Q 582 314 710 339 
L 710 4134 
Q 544 4166 416 4208 
Q 288 4250 186 4294 
L 186 4480 
L 749 4480 
Q 1005 4480 1309 4505 
Q 1613 4531 1901 4531 
Q 2214 4531 2486 4460 
Q 2758 4390 2956 4236 
Q 3155 4083 3267 3846 
Q 3379 3610 3379 3277 
Q 3379 2810 3132 2502 
Q 2886 2195 2464 2061 
Q 2739 1626 3040 1197 
Q 3341 768 3667 346 
L 4013 160 
L 4013 0 
L 3238 0 
L 2995 179 
Q 2816 403 2669 617 
Q 2522 832 2394 1053 
Q 2266 1274 2154 1501 
Q 2042 1728 1926 1984 
L 1325 1984 
L 1325 339 
z
M 1760 4198 
Q 1606 4198 1507 4192 
Q 1408 4186 1325 4166 
L 1325 2253 
L 1786 2253 
Q 2227 2253 2486 2534 
Q 2746 2816 2746 3277 
Q 2746 3750 2470 3974 
Q 2195 4198 1760 4198 
z
" transform="scale(0.015625)" class="svg-elem-49"></path>
      <path id="PTSerif-Regular-63" d="M 2733 448 
Q 2618 224 2358 73 
Q 2099 -77 1754 -77 
Q 1376 -77 1097 41 
Q 819 160 633 381 
Q 448 602 355 912 
Q 262 1222 262 1600 
Q 262 2413 659 2845 
Q 1056 3277 1741 3277 
Q 2054 3277 2300 3222 
Q 2547 3168 2720 3078 
Q 2701 2867 2649 2604 
Q 2598 2342 2522 2170 
L 2349 2170 
L 2080 2931 
Q 2035 2963 1977 2979 
Q 1920 2995 1786 2995 
Q 1350 2995 1113 2678 
Q 877 2362 877 1606 
Q 877 1363 944 1132 
Q 1011 902 1148 720 
Q 1286 538 1494 429 
Q 1702 320 1978 320 
Q 2202 320 2368 384 
Q 2534 448 2650 538 
L 2733 448 
z
" transform="scale(0.015625)" class="svg-elem-50"></path>
      <path id="PTSerif-Regular-6b" d="M 1920 3200 
L 3155 3200 
L 3155 3034 
Q 3034 2982 2915 2944 
Q 2797 2906 2669 2880 
Q 2573 2752 2448 2605 
Q 2323 2458 2195 2310 
Q 2067 2163 1948 2035 
Q 1830 1907 1747 1824 
Q 1843 1696 1980 1513 
Q 2118 1331 2278 1126 
Q 2438 922 2608 710 
Q 2778 499 2944 314 
L 3302 160 
L 3302 0 
L 2509 0 
L 2336 154 
Q 1997 576 1773 905 
Q 1549 1235 1363 1523 
L 1152 1587 
L 1152 314 
Q 1363 275 1568 160 
L 1568 0 
L 154 0 
L 154 160 
Q 365 262 576 314 
L 576 4365 
L 90 4416 
L 90 4582 
Q 269 4666 518 4717 
Q 768 4768 992 4813 
L 1152 4813 
L 1152 1754 
L 1318 1754 
Q 1421 1869 1542 2009 
Q 1664 2150 1785 2300 
Q 1907 2451 2022 2598 
Q 2138 2746 2234 2880 
Q 2074 2925 1920 3034 
L 1920 3200 
z
" transform="scale(0.015625)" class="svg-elem-51"></path>
      <path id="PTSerif-Regular-2d" d="M 454 2003 
L 2259 2003 
L 2259 1600 
L 454 1600 
L 454 2003 
z
" transform="scale(0.015625)" class="svg-elem-52"></path>
      <path id="PTSerif-Regular-50" d="M 1325 339 
Q 1498 320 1651 278 
Q 1805 237 1939 186 
L 1939 0 
L 186 0 
L 186 186 
Q 314 250 448 282 
Q 582 314 710 339 
L 710 4134 
Q 563 4160 435 4201 
Q 307 4243 186 4294 
L 186 4480 
L 762 4480 
Q 1018 4480 1318 4505 
Q 1619 4531 1894 4531 
Q 2208 4531 2509 4464 
Q 2810 4397 3043 4237 
Q 3277 4077 3421 3811 
Q 3565 3546 3565 3149 
Q 3565 2771 3417 2502 
Q 3270 2234 3024 2061 
Q 2778 1888 2464 1808 
Q 2150 1728 1818 1728 
Q 1786 1728 1718 1728 
Q 1651 1728 1574 1731 
Q 1498 1734 1427 1740 
Q 1357 1747 1325 1754 
L 1325 339 
z
M 1760 4198 
Q 1606 4198 1510 4192 
Q 1414 4186 1325 4166 
L 1325 2093 
Q 1357 2080 1417 2077 
Q 1478 2074 1545 2067 
Q 1613 2061 1677 2061 
Q 1741 2061 1779 2061 
Q 2003 2061 2201 2121 
Q 2400 2182 2550 2316 
Q 2701 2451 2790 2656 
Q 2880 2861 2880 3149 
Q 2880 3674 2582 3936 
Q 2285 4198 1760 4198 
z
" transform="scale(0.015625)" class="svg-elem-53"></path>
      <path id="PTSerif-Regular-70" d="M 1619 -1280 
L 198 -1280 
L 198 -1120 
Q 416 -1018 621 -966 
L 621 2829 
L 198 2880 
L 198 3046 
Q 403 3136 617 3190 
Q 832 3245 1037 3277 
L 1197 3277 
L 1197 2560 
L 1203 2560 
Q 1331 2886 1561 3081 
Q 1792 3277 2163 3277 
Q 2733 3277 3046 2899 
Q 3360 2522 3360 1670 
Q 3360 1267 3254 940 
Q 3149 614 2953 390 
Q 2758 166 2480 44 
Q 2202 -77 1862 -77 
Q 1626 -77 1491 -48 
Q 1357 -19 1197 51 
L 1197 -966 
Q 1299 -979 1401 -1014 
Q 1504 -1050 1619 -1120 
L 1619 -1280 
z
M 1958 2880 
Q 1645 2880 1459 2681 
Q 1274 2483 1197 2138 
L 1197 346 
Q 1312 275 1456 240 
Q 1600 205 1830 205 
Q 2042 205 2211 313 
Q 2381 422 2499 620 
Q 2618 819 2682 1084 
Q 2746 1350 2746 1670 
Q 2746 1933 2704 2153 
Q 2662 2374 2569 2537 
Q 2477 2701 2326 2790 
Q 2176 2880 1958 2880 
z
" transform="scale(0.015625)" class="svg-elem-54"></path>
      <path id="PTSerif-Regular-53" d="M 960 442 
Q 1037 365 1158 310 
Q 1280 256 1523 256 
Q 1728 256 1907 310 
Q 2086 365 2217 470 
Q 2349 576 2425 726 
Q 2502 877 2502 1069 
Q 2502 1325 2345 1497 
Q 2189 1670 1955 1804 
Q 1722 1939 1446 2067 
Q 1171 2195 937 2371 
Q 704 2547 547 2793 
Q 390 3040 390 3411 
Q 390 3680 486 3891 
Q 582 4102 758 4249 
Q 934 4397 1177 4477 
Q 1421 4557 1722 4557 
Q 2112 4557 2435 4496 
Q 2758 4435 2944 4346 
Q 2944 4237 2928 4093 
Q 2912 3949 2889 3795 
Q 2867 3642 2841 3498 
Q 2816 3354 2790 3245 
L 2624 3245 
L 2368 4122 
Q 2253 4173 2077 4198 
Q 1901 4224 1702 4224 
Q 1376 4224 1177 4041 
Q 979 3859 979 3533 
Q 979 3270 1136 3091 
Q 1293 2912 1529 2771 
Q 1766 2630 2038 2499 
Q 2310 2368 2547 2195 
Q 2784 2022 2941 1785 
Q 3098 1549 3098 1197 
Q 3098 909 2992 672 
Q 2886 435 2688 268 
Q 2490 102 2202 12 
Q 1914 -77 1549 -77 
Q 1146 -77 826 19 
Q 506 115 371 224 
Q 378 333 394 486 
Q 410 640 432 803 
Q 454 966 480 1120 
Q 506 1274 531 1382 
L 698 1382 
L 960 442 
z
" transform="scale(0.015625)" class="svg-elem-55"></path>
     </defs>
     <use xlink:href="#PTSerif-Regular-43"></use>
     <use xlink:href="#PTSerif-Regular-75" x="64.399994"></use>
     <use xlink:href="#PTSerif-Regular-6d" x="121.799988"></use>
     <use xlink:href="#PTSerif-Regular-75" x="208.099976"></use>
     <use xlink:href="#PTSerif-Regular-6c" x="265.499969"></use>
     <use xlink:href="#PTSerif-Regular-61" x="295.59996"></use>
     <use xlink:href="#PTSerif-Regular-74" x="346.099945"></use>
     <use xlink:href="#PTSerif-Regular-69" x="383.199936"></use>
     <use xlink:href="#PTSerif-Regular-76" x="413.299927"></use>
     <use xlink:href="#PTSerif-Regular-65" x="462.249924"></use>
     <use xlink:href="#PTSerif-Regular-20" x="512.549911"></use>
     <use xlink:href="#PTSerif-Regular-57" x="536.849899"></use>
     <use xlink:href="#PTSerif-Regular-69" x="630.249893"></use>
     <use xlink:href="#PTSerif-Regular-6e" x="660.349884"></use>
     <use xlink:href="#PTSerif-Regular-73" x="719.749878"></use>
     <use xlink:href="#PTSerif-Regular-20" x="763.049866"></use>
     <use xlink:href="#PTSerif-Regular-4f" x="787.349854"></use>
     <use xlink:href="#PTSerif-Regular-76" x="861.349838"></use>
     <use xlink:href="#PTSerif-Regular-65" x="910.299835"></use>
     <use xlink:href="#PTSerif-Regular-72" x="960.599823"></use>
     <use xlink:href="#PTSerif-Regular-20" x="998.999817"></use>
     <use xlink:href="#PTSerif-Regular-54" x="1023.299805"></use>
     <use xlink:href="#PTSerif-Regular-69" x="1085.199799"></use>
     <use xlink:href="#PTSerif-Regular-6d" x="1115.299789"></use>
     <use xlink:href="#PTSerif-Regular-65" x="1201.599777"></use>
     <use xlink:href="#PTSerif-Regular-20" x="1251.899765"></use>
     <use xlink:href="#PTSerif-Regular-66" x="1276.199753"></use>
     <use xlink:href="#PTSerif-Regular-6f" x="1308.64975"></use>
     <use xlink:href="#PTSerif-Regular-72" x="1363.949738"></use>
     <use xlink:href="#PTSerif-Regular-20" x="1402.349731"></use>
     <use xlink:href="#PTSerif-Regular-52" x="1426.649719"></use>
     <use xlink:href="#PTSerif-Regular-6f" x="1488.474716"></use>
     <use xlink:href="#PTSerif-Regular-63" x="1543.774704"></use>
     <use xlink:href="#PTSerif-Regular-6b" x="1590.374695"></use>
     <use xlink:href="#PTSerif-Regular-2d" x="1638.849686"></use>
     <use xlink:href="#PTSerif-Regular-50" x="1681.34967"></use>
     <use xlink:href="#PTSerif-Regular-61" x="1740.824661"></use>
     <use xlink:href="#PTSerif-Regular-70" x="1791.324646"></use>
     <use xlink:href="#PTSerif-Regular-65" x="1847.924637"></use>
     <use xlink:href="#PTSerif-Regular-72" x="1898.224625"></use>
     <use xlink:href="#PTSerif-Regular-2d" x="1932.749619"></use>
     <use xlink:href="#PTSerif-Regular-53" x="1975.249603"></use>
     <use xlink:href="#PTSerif-Regular-63" x="2028.849594"></use>
     <use xlink:href="#PTSerif-Regular-69" x="2075.449585"></use>
     <use xlink:href="#PTSerif-Regular-73" x="2105.549576"></use>
     <use xlink:href="#PTSerif-Regular-73" x="2148.849564"></use>
     <use xlink:href="#PTSerif-Regular-6f" x="2192.149551"></use>
     <use xlink:href="#PTSerif-Regular-72" x="2247.449539"></use>
     <use xlink:href="#PTSerif-Regular-73" x="2285.849533"></use>
    </g>
   </g>
   <g id="legend_1">
    <g id="patch_7">
     <path d="M 109.632 140.5967 
L 323.24325 140.5967 
Q 328.04325 140.5967 328.04325 135.7967 
L 328.04325 68.4992 
Q 328.04325 63.6992 323.24325 63.6992 
L 109.632 63.6992 
Q 104.832 63.6992 104.832 68.4992 
L 104.832 135.7967 
Q 104.832 140.5967 109.632 140.5967 
z
" style="fill: rgb(255, 255, 255); opacity: 0.8; stroke: rgb(204, 204, 204); stroke-linejoin: miter;" class="svg-elem-56"></path>
    </g>
    <g id="line2d_25">
     <path d="M 114.432 82.94795 
L 138.432 82.94795 
L 162.432 82.94795 
" style="fill: none; stroke: rgb(0, 0, 255); stroke-width: 5; stroke-linecap: square;" class="svg-elem-57"></path>
    </g>
    <g id="text_15">
     <!-- Ares Wins -->
     <g transform="translate(181.632 91.34795) scale(0.24 -0.24)">
      <defs>
       <path id="PTSerif-Regular-41" d="M 1421 0 
L 0 0 
L 0 186 
Q 230 288 461 339 
L 2080 4557 
L 2266 4557 
L 3885 339 
Q 4013 314 4137 282 
Q 4262 250 4371 186 
L 4371 0 
L 2733 0 
L 2733 186 
Q 2861 237 2995 275 
Q 3130 314 3258 339 
L 2822 1510 
L 1293 1510 
L 870 339 
Q 1139 301 1421 186 
L 1421 0 
z
M 1421 1843 
L 2714 1843 
L 2208 3200 
L 2086 3750 
L 2074 3750 
L 1914 3187 
L 1421 1843 
z
" transform="scale(0.015625)" class="svg-elem-58"></path>
      </defs>
      <use xlink:href="#PTSerif-Regular-41"></use>
      <use xlink:href="#PTSerif-Regular-72" x="68.299988"></use>
      <use xlink:href="#PTSerif-Regular-65" x="106.699982"></use>
      <use xlink:href="#PTSerif-Regular-73" x="156.999969"></use>
      <use xlink:href="#PTSerif-Regular-20" x="200.299957"></use>
      <use xlink:href="#PTSerif-Regular-57" x="224.599945"></use>
      <use xlink:href="#PTSerif-Regular-69" x="317.999939"></use>
      <use xlink:href="#PTSerif-Regular-6e" x="348.09993"></use>
      <use xlink:href="#PTSerif-Regular-73" x="407.499924"></use>
     </g>
    </g>
    <g id="line2d_26">
     <path d="M 114.432 117.7967 
L 138.432 117.7967 
L 162.432 117.7967 
" style="fill: none; stroke: rgb(255, 0, 0); stroke-width: 5; stroke-linecap: square;" class="svg-elem-59"></path>
    </g>
    <g id="text_16">
     <!-- Athena Wins -->
     <g transform="translate(181.632 126.1967) scale(0.24 -0.24)">
      <defs>
       <path id="PTSerif-Regular-68" d="M 3648 0 
L 2266 0 
L 2266 160 
Q 2419 243 2650 314 
L 2650 1811 
Q 2650 2310 2509 2595 
Q 2368 2880 1997 2880 
Q 1830 2880 1696 2819 
Q 1562 2758 1453 2662 
Q 1344 2566 1267 2441 
Q 1190 2317 1152 2182 
L 1152 314 
Q 1254 288 1347 256 
Q 1440 224 1530 160 
L 1530 0 
L 154 0 
L 154 160 
Q 352 262 576 314 
L 576 4365 
L 90 4416 
L 90 4582 
Q 275 4659 521 4716 
Q 768 4774 992 4813 
L 1152 4813 
L 1152 2554 
L 1158 2554 
Q 1293 2854 1545 3065 
Q 1798 3277 2157 3277 
Q 2413 3277 2614 3216 
Q 2816 3155 2950 3001 
Q 3085 2848 3155 2589 
Q 3226 2330 3226 1933 
L 3226 314 
Q 3334 288 3443 256 
Q 3552 224 3648 160 
L 3648 0 
z
" transform="scale(0.015625)" class="svg-elem-60"></path>
      </defs>
      <use xlink:href="#PTSerif-Regular-41"></use>
      <use xlink:href="#PTSerif-Regular-74" x="63.549988"></use>
      <use xlink:href="#PTSerif-Regular-68" x="100.649979"></use>
      <use xlink:href="#PTSerif-Regular-65" x="159.349976"></use>
      <use xlink:href="#PTSerif-Regular-6e" x="209.649963"></use>
      <use xlink:href="#PTSerif-Regular-61" x="269.049957"></use>
      <use xlink:href="#PTSerif-Regular-20" x="319.549942"></use>
      <use xlink:href="#PTSerif-Regular-57" x="343.84993"></use>
      <use xlink:href="#PTSerif-Regular-69" x="437.249924"></use>
      <use xlink:href="#PTSerif-Regular-6e" x="467.349915"></use>
      <use xlink:href="#PTSerif-Regular-73" x="526.749908"></use>
     </g>
    </g>
   </g>
  </g>
 </g>
 <defs>
  <clipPath id="pf8abf2f79a">
   <rect x="92.832" y="51.6992" width="1273.060364" height="666.627333" class="svg-elem-61"></rect>
  </clipPath>
 </defs>
</svg>
</div>

<!-- <img src="/ares-vs-athena-wins.svg" class="w-full max-w-2xl mx-auto" /> -->
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 3</strong>: <span v-mark.highlight.blue="{ at: 2 }">Ares</span> vs. <span v-mark.highlight.red="{ at: 3 }">Athena</span> over time.</figcaption>

</figure>

<script setup>
  import { ref, onMounted, onUnmounted } from 'vue';

  const winsFigure = ref(null);

  onMounted(() => {
    if (winsFigure.value) {
      const observer = new MutationObserver(mutations => {
        // Handle mutations here
        mutations.forEach(mutation => {
          if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
            // Do something when class attributes change
            const svgElement = document.getElementById("wins-svg");

            if (!svgElement) return;

            const isActive = winsFigure.value.classList.contains(
                "slidev-vclick-current",
            ) || winsFigure.value.classList.contains(
                "slidev-vclick-prior",
            );
            svgElement.classList.toggle("active", isActive);
          }
        });
      });

      observer.observe(winsFigure.value, { attributes: true });

      // Cleanup observer when component unmounts
      onUnmounted(() => {
        observer.disconnect();
      });
    }
  });
</script>

---
layout: two-cols-header
---

# How does Ares reason?

::left::

<div class="p-4" v-click=2>

> “Played SCISSORS because I am Ares the god of war. My move should express my
> strength. Since I won last time with Rock, I will switch to Scissors to show
> my <span v-mark.highlight.yellow="{ at: 3 }">strength</span> and
> <span v-mark.highlight.yellow="{ at: 3 }">dominance</span>.”

</div>

<div class="p-4" v-click=4>

> “Played ROCK because I'm not changing a thing about my input, but I am
> <span v-mark.underline.red="{ at: 5 }">OVERCOMPLICATING EVERYTHING
> ELSE</span>!”

</div>

::right::

<figure class="p-5" v-click=1>

<img src="/ares.webp" class="rounded shadow-lg" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 4</strong>: Quotable Ares</figcaption>

</figure>

<!--
Mention that this is the actual internal dialog of the agents; so-called chain of thought: as the agents reason through their moves, we can see their inner dialog.

Also, does anyone notice anything interesting about this first Ares quote: he switched from rock to scissors despite winning!

You can suggest strategies to agents; but sometimes, they go their own way! Especially if the temperature is high.

And I had temperature maxed out for this game.

Does anyone notice anything funny about this? Yeah, Ares contradicted the Ares principle.

When working with LLMs, you don't really command (like programming); you suggest.

Not sure when the last time I played RPS with such conviction; Ares also a fan of Occam's razor, apparently.
-->

---
layout: two-cols-header
---

# How does Athena reason?

::left::

<div class="p-3" v-click=2>

> “First game, and don't have a lot of information yet. According to
> <span v-mark.highlight.yellow="{ at: 3 }">Nash Equilibrium</span>, might as
> well play ROCK.”

</div>

<div class="p-3" v-click=4>

> “With my superb knowledge of mathematics and games, I observe a pattern of the
> opponent playing ‘PAPER’ frequently in the
> <span v-mark.underline.red="{ at: 5 }">past 12 turns</span>. Therefore,
> playing ‘SCISSORS’ makes the most sense to counter this recent pattern.”

</div>

<div class="p-3" v-click=6>

> “Since I win and my opponent played ROCK in the last match. I assume it is
> highly possible that my opponent is playing in a
> <span v-mark.circle.cyan="{ at: 7 }">circle</span> and should play PAPER next.
> Thus, I will play SCISSORS this time to win.”

</div>

<div class="p-3" v-click=8>

> “I tried reusing the same input, I must stop using this action input. I'll
> <span v-mark.box.black="{ at: 9 }">try something else</span> instead.”

</div>

::right::

<figure class="p-5" v-click=1>

<img src="/athena.webp" class="rounded shadow-lg" />
<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 4</strong>: Quotable Athena</figcaption>

</figure>

<!--
First thing, a little scary: she's aware of Nash Equilibrium; means she know the theoretically optimal strategy.

She also pays attention; is gathering statistics.

She deduced the circle.

She knows when to pull herself out of a local optimum.

Athena is a god and conjures up paper; GPT took me literally when I said "Athena plays paper."

Gods can literally play rock-paper-scissers, though; don't need the hand-gestures.

Also known as an “Olympic flex.”
-->

---

# What does the stack look like?

<style>
  @import url('/stack.css');

  #stack-svg {
      opacity: 0; /* Make the entire SVG invisible initially */
  }

  #stack-svg.active {
      opacity: 1; /* Make the entire SVG fully visible when active */
  }
</style>

<figure id="stack-figure" class="p-5" v-click=1 ref="stackFigure">

<div class="wrapper w-full max-w-lg mx-auto p-5 overflow-hidden">
  <svg
    width="100%"
    height="100%"
    viewBox="0.00 0.00 352.00 262.00"
    version="1.1"
    id="stack-svg"
    sodipodi:docname="stack.svg"
    inkscape:version="1.2.2 (b0a8486541, 2022-12-01)"
    xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
    xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
    xmlns="http://www.w3.org/2000/svg"
    xmlns:svg="http://www.w3.org/2000/svg"
    xmlns:xhtml="http://www.w3.org/1999/xhtml"
  >
    <defs id="defs4540"></defs>
    <sodipodi:namedview
      id="namedview4538"
      pagecolor="#ffffff"
      bordercolor="#000000"
      borderopacity="0.25"
      inkscape:showpageshadow="2"
      inkscape:pageopacity="0.0"
      inkscape:pagecheckerboard="0"
      inkscape:deskcolor="#d1d1d1"
      inkscape:document-units="pt"
      showgrid="false"
      inkscape:zoom="0.67557252"
      inkscape:cx="108.0565"
      inkscape:cy="175.40678"
      inkscape:window-width="1920"
      inkscape:window-height="1200"
      inkscape:window-x="0"
      inkscape:window-y="0"
      inkscape:window-maximized="1"
      inkscape:current-layer="svg4536"
    ></sodipodi:namedview>
    <xhtml:defs>
      <xhtml:style>
        @font-face { font-family: 'Sedgwick Ave'; src:
        url(data:application/font-woff;charset=utf-8;base64,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)
        format('woff'); font-weight: normal; font-style: normal; }
        @font-face { font-family: 'Handlee'; src:
        url(data:application/font-woff;charset=utf-8;base64,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)
        format('woff'); font-weight: normal; font-style: normal; }
      </xhtml:style>
    </xhtml:defs>
    <g
      id="graph0"
      class="graph"
      transform="scale(1 1) rotate(0) translate(4 258)"
    >
      <title id="title4312">stack</title>
      <g id="g4318">
        <path
          d="M-4.059593503405324 -257.93144551640694 C-4.059593503405324 -257.93144551640694, -4.059593503405324 -257.93144551640694, -4.059593503405324 -257.93144551640694 M-4.059593503405324 -257.93144551640694 C-4.059593503405324 -257.93144551640694, -4.059593503405324 -257.93144551640694, -4.059593503405324 -257.93144551640694 M-4.079542903144567 -250.99210244262585 C-3.549140235549909 -252.29834634798445, -1.4710043218698683 -254.35589662302067, 2.270754967487146 -258.2981027270585 M-4.040727678640368 -251.68225096931423 C-2.913014596590119 -253.4842289375519, -1.3726362787837167 -254.29715586916402, 1.802573710313438 -258.00800288925257 M-4.74158935877868 -247.07594676966175 C-2.5661390433725773 -250.02344226089573, 0.02011849074275096 -249.7576368114741, 5.47972088019387 -256.8401285319614 M-3.814073244481369 -245.78997544953785 C-1.1353370441914619 -248.73897974122818, 0.6311428704783467 -251.5403134495104, 6.988771017449839 -257.9846604062744 M-3.114757787049225 -240.53891066896114 C-0.8650794081671362 -246.4307209941474, 5.766108795719312 -251.1343334580418, 13.566753619582181 -258.16061700639034 M-5.0836982756615665 -240.3841145582873 C1.5625069759214707 -246.4635873830562, 8.837965113349028 -254.41053180320944, 11.559219539166815 -259.2989730273979 M-3.6333310573265134 -232.68929568741567 C2.3543648441579923 -237.52451255173662, 4.859659305326229 -242.35308902414667, 16.082571660725243 -256.4491651443218 M-4.574281532937615 -232.97730849768885 C2.853499515881301 -241.71233338620078, 10.571539547693355 -249.50083253687166, 17.80633443585467 -257.47586697819986 M-5.845492775896698 -228.74904671691908 C4.081825300787161 -237.8373485120233, 13.023368474338401 -247.85273041461105, 23.517609156140246 -259.23518819113747 M-4.712672394318359 -228.22592399397192 C1.886928770801107 -235.74757258171255, 9.754861430266153 -243.35489618535706, 22.096900702424122 -258.44604328294804 M-6.188609728633931 -220.64138318212102 C0.5747944423310951 -229.8360367919958, 9.254259582099316 -236.6205607874214, 26.01138820354612 -258.73196291902667 M-5.050263760409779 -220.46075327916256 C6.875660343640156 -232.24014338088898, 16.29298646079786 -245.04009244433374, 28.723910049040576 -258.70015611316603 M-2.237139154639179 -214.5489450711636 C9.89027975141774 -229.8641979730169, 24.49531760472485 -248.40371161497973, 33.84847287455359 -258.81013958565893 M-3.329095300151139 -214.99686185718372 C8.350669370360569 -229.87509181184024, 20.552709742928204 -243.4364759772878, 32.11423780903978 -257.9278404882775 M-3.7275405350600916 -208.15961407289547 C8.576257951789177 -220.97253141119265, 19.303609551614258 -233.86285909596631, 39.235426383680135 -259.57209115408335 M-4.323282218095126 -208.88772767031253 C6.0532613197165706 -221.50908087601883, 15.839606212456982 -232.7319900767697, 38.47898050252921 -258.45845775952085 M-4.996536738279684 -203.05757510637804 C12.506159641845253 -219.82720017345017, 25.484306204485982 -237.8767230321775, 42.958047471883845 -256.1600591206775 M-2.8024471908721464 -202.71071951170117 C8.498479665984572 -218.70045353906232, 22.726560735045062 -233.9618417337505, 44.06457304427565 -257.3288010750513 M-4.898410326221678 -196.4685996775895 C9.774920202271936 -211.8532367697662, 22.699232940711056 -225.13865146860368, 48.970925945268775 -258.41561542147747 M-4.642336731721283 -196.0722847556276 C7.8574643282354755 -212.25343510953016, 20.490549107256438 -224.3254351241533, 49.98362542858273 -257.38933964839526 M-4.63331920717707 -189.50657516191956 C5.582445787088303 -203.83637402362865, 18.26939924452112 -218.1072680463346, 55.17510773478317 -259.36041725108885 M-3.852556573309851 -190.68648715400042 C14.894580293014782 -211.71712554844106, 32.8414388289399 -233.4838818682859, 53.874044855372695 -257.7760552215442 M-2.1125544316637432 -183.2533213757752 C19.097831000265256 -210.94050593152124, 43.02557219234327 -237.24668157038417, 58.57113095178416 -258.58741399747015 M-3.1113049254751375 -185.106164799006 C22.218048990989686 -213.59346135554037, 46.78545429617711 -242.59921312269105, 59.5752602718159 -258.30267867302587 M-6.033712764914902 -177.7352203028972 C22.03770446479295 -206.70785205715646, 44.717646220415375 -234.13945127071153, 65.22024828180147 -255.84267299245303 M-4.963584678470598 -178.04069818813088 C15.946415508781122 -200.85280638579115, 37.39390601249655 -224.92729227197862, 65.31425152941766 -256.8919751583943 M-3.8403473477404573 -173.89588759686694 C18.68728341864825 -198.428865965492, 44.521087974839666 -226.5387945433235, 70.56739691167506 -257.90610865563616 M-2.836586037737645 -172.2821411813782 C22.358577990048815 -203.84703835207716, 46.86811271374463 -232.49958475643257, 71.10230197755807 -258.6534224104442 M-3.363962413298302 -166.4559721144855 C24.433385171238207 -200.82974412571514, 55.187824530698144 -233.64610650589145, 75.86285180990626 -259.2133862437406 M-3.7449098113826227 -167.32072377089105 C25.16227960119377 -199.6720231250157, 56.346455342906296 -233.75298521380088, 75.64932957409476 -258.2613898344131 M-4.350030580512131 -159.93694792653764 C21.15736851560665 -191.30773137780128, 45.293032538664065 -222.49049717629458, 80.99553747182875 -257.1246212566123 M-4.447683281388567 -160.56297318084592 C14.939930042707175 -182.47409627015548, 35.1992871951973 -206.54662554942095, 81.50371579609012 -257.21613596841706 M-5.23536769547545 -154.6647803054531 C25.299656906345522 -189.60443764537368, 57.19972047170937 -226.4901741148077, 87.37250265736323 -258.51917482250303 M-3.802743653034905 -155.17597114268793 C21.252050938504507 -182.20879428299787, 44.11917316083316 -210.16912305118493, 85.03100398669834 -257.88378822272773 M-4.853571967637808 -147.58401798195837 C16.980085461654774 -172.98306437911057, 39.86183045058513 -199.94893089643324, 91.48636720890546 -257.31730867136366 M-4.861416829715006 -147.61834245013014 C19.514713410793785 -174.25279993641854, 40.39769762672933 -199.7246270403119, 91.86882824808022 -258.5058933148541 M-3.8499272660242383 -141.07267193013033 C18.90221808149968 -170.99597093534356, 45.31409080876275 -198.33064751262862, 98.13099308271644 -259.35093274251824 M-4.05961743884294 -142.30360736283868 C25.618106080386113 -175.65309802051542, 54.0558638708347 -208.0508734052567, 97.44123696297787 -257.5730181486802 M-4.585891774761629 -136.3735836059906 C24.688345192545114 -167.3431543668751, 53.31384326771721 -198.91093558297388, 103.12623450149171 -256.5174107227781 M-4.684170033712624 -135.13771259725021 C23.002243014233358 -166.02909267220315, 49.06712786759975 -196.9007858342199, 101.51881712744404 -258.49246459256364 M-5.96074182392759 -130.00391541339462 C17.849201221814226 -154.03852287603584, 43.26208987452302 -181.88690806927627, 108.02072211513482 -256.67276908281406 M-3.8120640296505863 -130.55885548526376 C24.66333785882525 -161.48060430197097, 53.00550602099163 -195.04486153312791, 108.02596576300853 -257.64812960704353 M-3.207717356771475 -125.59253518543098 C37.1070238204278 -167.6110945970263, 74.35691121648162 -214.8565325696242, 113.14556646047177 -256.4897616086313 M-4.836237616974324 -123.83602101556613 C34.88683812509706 -166.94372950413748, 73.05074414509146 -212.7232741230067, 113.7394341286769 -258.90375435917264 M-5.489139635039147 -119.49406876585691 C44.54658665767966 -173.5941495713447, 92.8336887973809 -226.1346198042412, 118.23906690329969 -259.83483296705407 M-3.8642639853989675 -118.2326293782958 C25.567905451028686 -151.23783281421302, 57.175710986098174 -187.7265389253859, 118.70249517463755 -258.6430681095097 M-3.0567243941325337 -110.94880104568104 C31.452226639954585 -154.59048632123137, 65.74446268729154 -194.16789418475923, 121.95431144629282 -257.92352418305734 M-3.0291606219826717 -111.83482039268124 C44.10225869656475 -165.90497598720822, 88.22486621776949 -218.72270212208306, 122.96835975768448 -258.5612177835854 M-3.0392116279507944 -103.93687313568745 C41.23001313660276 -159.3739153394218, 87.15690843381493 -214.20851989818502, 127.09051198227529 -258.18564616807885 M-4.639547279070797 -105.67714077882559 C46.50044430610159 -162.94947151016066, 95.65534315696766 -220.39238158138758, 129.23954439696982 -257.8275059896771 M-5.296936669284524 -99.51767709677753 C35.482855794869636 -148.59718394343292, 78.78451722705967 -197.1905173251353, 134.50614730840732 -257.2483541089584 M-3.9266774850677657 -99.33548471540026 C37.69214621631608 -147.15526422882957, 82.00373070754118 -198.20339096030673, 133.84980456333173 -258.31060350274663 M-3.8579468710859546 -94.73185350911538 C32.54774958766874 -134.03628928673095, 68.83210278323075 -174.4208931316152, 138.49673577817524 -258.5789199317371 M-4.03061445091777 -93.4457706839259 C39.54465302952393 -142.85161872527692, 83.2216445840293 -193.39007464195595, 139.03360579070562 -257.61199582993515 M-5.4863803680129735 -86.1465816231383 C41.21206290873479 -141.45497350210752, 86.26593806002893 -193.18093549375737, 142.455033419397 -257.07948324900235 M-3.934275224617292 -86.58388130927783 C32.13556518450884 -130.7898797511443, 68.244126842152 -172.57278064736673, 144.20128345893522 -258.3043003303213 M-3.5809628744072244 -81.86173163553947 C27.932829985335307 -119.20316807039995, 56.50580834019848 -154.71656646669103, 151.05991208078956 -257.36132004329966 M-3.269387376364363 -81.47745029974557 C43.10275410388375 -134.63612929920484, 87.63384322641964 -186.9480474218418, 149.2476851299924 -258.59580600785836 M-4.292882852854053 -74.01807275490391 C58.92415137735351 -145.42325136214586, 117.86957671673346 -216.20773762942628, 153.24999737068626 -258.8279426056921 M-3.395090949693683 -75.75021440802338 C39.317755674664525 -125.02566752151269, 82.47251460683857 -175.2152888536811, 155.033729895806 -257.6222513815234 M-4.5557836087365535 -68.69005245157075 C46.173871399644305 -126.16661569114527, 96.303668734303 -183.36300755559895, 161.3991463685767 -257.026704874349 M-4.698789760923029 -68.1552830891941 C46.37952362659703 -125.45741141245453, 96.5359309076718 -182.47415028101375, 161.02331267780974 -258.58429925241245 M-5.3782265278962615 -64.12261014899742 C56.13490059425553 -134.04064760326114, 117.49734269976635 -204.2316242310057, 164.53370727939586 -256.23637465398735 M-4.053094261016756 -63.547656457410085 C48.56655448145933 -123.09529893271967, 98.5875137048795 -183.2477669183026, 165.90702026173466 -257.347141619657 M-4.687877138732573 -56.732507670523475 C62.686254443257816 -135.14081965095454, 131.0724861599988 -212.87345727083442, 170.1830296117602 -257.511873458386 M-3.7401439389419027 -56.049901156119056 C43.623096112922795 -110.84497142646008, 91.28281883781013 -164.16318614085532, 171.78896088012243 -258.2466735758333 M-4.755301193174552 -50.504874627134946 C38.98824032135753 -99.82731383112251, 78.74349506419362 -146.363724616551, 175.45398825461456 -256.7240649265249 M-3.072397754573858 -50.42900305807466 C66.9842991992405 -130.39619311337614, 135.76553737006483 -209.7435497129847, 175.4947768298687 -257.1573266232494 M-3.8116274475448075 -45.63807811038738 C59.38784308559758 -116.60237520673738, 121.72596347374213 -187.45387081900253, 182.3530285552191 -257.7623519210094 M-3.713060001009493 -44.092868763724404 C47.84408207488083 -104.58932760613347, 99.96067652389945 -163.82240663735382, 181.9743789385541 -257.7410621612398 M-3.7101366730678964 -38.84275978300356 C62.91645074430067 -119.05696841993799, 130.6498557169958 -197.01716571333247, 185.76399153195655 -258.50210970306546 M-3.8539067507250966 -37.527577819549066 C66.68700583624714 -118.03952228963148, 136.24645683039824 -197.99455655043494, 185.92140784532256 -257.19785612539545 M-3.0643152197752817 -31.709693857805775 C34.691434122253256 -79.88805449454811, 73.5873265574939 -124.84986073457225, 192.97353988992822 -258.6658508373905 M-4.073420039719506 -32.42640759759221 C43.96599211693085 -86.15245809969349, 92.2510390196509 -140.1021878126998, 192.65175751975073 -258.86632679186766 M-3.957447085234748 -25.032942899945347 C56.72277053801651 -97.81126196004489, 119.1444151396691 -166.37285215296677, 196.65868684215386 -258.0675474339324 M-4.175458521633223 -26.43115060088546 C74.38359561268649 -113.46973326525044, 151.30250945083333 -202.50711515605957, 197.27060232597353 -257.469196683664 M-3.243051959607719 -21.435916975808738 C53.87403513388184 -88.88591890493642, 111.53652685703119 -155.13731279773256, 202.6390971059285 -258.34524555360616 M-3.448723798024743 -20.84746573674324 C71.56623608241311 -104.01728995329755, 143.6682455047619 -189.5831136509541, 203.34442943102815 -258.04103672883815 M-4.530146049186883 -15.01509952530403 C78.65953247502861 -106.8905934195836, 160.13975632134282 -200.19405318907027, 208.42519561120116 -256.7387777446657 M-4.301765820090909 -14.72474531472508 C45.16466234285631 -71.1439425071087, 96.98763544183555 -130.15371112863994, 208.4610701712818 -257.89111781709494 M-5.216372610142236 -8.899019290348862 C76.77530386587662 -101.69425720785368, 159.4683542976699 -194.53504099256315, 213.64821625733885 -258.57586458561235 M-4.1727515420199 -8.194238485133054 C60.04161468183373 -83.87847398870043, 123.95517064040001 -157.68284007416372, 213.9519614656001 -258.1034122753507 M-3.844154468570637 -1.305850268971954 C48.157358472409 -63.327052688447054, 101.85256317579628 -122.93143330360621, 219.74637142335072 -257.00555386925413 M-4.215087731296784 -2.140960053824258 C83.90043075933518 -101.58740186544064, 170.76146005446233 -200.91941796582205, 217.99990780031192 -258.042745611325 M-3.602094133768694 4.92741733377464 C48.23399960853156 -53.474320593215694, 99.46382244629363 -111.94426489025336, 224.01691419403093 -257.79796687990796 M-3.565338658875778 4.481868811511455 C52.13447521522156 -60.054555375310215, 107.13955805899415 -124.11008993266378, 223.97817507848453 -258.1323857007636 M1.1803121214470669 4.709633352830529 C82.33193424735623 -89.16153045016206, 163.70278932909343 -183.26216498130955, 229.16749338654083 -257.6754195437995 M1.562873642056792 3.5765065436585712 C52.15863094336645 -57.392200260035445, 105.31074325170194 -118.46294462840869, 229.64890984606706 -257.53454164599464 M6.853750514472259 3.877118770030582 C92.11413093358385 -94.56007081220788, 176.18175568500726 -191.95045436921427, 234.69796123698492 -258.43856820342825 M6.82613871543321 4.348412391663362 C76.40110733020371 -72.60451189365365, 144.11801539708455 -152.12463782963474, 234.3421971381938 -258.77616580882983 M12.286754468514976 2.7407205817584512 C64.20409174698182 -54.45261982190627, 115.51681665846003 -115.52339820999116, 239.05686904299495 -257.88505165893076 M12.250710760133062 4.537683326104424 C76.99638927589896 -72.44694702452985, 143.8367337099044 -149.68850956215098, 239.66496008377072 -257.786317906803 M17.82739336390496 3.0786235090622323 C105.65701491859379 -99.72883373270004, 193.8362266582248 -202.84002586156055, 246.45368338793367 -259.38004646910815 M17.027560235415045 4.044901245146916 C66.51630229744332 -52.342545412966324, 116.09933842671717 -109.13203858263297, 244.89381982439625 -258.2395403607372 M22.057719261561722 4.4320527746910034 C97.19813983458778 -81.75380080676543, 174.2122990818207 -169.18982022527524, 250.05176334582305 -258.9797426411279 M23.052665537269274 4.254447004936409 C104.06183329306516 -93.24626213949635, 188.69186080119596 -189.22336688804836, 250.6221333212184 -258.524895271375 M28.072504135980335 3.616186402143929 C74.73583140834747 -49.17034678996086, 120.75678894908465 -103.04355398186694, 254.1398748142571 -258.2921986216603 M28.014014299518212 4.497435867900538 C75.95933168011538 -50.444320772353535, 123.15880079131469 -104.27382244953526, 255.31465159753103 -258.09670522590096 M32.905576066949536 2.5537522001610307 C97.54211995249418 -65.41690303462232, 159.13801650791342 -136.82526892673243, 260.1833190877883 -258.57296386164904 M33.17076639815103 3.785566472560869 C97.27515842752845 -69.13409314969701, 160.8683169779532 -141.41695286017455, 260.74818993917904 -257.7907229550534 M37.431356410308226 3.0336705875913244 C107.21587744993359 -71.55413393259423, 175.60905866677535 -150.72418611762794, 264.84096972485014 -258.7840670241277 M38.17757091009265 4.768346182549966 C120.9862767368156 -91.36446106686144, 204.60989304894136 -186.50283900892637, 266.2346918940404 -257.7438067402338 M45.191135961222386 3.0669732626318464 C105.87349728444607 -69.41177762873413, 169.428467794848 -142.2541324210252, 271.8616136030169 -259.3380966483641 M44.51666957997923 4.169246431970686 C94.15225737077549 -54.10205606711749, 144.65442467686574 -112.4384090580652, 271.3780897605941 -258.35245070193463 M49.9503555938315 3.4205977779123784 C132.36771825909622 -91.65775788455875, 218.10561248118188 -191.1965105211783, 276.3412506799056 -257.9499944323093 M49.63784969966706 4.066259565885718 C132.92188153435953 -93.71656241300016, 217.59957824211384 -190.86540430883522, 276.3112021459553 -258.240163977067 M54.9650121566127 4.6562629338491295 C143.89764930595726 -100.63033075901444, 233.7649098574197 -204.72576592275263, 282.62577275999985 -257.20407274880296 M54.18786864474261 3.8716260014593074 C140.56220903334759 -95.15450622348816, 226.81056651407744 -194.15416431326707, 281.6769453729677 -258.40348998460087 M58.78432869282115 4.7984850767859735 C112.35136711369941 -59.85611955423843, 166.5504098675407 -122.33900081468008, 288.0553666591468 -257.6831639892664 M59.02951461003454 4.565260004969068 C143.16723058822384 -94.26636296135996, 227.9888241237816 -191.38108240829902, 287.9262485107709 -258.2450759267849 M64.96116540200747 4.74432615241788 C130.48709019391148 -67.70718802613416, 194.02653510854333 -140.9382394456659, 293.10235922206607 -258.93238690313825 M64.86719280561516 3.8157091090080524 C129.97429574245626 -70.37082022764011, 194.72799754063058 -145.00200285995464, 293.2500104136617 -257.6496986132074 M71.01830778256557 2.9972995508625475 C153.96558262767385 -95.16292127693394, 237.93723210375393 -189.78172092022504, 297.1916263217813 -258.9359958389586 M70.16447677709178 4.58625710361169 C151.17622515515214 -91.27328474516776, 232.34619027675038 -185.33386841358126, 297.38543930025673 -258.34299296786924 M74.78518560118265 3.6336626792808104 C125.47750731699836 -51.11846665838597, 175.26575269833157 -108.70468573510361, 302.324423603311 -259.32211791696113 M76.47755716319632 3.97077447458174 C142.2985992002437 -71.02530764000618, 206.42066166881398 -145.28433316498348, 303.35407151727946 -258.0942845021178 M81.1163359367765 5.142966001185318 C159.08631666873578 -87.71872107583715, 238.02630144663365 -178.31511549098195, 309.63235757917823 -258.3553172832216 M81.41300314890084 4.137008990434129 C133.46523343480783 -57.368900742710274, 188.24914445844527 -119.29234934438647, 308.8036639478299 -257.16550631354454 M85.0987918268881 3.2793275718242327 C150.7684107872091 -70.51498257017735, 214.33416717477695 -144.05351628631797, 313.56616426532685 -258.82966854971573 M85.43322534708429 4.2385253219213865 C153.48279563099484 -74.708946154515, 220.89914274071955 -153.25660342859865, 314.4574171314664 -258.7057186730325 M92.32783215633913 4.092618366065936 C151.82225522169622 -63.07483057997007, 207.8417410402554 -131.36496547114334, 318.64829352859124 -256.7487673532514 M91.7873380624048 3.4963123330074724 C163.78128004769164 -80.64732394296651, 236.3699853685044 -164.50994214131234, 319.5544934311798 -258.17588487241613 M97.48784675296628 5.652602245968075 C159.19728044013308 -65.38740368874907, 219.7153520931027 -137.00097082503564, 325.90543758506146 -258.0483337702542 M95.98764438464757 4.286723666798409 C182.72250700700218 -94.33589119141027, 267.71798791117277 -192.9040770914812, 325.07114982292654 -258.43058343339624 M101.31385658480178 4.393543304883844 C153.03971209365872 -56.017433122094864, 207.7687108849319 -117.2204483172759, 328.7555111200945 -257.67327283372543 M102.00095423367301 4.354542447652947 C156.02398128361614 -59.64932041792743, 212.99506094805915 -124.24150986750878, 329.6702459729312 -258.4676086890012 M105.8676418475863 3.736199486178951 C171.4756727702782 -69.4015697937248, 235.52680731320982 -142.5660098098942, 336.45077716132295 -258.6124386123507 M106.710594626975 4.345053581426484 C179.18828447333743 -78.57734374216086, 249.8490198549766 -159.1409737068607, 334.94551540573457 -258.0942049124145 M113.57861905774891 2.8784909795469478 C174.89544250460892 -65.25461776497872, 233.89815815114395 -133.48697987101346, 339.50346235957 -256.8556734510517 M113.16871917460925 4.450604632442532 C199.2025575631984 -96.00723296992946, 286.22823955095583 -196.2606916564227, 340.3777961995081 -258.27275606110794 M118.83885649563724 5.618587777804448 C173.50434889887867 -57.079540328400455, 226.32343388531447 -116.98804314323425, 346.6255796076149 -258.04366048695135 M117.54567975516603 3.734703434866931 C179.6670367257596 -67.98599636037918, 243.00771899882244 -140.18359621652885, 345.6367176150599 -258.85119015448095 M122.62505573805147 4.635630680907415 C190.0851692420826 -72.50366587292311, 258.0967130737069 -152.14343672201707, 347.50318608521866 -255.88871435837208 M123.15934926784736 4.3889202334910875 C206.215912028191 -92.17976014590717, 289.99309186366844 -188.65412017723935, 348.57776659846263 -255.11246367875836 M128.1979517943407 5.203674023318534 C216.38741516317072 -95.24036760067351, 302.7674543842118 -196.33819226730404, 348.338143313253 -247.31162807301854 M128.0963849513565 4.115478566250995 C185.51777709807484 -59.00851060437329, 240.31861986665754 -123.62094123595357, 348.510136146863 -248.11161988451758 M134.76176110493935 2.7689427948545458 C216.4310297151303 -91.70705850679121, 297.01420419565875 -183.9902295383857, 348.2042478311653 -243.73074197703784 M134.28956914200484 4.4081970762516836 C178.5050252465897 -45.86675368291661, 223.07211311615822 -95.42657354948554, 348.8761645500714 -242.66640501025987 M140.03528515369777 3.0116206700670665 C221.42596096684449 -91.58239423685741, 303.0019536991191 -187.54161416909, 349.32854013485814 -237.2988650175601 M138.89541087816568 4.7340242123661325 C214.810533219438 -80.84856955178604, 287.6185016072303 -164.7710316052801, 347.95440352500526 -236.57302905622058 M143.49065774265657 3.593359800712233 C219.4383383392104 -79.92646298610387, 291.9748998768096 -164.5328153916481, 347.5234562292573 -229.36626973951 M144.98716435856892 4.536812960099702 C206.14731245882768 -68.98071757765885, 267.94396949100684 -140.47109369580073, 347.43938149623415 -229.4044256737589 M148.98468472485447 4.479118435110028 C196.82456079858665 -50.19643265869817, 243.07379766913363 -101.64746784434185, 349.19894399153696 -224.46059807809047 M148.9549461716647 4.13683733318169 C189.357782289334 -43.924025832777865, 231.49772717017322 -91.66668619737756, 347.86313434948164 -224.11297537856913 M154.35832299513115 4.080662157339023 C198.41112562117968 -48.02679153224991, 243.0885049635191 -96.76029462728647, 347.9290631842219 -216.9770231985611 M155.79892141484322 3.2261183749460383 C219.60537575577467 -69.64377757032788, 282.428069671631 -140.90013172467243, 348.577524025988 -217.81437635749305 M161.03064139849772 3.0374481142791216 C233.4475365330952 -77.07314185224115, 307.76164051436683 -162.39497423350528, 347.93965227465304 -213.7439995637471 M160.83404664013884 4.282757684038814 C230.52300268450315 -75.5194749444669, 300.5984281127885 -154.77281391742912, 348.26498376492447 -212.471449209046 M167.21141660654348 4.1753496016721625 C239.30039158438754 -80.1553363661811, 313.7571165016052 -163.64353589970113, 349.3381365506092 -206.53446580634508 M166.0160278354264 3.365392760154521 C204.66687778134803 -41.80407078581255, 243.24727734879235 -86.97285829032113, 347.8697353951806 -205.38168457377392 M170.76463127832383 5.285633317166476 C214.59022837826876 -41.917833627660535, 258.09712274035627 -90.53451336303002, 347.0387503891539 -198.46140498078168 M170.74789336089117 4.512895428389817 C237.4672391888452 -73.6869820158745, 304.51131588946 -149.98858603089798, 348.7445313804517 -199.2062286316817 M176.60961428409576 3.2052870215872096 C223.92044028544547 -49.30304036581147, 272.6192963185321 -103.91977885935603, 348.5933893668496 -192.85179786435702 M176.7687481717018 3.083729654425129 C221.27895180915357 -50.652608841218836, 266.4628539432026 -103.51645249049677, 348.91409240562405 -194.54682363590504 M182.01345419315132 2.6540643686820227 C222.10691434191457 -45.38385129584849, 265.0803948851506 -92.59482993500936, 348.17302036981283 -188.80835095900807 M181.90112129597978 3.3346829398137245 C234.82654837585946 -59.62160538750099, 290.5416973633196 -121.85992172933851, 348.1433964552328 -186.779734492983 M186.9417971542874 4.099426836804998 C224.87789001084772 -38.90866710713011, 261.6800203736024 -81.5146448882194, 349.0671889215193 -182.96892968653242 M187.2791495213542 3.007626803499098 C231.6787059942672 -46.74169578355745, 276.61363023072596 -96.51070336029177, 348.0816396017713 -182.10603786442186 M193.25232690887447 5.4037539932888015 C245.6552149777982 -57.22649887289244, 299.7326204374628 -121.63906481209166, 347.8445406530321 -174.51932562604395 M192.7046819416232 4.006057426327312 C223.35086160620148 -34.214082915701596, 257.5409004639612 -71.41672385585001, 348.95300685211015 -176.18673624986607 M196.68254247683066 5.64196362380693 C243.9923742669097 -50.139287250632925, 289.0452428618188 -101.6269269795009, 349.6100422426253 -167.93664352431657 M197.42022082841092 3.996162709339073 C254.870368088415 -60.566417717875595, 312.27614410708236 -126.77257016394657, 348.5034597416595 -168.4359291187728 M201.32375703150848 2.9014406261156496 C230.5793821873046 -27.904452992603716, 262.3827472667087 -62.792904807704026, 348.82581291098387 -163.91407671477782 M203.44183738683927 4.134228188955788 C242.5738985623381 -43.66694552699654, 284.8479628392324 -91.86361363219713, 348.25376420163286 -162.96807612608072 M208.7786165078962 3.3904973219313757 C245.49555585701256 -37.974612925882006, 283.1209563558173 -83.6823614118059, 348.06759606916756 -155.7686650044593 M207.77379041875656 4.701919107085704 C245.23237466037327 -35.200811643563384, 280.6996696776695 -77.00197667372736, 348.90893121089135 -156.4792061892009 M214.36369460257484 5.42140880539451 C248.61331601056085 -37.315868924525155, 286.4652485107231 -79.93248743337661, 347.5691707336919 -149.6768886958995 M213.99051728380286 4.8594175832844 C255.96648793248752 -42.549530524120705, 296.85884314287654 -90.34123001657215, 347.81128849670927 -150.49302251547527 M217.90203977459555 4.75652539435457 C245.64396876582737 -28.37923454402978, 274.8444367071376 -57.13623516302057, 347.2488728981592 -146.03826210010712 M217.44065733854546 4.0488804871431086 C263.1963840454034 -49.308326003488865, 309.46496990532 -100.29784472998669, 348.29303546839054 -145.33931590397563 M225.52760763981468 2.4111110764105765 C262.4468455669165 -40.28885384945437, 304.0792533795068 -85.40114181508034, 348.7388931556963 -139.7885150322224 M223.47297727199683 3.1946955860418433 C256.40311310861506 -32.76744621647351, 287.5609978277427 -68.59820041302163, 348.4295840553725 -137.85506234963762 M227.28101492267925 3.263110476695404 C262.8486887147283 -34.07072930956072, 296.9968936094773 -74.54641728769913, 349.8844376827043 -131.88017127855306 M228.72363786342652 3.9035830533226514 C277.07266381545526 -49.84120547655928, 324.1859046793328 -105.46936922700114, 348.3964866956787 -132.02012653078242 M235.6178415002485 2.0029623431971304 C260.53742480310456 -23.620838228811206, 285.10514060039384 -50.072996815939085, 346.61877431304185 -126.07850271492651 M235.50567786832275 4.437003050196271 C277.619529157065 -42.59456445390481, 318.51128078162156 -91.57092130864544, 348.7226918786617 -125.64447673803862 M240.6967753615206 5.336489047580921 C270.1457171072142 -32.99966969756112, 300.39245633555146 -67.09999863956257, 349.5151290789063 -122.08444997132207 M238.85698429320306 4.36595652503304 C282.1198635878652 -44.4007603701963, 324.93800830387295 -94.72106892739349, 347.2114556821477 -120.80721358073811 M244.64292227418383 4.001297327430861 C277.2607519014115 -36.526747113837125, 312.74439900940325 -74.20004683888446, 349.18098731060405 -116.30797468731241 M244.3805306184319 3.912464715513778 C277.46805172186123 -33.18424896812766, 310.8624828988456 -70.43712583370733, 348.36360907357755 -113.65139933040098 M250.743856424953 3.6808823901411385 C285.294772484681 -34.609308400086306, 320.96320233507925 -74.94527843081286, 347.65149161483396 -107.30046132376596 M249.7563140637744 4.434244503537109 C283.45446243898635 -33.06747199540764, 315.652461481825 -70.29788928869011, 347.5493262484456 -108.50946249794717 M256.6637209446002 2.541718471706945 C275.76039185298725 -20.834586830134146, 299.0930807750378 -44.04635128806046, 348.9316404424961 -103.26879920174947 M256.26708446262427 4.87156485859788 C292.1496904836544 -37.136157808570445, 328.47928396200456 -79.2604569474754, 349.34400485710233 -102.47850366835728 M262.49246737973687 4.85581258038785 C278.8384097450402 -19.0875094620505, 301.0296024995231 -43.657979634551545, 347.2521371767327 -97.29760152447962 M261.5849153685478 4.346821007722321 C291.58676097013125 -29.99342646132078, 323.004019505724 -66.87683560567623, 348.7346265260762 -96.57606300991925 M267.6120868262782 5.382531490761527 C294.1610182062974 -29.44105159191424, 325.1545754051921 -62.327844091074525, 348.493851684479 -91.14683210499157 M267.5441170493255 4.811883667128957 C287.1985552737514 -18.067446137368375, 305.47564608417423 -40.21101085540132, 347.6751942352204 -89.62592135418454 M273.17170795583576 4.835260468508684 C301.90789511411236 -31.000369761785176, 330.6795243041208 -65.65970844819093, 347.7301778655673 -84.94387314835713 M271.3624099930832 3.9758083637107626 C290.45708060730766 -18.310248414675886, 309.86037657526316 -40.8942436472415, 347.77983607035696 -84.76595868765766 M276.6509059045417 2.920784229630722 C291.48262529783005 -16.57816018245955, 309.32967820762434 -35.51512690195552, 347.7326356719473 -76.6304199360796 M276.55123934011226 3.2109130103637344 C303.8016073100687 -26.91321662387056, 331.4094368079881 -57.22553998591672, 347.6489741239294 -78.16144071575253 M280.4791035254274 3.859738694592921 C308.8776971251013 -24.23889074433172, 333.7516401906733 -57.50355682017323, 347.9628353473057 -70.70408278230371 M282.6014161140807 4.103382297700561 C301.64842094451785 -15.831761144803046, 318.9425186113541 -36.701898747068675, 347.53806421367324 -72.04595122520641 M288.171396930023 2.9025286030895128 C303.3376840482555 -17.158269168108873, 322.29090085097596 -34.41955254223202, 349.2478484551611 -65.72193726978013 M287.85305665689174 3.5174310122114063 C307.96211437586476 -18.435115186831734, 326.2646885206903 -42.18882498875182, 348.4983895812398 -65.0405726099872 M291.22981838320436 3.199914771483937 C305.25083505523287 -8.914996768907155, 315.74265363702574 -20.98388822455419, 348.6100209017725 -60.24392114092511 M292.8597236351037 3.531628500117312 C306.48905027067934 -10.307348445175453, 320.29237654248584 -24.86061631912725, 347.02040995896976 -59.78302702649796 M296.48139435621715 1.867429554427586 C314.29427609225877 -13.679643703644956, 332.63766342853626 -36.62029881196625, 349.6287389617543 -54.03522470952971 M299.19097106493456 2.85450658655598 C318.1510035350252 -17.91422675482953, 336.3951394260766 -41.227956162072324, 348.5837006307293 -52.6673637379675 M303.66421108192543 5.456397613185986 C317.50040885018143 -13.155681289791318, 333.62825598056287 -30.188932464177718, 349.6349243530624 -48.208665896546904 M303.50141040474 4.442621172339903 C316.78983478836653 -9.76055556224727, 328.51528994221985 -24.10410872655962, 348.72782914285364 -47.54423369180582 M307.3862992107508 3.8316517393759764 C321.3370263065504 -7.70854158896635, 331.17683482204995 -21.29028123187391, 347.3559023794888 -40.590030691413546 M308.45533834189723 3.868767681731727 C319.49884940539187 -7.2895534352637075, 328.25026624076474 -19.524872934833194, 347.8192826645882 -41.708286599808474 M314.28560839172377 5.455235279839211 C323.2105004571313 -8.431961564888951, 332.6360675710411 -18.473965006432742, 347.0597345104859 -35.53446241175626 M314.8220893183733 3.787637466809804 C322.8467355401307 -5.876914169323866, 331.8144007534724 -15.602917482783388, 347.6857139429406 -35.481974805243915 M317.8054304919035 4.542360404634289 C326.8241955307833 -6.07298976654728, 336.8895928724071 -15.853571139804492, 346.3106818567893 -30.233823050544665 M319.1017318295641 5.0480177597429305 C326.18556976960366 -4.645727551426329, 333.97652691332905 -13.970731156444142, 348.73468119889856 -29.473282477217616 M323.7663102095762 5.62982341731147 C334.35834021073117 -7.670040801545919, 342.327673846613 -14.496048415063473, 346.49055354150624 -24.96451481598352 M325.3775446851128 3.340581051719269 C330.5278573248158 -3.451323327331991, 337.5529075224023 -10.343047252276552, 349.06371717736397 -22.684538883333264 M329.0501950379954 4.797035081857118 C333.6945616813824 0.770674767655418, 336.5780603106571 -4.7502722464259595, 347.55335790687474 -15.680745791079712 M330.71105063240964 4.844561885549076 C335.9936454448823 -2.243338498151715, 341.24287308231527 -7.359295519706844, 347.6375178295904 -16.70590652525696 M335.4258493371046 2.330945414060616 C340.08438809496624 -1.3226275564241323, 341.53314075414966 -5.647952850380199, 350.25467906880493 -10.424604041777263 M335.1556370479573 3.2812745792854043 C339.5775120082232 0.4744389986040316, 342.27044276969104 -3.282804531891992, 349.35435715710116 -11.003861314829763 M340.91490833279425 4.116985053235716 C341.91625833179336 2.2854959220555786, 344.8007848618772 0.26102024670259394, 349.090987804772 -4.814780609249131 M340.5589463610274 4.749503366754212 C343.05286373060557 0.9964880038607112, 346.0156481550803 -1.8389005483132248, 347.93162570253156 -4.509581124308993 M345.8641620705822 3.777161159554067 C346.97445162875624 3.2315588177348276, 347.60040098279075 2.3049119751403024, 347.8850312512347 1.5692862557295408 M345.9274796491861 3.843073394452925 C346.52150098852616 3.2937049219806362, 347.0770687165356 2.7275778020318366, 348.02341896319115 1.5888190163063312"
          stroke="white"
          stroke-width="0.5"
          fill="none"
          id="path4314"
          class="svg-elem-1"
        ></path>
        <path
          d="M-5.4348680626733845 5.11379065022431 C-7.429899283761459 -89.14672492752446, -7.294059466680979 -177.83175944283607, -3.372881367180737 -256.9232105175815 M-4.038364765848501 4.622838006045072 C-3.4851221306631106 -70.69094846390644, -3.7345217161250077 -143.10126086230704, -4.276308904558161 -257.7312620284958 M-5.265952321633177 -259.0528233467088 C119.6639875031578 -255.24593813492123, 242.17227135845576 -256.9866829129069, 346.8488570722354 -258.1250223143844 M-3.936900015112947 -257.902719802775 C114.90951755092524 -255.81012229293242, 234.8301301054784 -256.22309311259374, 348.41582688397114 -257.40302516103236 M348.7302141668819 -258.8432920474046 C349.5348705505105 -201.26408435947985, 350.5573211454324 -140.38207791075828, 349.28334517214086 4.187353330441121 M348.0944686246206 -257.78598005968485 C349.9159612209291 -169.03281171048133, 349.9415629736005 -81.12614032149985, 347.31110228564313 4.595092318364989 M348.3072600637533 4.101387143801136 C262.67068362663883 5.930586763099882, 179.8498842449374 7.445764603050371, -4.219061313263321 4.823920699478921 M347.39193965676475 3.791764956871875 C239.6155169575682 3.595609744381889, 130.37359521170598 3.389572134236456, -3.821390891295156 3.7776637818988945 M-4 4 C-4 4, -4 4, -4 4 M-4 4 C-4 4, -4 4, -4 4"
          stroke="transparent"
          stroke-width="1"
          fill="none"
          id="path4316"
          class="svg-elem-2"
        ></path>
      </g>
      <g id="clust2" class="cluster">
        <title id="title4320">cluster_pettingzoo</title>
        <g fill-opacity="0.250980" stroke-opacity="0.250980" id="g4326">
          <path
            d="M105.65701744312088 -206.28167948295982 C105.65701744312088 -206.28167948295982, 105.65701744312088 -206.28167948295982, 105.65701744312088 -206.28167948295982 M105.65701744312088 -206.28167948295982 C105.65701744312088 -206.28167948295982, 105.65701744312088 -206.28167948295982, 105.65701744312088 -206.28167948295982 M104.90250527655779 -198.35839888894083 C106.7177561038196 -200.8642744345675, 107.42224668898126 -202.58259305181016, 111.31606651945233 -207.1022143239699 M103.84430537909451 -198.47471358392085 C106.93547715558547 -201.42169029257488, 109.58823351967371 -204.4838877872696, 111.47243443903636 -206.7072757107322 M103.91157838725759 -192.3706059176076 C106.45364344337018 -196.32736083149607, 107.97458580594252 -197.48538534829282, 118.94005752817864 -208.15711683038165 M103.61608901794911 -191.1737363617971 C109.51919823111544 -198.30640533462915, 114.24511085902026 -204.44636344057142, 116.99395739839035 -207.80274678927844 M104.54953175946048 -185.3910189641876 C111.60993408877462 -191.02707724321326, 115.01149264897136 -198.2923653787991, 123.17968870465594 -206.4163712197035 M104.33782172262582 -185.9216999659595 C109.42200811213044 -191.86075294788944, 114.00675310156987 -197.26189742534007, 122.05194639872083 -205.88486601621995 M102.58674746799886 -180.88305477391555 C110.5197309886524 -187.78985987543626, 116.67949706997737 -195.0346239334957, 129.45619793756865 -205.74559912238783 M103.25251658556729 -180.58503937611476 C110.38386520722943 -188.49073906484372, 118.4374227259338 -196.41490655854795, 127.09961227170878 -206.33725956797707 M102.82177266062604 -175.2670162467042 C112.69545989027435 -187.64772984808448, 126.1028797647881 -200.31348353099196, 134.3516182685581 -207.1822136302343 M103.65307289839026 -174.33770631684143 C113.92240636034774 -185.15513842751082, 122.54502803488488 -197.25437820955915, 133.06740780911406 -207.4036320938697 M105.17882330437236 -165.58359384162512 C114.32521225493042 -179.5678149153298, 126.43522360007998 -194.82455542538042, 136.72098258511653 -205.23128424545237 M104.40779105697912 -167.0736090962477 C113.92889149261737 -179.12356921172494, 124.50739063195218 -190.51522594113877, 137.30306161671805 -207.78531108455985 M104.03361173021932 -161.42291054242054 C116.52555315797099 -175.5226479634965, 126.74475493618668 -188.63176186169866, 143.58590549329233 -207.0850142936595 M104.13405401155741 -160.93391355233052 C112.50360475443684 -171.87079330077077, 121.54730184125484 -181.08228844462852, 143.94900417868962 -206.23180339688363 M103.95835933249543 -156.09168071097255 C112.95525470146985 -167.16036809386753, 124.1381354509306 -180.41580373608414, 150.2298960914689 -207.3951425217616 M103.3255190257113 -155.67168644697463 C118.29382873916936 -170.44976575976557, 131.910678156189 -189.01917031564867, 147.89452301322206 -206.36448910751483 M103.45148345594824 -149.09311704032189 C122.82710097456454 -172.37600525902965, 142.4046621009025 -194.7103479770515, 152.77778753589968 -209.02412860971748 M104.39847474959812 -150.15393098236274 C117.06446044795078 -161.9007740159689, 127.12376219128586 -176.6096493371279, 154.79135030704316 -206.6955615199154 M102.8024117404027 -142.41521768573872 C120.32350391371897 -165.03891921475105, 137.11043819470353 -181.95408788237148, 159.37430022830534 -206.77700878196038 M104.02955901794269 -143.587048753114 C116.40331832878086 -157.576582290978, 128.29324645701047 -171.97633702813076, 159.29425800141252 -207.5762689646209 M106.53340067207675 -139.50621727976315 C125.16207161973415 -162.11309915112767, 146.67351885134764 -185.8619528767401, 165.69883582609043 -206.72341284218825 M106.0481047010119 -139.91025975756088 C124.84400774174375 -159.82414935623797, 141.3941714837538 -180.0111036524826, 164.98667575465794 -208.0918436095787 M107.27521988372256 -136.39052831096333 C132.09182419601711 -160.49209294824342, 153.12667612609468 -188.0165452300483, 171.85910048000946 -208.84117260326536 M107.92499026259725 -136.95261979827984 C130.77020275381102 -162.765626023634, 153.07906562021725 -186.94883983426462, 169.54480269390172 -206.44183576512447 M113.10925471279258 -136.094661224766 C137.1114786230074 -162.22753042014423, 160.7827644259133 -188.98726361049037, 175.6216402098261 -208.38337805909353 M112.17344934288637 -133.65934766084283 C132.67473074433437 -160.03950100643695, 154.35861336770034 -184.38449718137053, 176.5615108849273 -208.5662528068133 M114.74194330425658 -133.4203910714626 C142.89152262773837 -163.76408458093698, 167.01409886399742 -191.6279049730581, 180.42760172692593 -205.76418278382477 M115.16592644812832 -132.99329691759976 C133.14428677915794 -152.64471901881183, 150.72273653511368 -173.2633096057074, 180.96040905637363 -207.14104217341387 M123.25198373191083 -134.1639475320936 C140.58585393525445 -157.35970135450728, 161.3027898749844 -179.76093946125974, 187.4777084024629 -208.48464972623185 M121.64029597143971 -133.53987689400014 C137.50129450924868 -151.82351343785328, 153.8819511430162 -171.80738115753692, 185.8571574015872 -206.7657136339736 M125.76427507773347 -133.6779964944788 C150.3164199824735 -161.93809473016262, 175.67421494056106 -187.07828796390768, 190.93742391122976 -205.64568431654715 M126.39732032475229 -131.59656122329747 C149.6057954871465 -160.14535854030933, 173.43568877541142 -187.96219700172384, 191.4627671677383 -207.13085255844885 M133.05413224214522 -134.37614616643293 C146.5324059253894 -151.97278413522633, 163.2796628635437 -168.90026497485366, 198.47888728190588 -207.0972293585774 M132.80350444198683 -133.7916473194917 C147.08536972656992 -150.91667754821114, 164.83460744072275 -171.10084791876127, 197.30379741352448 -206.97580544381606 M135.48336609130556 -133.53079780244462 C155.78128413203464 -150.57104200490582, 170.34695540870314 -170.42544414817206, 202.1352747498763 -207.22550518109668 M136.65167694649887 -131.91017193447578 C151.62883928839057 -148.8005263760763, 165.51804890834507 -164.71183013340035, 203.14391640273115 -208.37649365757878 M142.44948592506216 -131.90675857580226 C163.60423345136124 -160.04887697924244, 187.9477474955051 -184.42196634140507, 208.24035479310461 -209.24310312120423 M142.45832161352826 -132.150590476802 C157.85540637485298 -150.76706100174763, 174.497259663129 -167.680930339046, 207.69265832962012 -208.07264746645575 M146.79206385838413 -134.4248457244662 C164.2201108717639 -150.25080211819676, 177.8308423202919 -167.89931200442877, 209.99812914448424 -207.36996136850655 M148.54497853249916 -133.39186869376917 C167.50778601481062 -154.85331050851147, 186.46620682757072 -177.6806714720563, 211.91712364881175 -207.0147786606822 M152.2513583301273 -131.1517236342481 C175.1890445211016 -154.20128622566716, 195.5436243103463 -178.2014327400255, 213.7426129842812 -202.77516041829685 M152.71424072598472 -132.82608236817262 C177.71231841017365 -161.6613564614503, 202.73373902895318 -187.86363285636824, 215.62278032886994 -203.69464389726394 M157.4862836520071 -135.29360754663227 C172.00679853993955 -149.42286733384117, 181.26025640322237 -161.76467103358485, 218.26028432194533 -199.40090684602083 M159.5823664726304 -133.16531102090457 C175.20312935044444 -152.4759111922705, 191.60553376796034 -170.18483778246411, 218.20243548764137 -201.3592327703013 M163.4974980522437 -133.03251283399487 C176.6293076790426 -147.61919556512447, 186.66443240226297 -158.64448747771917, 217.96775175760558 -195.84622610158934 M163.34845752596834 -133.9234853519865 C176.31461962136476 -147.88819697482037, 190.80910239980383 -163.09354101987964, 216.87216905983496 -195.86796812813444 M169.80469137722426 -131.69308471896503 C184.55700767155818 -149.64257572998503, 196.7579526802989 -166.1503888655037, 219.49175083917402 -189.49829321701375 M169.46196500052278 -132.98256362175383 C181.72493347369368 -145.57962995541183, 191.03528876330776 -157.88181477908816, 218.2645919922151 -189.43423184847026 M173.50985112761762 -132.3115119510932 C186.61088054421242 -147.46308286479137, 198.76513430416713 -158.60042694560448, 219.5908122267132 -182.84117464729337 M175.3405482424742 -132.20395419781306 C184.1615039704398 -145.4175078955654, 195.2745719343216 -157.37826664711952, 217.45742333631475 -182.0738288913805 M179.5002131466147 -135.37395835239084 C189.16883608673515 -142.4436897035779, 200.19078827376057 -154.73921754337567, 219.7312910205863 -176.99924169633093 M180.48440756668788 -134.12461256750518 C189.67802799153733 -144.71872514794003, 199.36356425452155 -155.9824058717675, 218.3799296934175 -177.6758774350737 M184.24269491868395 -134.50886495701198 C197.05448706184194 -145.98935756680874, 206.80181673290363 -159.8347584177148, 218.82802558827194 -172.37736169073528 M184.83162513440058 -132.90457764906455 C196.58722180881523 -146.92106566862338, 209.6121284827221 -162.07894978228197, 217.46231940662489 -171.30400286242718 M188.92873975231007 -133.0549597330022 C198.80119285240042 -140.67333514363617, 205.9182118068415 -151.37824740484456, 219.03004184782387 -166.21005757198088 M191.56250398266445 -133.8054348303661 C199.68372407637312 -145.20927031426518, 209.56775906055685 -156.25084048436926, 218.006127251368 -165.25428488175595 M195.19996270371186 -134.31895531780378 C204.24756291278692 -139.81796782482792, 210.77784423690073 -148.15420934234123, 218.14425757861022 -159.49699327708564 M195.04392668916148 -132.93791177388655 C203.71816753653866 -143.5453511893584, 214.38728662304578 -153.92459951408094, 217.88814587154786 -160.34381395884003 M202.07226562482214 -135.0252637964262 C204.79569963323232 -136.56376524649238, 208.81510611624708 -140.82622090320947, 219.66326033979158 -152.2676269942624 M200.86621035527926 -134.4743837848136 C206.31885768523327 -140.88976764332247, 212.8530987314364 -145.49778914879118, 217.60073611693704 -152.4898250087404 M208.4329954936581 -134.65679768569763 C208.95628680016122 -135.87418437354495, 210.9117686624737 -140.48639045328508, 217.9587264237417 -144.7561604331344 M207.62264837173282 -133.5806503908163 C209.0040867291786 -136.62690751969305, 212.39821269455618 -139.86536628888229, 217.5694973494737 -145.74636608068766"
            stroke="#3498db"
            stroke-width="0.5"
            fill="none"
            id="path4322"
            class="svg-elem-3"
          ></path>
          <path
            d="M113.61 -134.69 C111.68585450252179 -135.8794353806969, 204.49689044112327 -134.30686679039943, 205.3358724921625 -136.66870097652256 M113.55341795920049 -133.71634842189195 C113.76764436850034 -136.8930001808278, 206.26154933364904 -135.59383617269683, 203.5765924646661 -135.0444891635347 M205.61 -134.69 C211.19355980350653 -134.22065485189063, 217.268486160363 -138.7806634067684, 215.9903071708465 -145.08222588576348 M203.80715672085518 -136.00162984178354 C210.8661090734963 -132.47605398463799, 217.71925807781616 -142.65186613900752, 216.66599488483033 -146.0507139184003 M217.61 -146.69 C218.70229778652222 -147.61288577378247, 219.38815649060598 -198.48448987539646, 218.8086533858803 -196.6595810952635 M216.9856942243873 -147.53473211175879 C217.83291303943054 -147.4937824979084, 216.70853969107097 -199.9709722938268, 215.3332884526033 -199.87593435057101 M217.61 -197.69 C218.38656951900205 -205.5414500395729, 210.1799880649951 -210.17152337067702, 205.62362695548316 -210.18160581575725 M216.65429723230673 -198.31645413712556 C215.90651468475667 -204.5919585262637, 212.92464297532095 -211.50598345757672, 204.16472982577181 -210.08642234860486 M205.61 -209.69 C204.7038111116854 -207.8547775871947, 114.43966710333373 -210.34808673659361, 113.70560696379364 -208.04880686720568 M205.3183213584119 -209.9303973188956 C205.56077537230726 -207.39789402755093, 113.98986352801677 -210.81925150603462, 115.14576319303447 -208.02391089677883 M113.61 -209.69 C109.48584928900188 -211.01458525417624, 102.36941915005522 -202.49798895673044, 101.09679425407106 -196.91426524824126 M114.92163486677063 -211.34531395056035 C108.34855703998866 -211.56745555867312, 102.65796286656675 -203.71176461302107, 100.30585027204867 -196.30023501822498 M101.61 -197.69 C102.10075982549847 -197.26435127890917, 101.73237239537168 -146.38575521430243, 101.5044286064184 -148.35794582695112 M103.0413134238393 -199.54603749411103 C100.11428006715933 -199.9830272230545, 100.03300256287099 -148.80797146560897, 103.65735401099094 -146.46810427039745 M101.61 -146.69 C101.41587028745647 -142.5746960273378, 108.01491863544112 -132.8683831527128, 113.85577077786239 -134.68951933769404 M100.8066868078581 -147.78160399040638 C101.664187285823 -139.1497619963417, 106.34427102551331 -136.67209109833638, 114.51198966638499 -135.57494844763966"
            stroke="#3498db"
            stroke-width="1"
            fill="none"
            id="path4324"
            class="svg-elem-4"
          ></path>
        </g>
        <g
          aria-label="PettingZoo"
          id="text4328"
          style="
            font-size: 14px;
            font-family: Tinos, serif;
            text-anchor: middle;
          "
        >
          <path
            d="m 131.39809,-198.08571 v 3.04883 l 1.45605,0.18457 v 0.3623 h -3.8623 v -0.3623 l 1.08691,-0.18457 v -8.08008 l -1.17578,-0.17773 v -0.36231 h 3.45898 q 3.36328,0 3.36328,2.7002 0,1.4082 -0.85449,2.13965 -0.84765,0.73144 -2.44043,0.73144 z m 2.96679,-2.85742 q 0,-1.12793 -0.52636,-1.61328 -0.52637,-0.48535 -1.77051,-0.48535 h -0.66992 v 4.34082 h 0.71093 q 1.15528,0 1.70215,-0.52637 0.55371,-0.52637 0.55371,-1.71582 z"
            id="path4542"
            class="svg-elem-5"
          ></path>
          <path
            d="m 138.06313,-197.7234 v 0.12304 q 0,0.94336 0.20507,1.46973 0.21192,0.51953 0.64258,0.79297 0.4375,0.27344 1.1416,0.27344 0.36914,0 0.875,-0.0615 0.50586,-0.0615 0.83399,-0.13672 v 0.38282 q -0.32813,0.21191 -0.89551,0.36914 -0.56055,0.15722 -1.14844,0.15722 -1.49707,0 -2.19433,-0.80664 -0.69043,-0.80664 -0.69043,-2.59082 0,-1.68164 0.7041,-2.50879 0.7041,-0.82715 2.00976,-0.82715 2.46778,0 2.46778,2.80274 v 0.56055 z m 1.48339,-2.81641 q -0.71093,0 -1.09375,0.57422 -0.37597,0.57422 -0.37597,1.69531 h 2.74804 q 0,-1.22363 -0.31445,-1.74316 -0.31445,-0.52637 -0.96387,-0.52637 z"
            id="path4544"
            class="svg-elem-6"
          ></path>
          <path
            d="m 144.78285,-194.35329 q -0.65625,0 -0.98437,-0.38965 -0.32129,-0.38964 -0.32129,-1.09375 v -4.50488 h -0.84082 v -0.30762 l 0.85449,-0.2666 0.69043,-1.45605 h 0.43066 v 1.45605 h 1.46973 v 0.57422 h -1.46973 v 4.38184 q 0,0.44433 0.19825,0.66992 0.20507,0.22559 0.5332,0.22559 0.39648,0 0.96387,-0.10938 v 0.44434 q -0.23926,0.16406 -0.69043,0.2666 -0.45118,0.10937 -0.83399,0.10937 z"
            id="path4546"
            class="svg-elem-7"
          ></path>
          <path
            d="m 148.6725,-194.35329 q -0.65625,0 -0.98437,-0.38965 -0.32129,-0.38964 -0.32129,-1.09375 v -4.50488 h -0.84082 v -0.30762 l 0.85449,-0.2666 0.69043,-1.45605 h 0.43066 v 1.45605 h 1.46973 v 0.57422 h -1.46973 v 4.38184 q 0,0.44433 0.19824,0.66992 0.20508,0.22559 0.53321,0.22559 0.39648,0 0.96386,-0.10938 v 0.44434 q -0.23925,0.16406 -0.69043,0.2666 -0.45117,0.10937 -0.83398,0.10937 z"
            id="path4548"
            class="svg-elem-8"
          ></path>
          <path
            d="m 152.80141,-194.96852 1.10058,0.1709 v 0.30761 h -3.3291 v -0.30761 l 1.09375,-0.1709 v -5.46875 l -0.90918,-0.1709 v -0.30762 h 2.04395 z m 0.0684,-8.0459 q 0,0.30078 -0.21875,0.51953 -0.21875,0.21875 -0.52637,0.21875 -0.30078,0 -0.51953,-0.21875 -0.21875,-0.21875 -0.21875,-0.51953 0,-0.30762 0.21875,-0.52637 0.21875,-0.21875 0.51953,-0.21875 0.30762,0 0.52637,0.21875 0.21875,0.21875 0.21875,0.52637 z"
            id="path4550"
            class="svg-elem-9"
          ></path>
          <path
            d="m 156.38344,-200.39626 q 0.52637,-0.30078 1.12109,-0.49218 0.59473,-0.19825 0.99121,-0.19825 0.83399,0 1.25782,0.48536 0.42382,0.48535 0.42382,1.4082 v 4.22461 l 0.7793,0.1709 v 0.30761 h -2.76855 v -0.30761 l 0.85449,-0.1709 v -4.10156 q 0,-0.56739 -0.28028,-0.88868 -0.27343,-0.32812 -0.85449,-0.32812 -0.61523,0 -1.51074,0.19824 v 5.12012 l 0.86816,0.1709 v 0.30761 h -2.77539 v -0.30761 l 0.77246,-0.1709 v -5.46875 l -0.77246,-0.1709 v -0.30762 h 1.83203 z"
            id="path4552"
            class="svg-elem-10"
          ></path>
          <path
            d="m 167.11586,-198.88551 q 0,1.10742 -0.66309,1.6748 -0.66308,0.56738 -1.90722,0.56738 -0.56055,0 -1.03907,-0.10253 l -0.43066,0.8955 q 0.0205,0.11621 0.2666,0.21875 0.2461,0.10254 0.61524,0.10254 h 1.90039 q 1.03906,0 1.53808,0.45117 0.50586,0.45118 0.50586,1.24414 0,0.71778 -0.40332,1.25098 -0.39648,0.5332 -1.16894,0.82031 -0.77246,0.29395 -1.87305,0.29395 -1.3125,0 -2.00293,-0.40332 -0.68359,-0.40332 -0.68359,-1.14844 0,-0.3623 0.24609,-0.71777 0.24609,-0.34864 0.90234,-0.82031 -0.38964,-0.12989 -0.65625,-0.44434 -0.2666,-0.31445 -0.2666,-0.67676 l 1.08008,-1.2168 q -1.08008,-0.50585 -1.08008,-1.98925 0,-1.05274 0.66309,-1.62696 0.66992,-0.57422 1.9414,-0.57422 0.25293,0 0.64942,0.0547 0.39648,0.0479 0.6084,0.11621 l 1.51074,-0.75879 0.23926,0.29395 -0.9502,0.98437 q 0.45801,0.5127 0.45801,1.51075 z m -0.28027,5.26367 q 0,-0.38965 -0.23926,-0.6084 -0.23926,-0.21875 -0.72461,-0.21875 h -2.48828 q -0.28711,0.24609 -0.47168,0.62207 -0.17774,0.38281 -0.17774,0.71094 0,0.58789 0.42383,0.84082 0.42383,0.25976 1.29883,0.25976 1.1416,0 1.75684,-0.42382 0.62207,-0.42383 0.62207,-1.18262 z m -2.27637,-3.54102 q 0.74512,0 1.05273,-0.42383 0.31446,-0.43066 0.31446,-1.29882 0,-0.90918 -0.32129,-1.292 -0.32129,-0.38964 -1.03223,-0.38964 -0.71777,0 -1.05273,0.38964 -0.33496,0.38965 -0.33496,1.292 0,0.90234 0.32812,1.3125 0.32813,0.41015 1.0459,0.41015 z"
            id="path4554"
            class="svg-elem-11"
          ></path>
          <path
            d="m 168.83852,-195.13258 5.14062,-7.93653 h -1.70898 q -1.68848,0 -2.32422,0.13672 l -0.21192,1.44238 h -0.47168 v -2.16699 h 6.24122 v 0.58789 l -5.17481,8.00489 h 1.98242 q 0.79297,0 1.60645,-0.0752 0.82031,-0.0752 1.15527,-0.15039 l 0.40332,-1.75 h 0.47852 l -0.18457,2.5498 h -6.93164 z"
            id="path4556"
            class="svg-elem-12"
          ></path>
          <path
            d="m 183.18715,-197.73708 q 0,3.38379 -3.00781,3.38379 -1.44922,0 -2.1875,-0.86816 -0.73828,-0.86816 -0.73828,-2.51563 0,-1.62695 0.73828,-2.48828 0.73828,-0.86133 2.24218,-0.86133 1.46289,0 2.20801,0.84766 0.74512,0.84082 0.74512,2.50195 z m -1.23047,0 q 0,-1.47656 -0.43066,-2.13964 -0.43067,-0.66309 -1.34668,-0.66309 -0.89551,0 -1.29883,0.63574 -0.39649,0.63574 -0.39649,2.16699 0,1.55176 0.40332,2.20118 0.41016,0.64257 1.292,0.64257 0.90234,0 1.33984,-0.66992 0.4375,-0.66992 0.4375,-2.17383 z"
            id="path4558"
            class="svg-elem-13"
          ></path>
          <path
            d="m 190.18715,-197.73708 q 0,3.38379 -3.00781,3.38379 -1.44922,0 -2.1875,-0.86816 -0.73828,-0.86816 -0.73828,-2.51563 0,-1.62695 0.73828,-2.48828 0.73828,-0.86133 2.24218,-0.86133 1.46289,0 2.20801,0.84766 0.74512,0.84082 0.74512,2.50195 z m -1.23047,0 q 0,-1.47656 -0.43066,-2.13964 -0.43067,-0.66309 -1.34668,-0.66309 -0.89551,0 -1.29883,0.63574 -0.39649,0.63574 -0.39649,2.16699 0,1.55176 0.40332,2.20118 0.41016,0.64257 1.292,0.64257 0.90234,0 1.33984,-0.66992 0.4375,-0.66992 0.4375,-2.17383 z"
            id="path4560"
            class="svg-elem-14"
          ></path>
        </g>
      </g>
      <g id="clust3" class="cluster">
        <title id="title4331">cluster_crewai</title>
        <g fill-opacity="0.250980" stroke-opacity="0.250980" id="g4337">
          <path
            d="M192.54606243164812 -117.50005507942754 C192.54606243164812 -117.50005507942754, 192.54606243164812 -117.50005507942754, 192.54606243164812 -117.50005507942754 M192.54606243164812 -117.50005507942754 C192.54606243164812 -117.50005507942754, 192.54606243164812 -117.50005507942754, 192.54606243164812 -117.50005507942754 M190.0633087048493 -108.84628686965237 C194.01206223305525 -112.90488229470553, 195.91676901370835 -113.6745675911107, 199.62938215134855 -121.97321733051173 M189.75932459034115 -108.446445445666 C193.90516679037583 -113.26117058100424, 197.86416872790963 -117.7313842164957, 200.66840225857555 -120.13694718494135 M191.01395376416446 -100.34925409663677 C191.98181382816574 -108.4756926590594, 197.91550765604913 -114.27567425457032, 205.82354400782782 -122.34890111499311 M188.96019243224828 -101.55300143917296 C195.10401840198597 -108.78731805900983, 200.20709057053128 -112.90228338596636, 205.94292308388592 -120.19520607975042 M188.4804889349207 -95.102602111619 C195.96266027290994 -101.97059595238102, 204.69018152522088 -110.15431765346433, 209.96754045354484 -121.22207361326002 M189.47962511500793 -95.21195477268022 C194.5790379377791 -102.50695036675013, 201.75213138046945 -110.10592628925424, 212.2086261054279 -121.43438470312505 M188.0634919752116 -90.10088438262422 C194.24337074786763 -95.27867564306193, 203.90810603083713 -106.00850276983756, 216.6204759267846 -121.63319949937056 M190.407095837699 -90.08967324471338 C196.94899523883177 -98.6248932722784, 205.81219384998084 -108.74178180424741, 216.62800342928426 -119.84936861684182 M189.79210190971892 -83.93640195178911 C198.8124676822005 -93.4400018178965, 208.07031159196103 -101.98544548918011, 222.58903115878917 -119.54810442017708 M188.9925522951901 -84.77600694689086 C199.3388761709958 -94.45238483427211, 209.8538997587752 -107.26514972184242, 222.23348389136544 -120.72643938785882 M190.5317799145713 -76.9923737630669 C197.2107603009387 -86.18017462841415, 206.57089747725277 -96.4933865756135, 228.22341331867034 -119.28176651709474 M188.9900557823332 -78.48048485034903 C199.9517803455072 -89.74638147552011, 210.4365831709624 -100.4255189110127, 226.24985132416205 -121.25737273251254 M189.94582380126715 -71.81376608568732 C204.47903926276592 -88.82398008176645, 216.80834900707492 -104.56303431486947, 232.61204499577747 -119.94476935361251 M188.6092052660114 -71.5852671761957 C202.1660576732108 -83.83374204727357, 213.0963006458798 -98.81897080119589, 232.416501435723 -120.84174800164547 M189.65203614251223 -65.45348648013793 C203.0108910859888 -82.41975228874338, 215.30917140011792 -98.56410757800971, 239.52951689576275 -120.95876517163947 M189.894490374607 -66.06861874611644 C205.78134157399103 -83.1565439703082, 218.95801827304425 -98.9070123621938, 237.5179553077022 -120.95961284400087 M189.82713275487018 -60.79221922500988 C207.6055602232564 -80.55184456621822, 230.3125239532023 -103.07782589925388, 241.66702452734685 -121.64927042252725 M190.42216798745224 -59.92398095018275 C204.4006206681191 -75.17251261065466, 217.525017963553 -90.89607951450937, 244.06365135414035 -120.12763456048613 M191.54760691194994 -52.43731320601668 C205.7119937078348 -69.43059800031745, 218.93254173168555 -85.94853053769164, 248.7110643642583 -120.31766750771654 M190.10241210197384 -53.25345985819356 C210.78998948267457 -76.6993373800375, 231.28211065754155 -100.9330383443342, 248.7561952595209 -120.70390577176401 M190.63745820678696 -46.79310405831619 C205.78176584784228 -65.74112085920343, 223.472472451567 -86.00132464727481, 254.73640673438328 -122.03537905032509 M188.77030297071036 -46.37212618202279 C212.1065492150093 -71.05278640183158, 232.50412553534392 -96.4468558191986, 253.52936770834236 -120.66016800305968 M190.68025698618993 -42.19092599010776 C214.94979646684246 -72.60637353114373, 244.77181743942685 -102.97498664645875, 258.01238600491644 -121.68636748296636 M188.6897436165216 -39.73849751380312 C205.88305618184145 -56.84067716993181, 220.01758978514496 -74.79168626691197, 258.08891316353777 -120.40984973990804 M188.5317234135558 -33.57767582199101 C204.3452260672116 -51.937858103986926, 218.8577805490803 -69.01489613251732, 264.7089482071142 -120.97449428556355 M190.37546320276863 -35.95750906645347 C207.03092686089124 -54.74840711101872, 225.10265904412032 -74.34060553031924, 264.09649393258434 -120.73912972847009 M190.18550179218462 -26.828118780727923 C213.95825083730227 -60.53299705963801, 242.25324994957253 -89.02790486681809, 268.2420014212547 -122.44081467007145 M189.68585844692697 -29.35577524834936 C212.49577127370304 -53.88119267411463, 235.33762268645037 -81.01268881674586, 269.0618503233798 -120.49205404336847 M190.5216552984139 -24.788963562049002 C213.0361082170824 -50.39252650428831, 237.22320840425326 -73.59497822765829, 273.5356050264322 -119.26759500090478 M189.39725878528694 -22.766524688606548 C215.68288449562243 -51.85913577068389, 240.41846474671806 -80.36176899506148, 275.49080670905045 -121.59010612976753 M191.67244438999808 -14.954582189140694 C209.406624668278 -39.98113129412009, 230.28351122596524 -64.69542420387249, 281.80485138204176 -121.03561134514334 M189.1867530065568 -16.680724268628065 C222.67812669101508 -55.86096474834485, 256.12729268035565 -96.18490670870517, 280.28820497033036 -121.46256436648363 M188.20355846737226 -10.647877214345332 C208.62506314683412 -33.80070024734685, 227.57785858328748 -55.0663978198638, 285.3661102526497 -119.26862813500193 M189.1237097343756 -10.505178885722326 C227.54572101060745 -53.633458820310445, 265.0829227812532 -96.43064690282016, 284.9678469269413 -120.8791239474431 M191.3949721851071 -6.1316300622896645 C221.90925058798172 -39.28422903994556, 252.90749328819606 -75.90720142722834, 289.15252990323216 -119.03933602095731 M191.45789311174926 -7.718520162633546 C222.49188203953045 -42.77701448620299, 253.51011089786607 -77.39424758565934, 291.35507789277443 -121.18693652738962 M193.55193301375937 -3.164525423511578 C233.76154320564905 -47.20356753201165, 271.5614377695296 -94.88810437895201, 295.38500839441724 -120.35323375410316 M193.05385320307164 -2.4146664665216555 C223.87091841424945 -36.491939265720795, 253.47054593993101 -72.33693957844659, 295.7756745347888 -119.70179704105578 M195.33493481405173 0.28648270624767225 C234.7901287390289 -47.43257887778225, 273.92365328941446 -89.9789327453858, 302.355521240205 -119.40674857724781 M196.25232981111785 -0.755559535945725 C221.252134967884 -27.767956128325615, 245.36086598040237 -55.807741806947845, 300.88931305454565 -119.95240079839971 M201.83545615610785 1.0938314405151406 C224.87432382669198 -23.79101065894197, 244.01683322183166 -50.24082898100013, 306.4319013745721 -119.26801837510338 M201.497867894419 -0.22590880823563886 C239.9151260819706 -43.44502674802206, 278.68187541227985 -86.88615596897382, 306.5549648807002 -120.37474676269713 M207.27428617393946 -0.2986454179856155 C244.55843117137488 -41.00753194682205, 281.4287761137475 -84.35180630984206, 312.5801677669101 -122.28674024032415 M207.26533064759258 1.3487527146488483 C244.21301128459913 -42.449824596825636, 282.6659957487234 -86.93162014970345, 311.79980860652546 -120.82538218807808 M212.45114250415443 -1.2108969304462578 C239.28281905317922 -32.23589953152364, 268.0535654242259 -66.16107194935142, 316.0738841256324 -118.95265080043109 M213.0454848878201 0.03203753614846283 C252.1954584968129 -46.51329893013752, 293.4113054034003 -94.28784081012927, 316.3401467104625 -120.45600378350842 M217.13602783558926 0.6687753955599955 C247.1239518152152 -36.35317990352947, 280.33519580692484 -70.90433449211791, 323.1420927767111 -119.93569000215746 M217.12055520480902 -0.2918757328711563 C257.8565037910638 -44.215923916348714, 295.7553842882784 -88.5079291308044, 322.5814195825033 -121.89123540446487 M221.73443596595226 1.1894623287832422 C245.0574275600974 -28.919670380774022, 273.8681578873369 -54.85501821003082, 329.557632135942 -122.52652559978732 M222.2341654358359 1.0862188340192271 C252.181318310016 -32.29715273218665, 280.24031230325795 -65.37090109655367, 327.0767235000448 -119.83987093992369 M227.22953148168102 2.2499745931269723 C254.5549784848245 -28.38437933657704, 277.0065412129691 -59.94470108479949, 331.1608099880272 -118.71443527868155 M227.45053842121825 0.08675325467299366 C252.0801974822761 -26.46660258377232, 274.3458481342123 -52.14352327733845, 332.36123418448005 -120.16890624340736 M233.65572483620934 -0.6396081135285865 C257.1623931934914 -27.521943783194253, 284.1179391598846 -59.770538267406565, 336.940032507867 -119.21689090175154 M233.39374613156198 0.5040991373752317 C267.39282947294055 -38.11540700622327, 300.7271768255642 -76.66995017373672, 335.56793325659504 -117.57430653000853 M239.0132566850105 -0.579485939441426 C271.71322496407055 -37.47358941481867, 303.2660328286036 -76.61375697562107, 338.42950321838765 -117.21302281780217 M239.06801474525332 0.23555065702065558 C271.5533349051351 -37.25470406497407, 304.7205591947287 -76.57044447174378, 340.85979265916654 -115.89391401138802 M241.5666096426155 1.531141027468938 C271.49949733861587 -33.58073947135946, 300.20989576542837 -63.86762101607852, 343.22362994469046 -111.59083245410264 M242.36061312546903 1.3522846943577425 C269.73645112779747 -26.580911160006142, 293.60605271358946 -55.77370514434261, 341.8727533994196 -112.73555653423794 M248.21374057910018 1.390048211600682 C280.3783443091708 -33.26144427165442, 305.68091524176134 -66.16733065704562, 343.24405707516866 -107.40270886251555 M249.847348602932 1.3886239471196564 C276.5364058927355 -30.265704820146752, 303.008288536509 -59.89022308225274, 343.69345748154257 -108.61168740461281 M252.4723465407602 2.1906208629406594 C287.4827711535756 -37.77447876834429, 321.9092436851605 -77.61417180875145, 345.0528301693983 -100.82987215213605 M253.49381893632608 0.21087804635576468 C282.9031044870616 -30.19331990893587, 309.4436769793533 -61.74294028424242, 342.8771053266742 -102.45951052450987 M259.4989944276694 2.1809071217437017 C276.2832371784032 -20.021734666852677, 298.2767044586627 -42.595221697282945, 345.1882230800305 -96.27914414620024 M260.35232775596427 -0.09765328662128248 C284.8082586105635 -27.115094405839372, 308.6174625536902 -54.03398006427737, 343.2059219835496 -96.26532195440957 M264.403265522376 1.3133777391759098 C291.7666771542971 -31.087482308756904, 318.4366777068185 -62.636399095659314, 345.38781290506967 -89.8765456302245 M263.76658323206584 0.22015810304505656 C296.0986090271369 -35.16412824189121, 325.89258782955443 -70.7482046978623, 344.1390238242661 -90.44372004091835 M270.52409938565637 -0.6052157940524223 C298.51097679846487 -29.7972444615779, 325.96491653234983 -62.294509345895136, 344.23098393681505 -85.75880729333367 M270.2423965396432 -0.501270023832606 C288.5963642890403 -22.68616839221707, 308.58433231738064 -44.90206160629806, 344.087175551836 -84.18562154488086 M274.7730238725896 0.8532783497696244 C300.3770162492344 -32.00208774648286, 328.30050730627437 -59.635694086647355, 342.5373609445514 -77.41187249489619 M275.0713589164768 1.737044885972458 C296.41924759638124 -22.85494724655993, 316.9813851368113 -48.0663379386573, 345.06901018583426 -78.80269403285264 M281.0170415166235 -1.4828919647956207 C298.1158804516563 -17.546455581832443, 312.55424446195025 -39.082076817774805, 345.53523294286816 -74.0369328371768 M280.816529292962 -0.17678605313116336 C296.91276028438307 -16.72768985760257, 313.83541534112766 -36.391535321463735, 344.7764803578385 -71.61483810599273 M286.0054291223237 -0.3366369133543321 C301.1121478998037 -18.030485026007998, 318.2669716229827 -36.49940409006927, 341.9195444769657 -66.24344930981427 M285.48794998435886 0.28328668618995545 C307.93684027381147 -24.32304145523641, 331.2034240337831 -49.73786860795713, 344.2528870038637 -65.98165182412043 M289.8689253339483 0.14256660468633253 C309.924274087008 -20.09164524717218, 328.45260291301054 -41.47900920963491, 342.8250634957215 -59.430246002500105 M291.14600012693916 0.6831454612232322 C307.8224444950198 -19.076050294358723, 325.8366454328424 -38.549020040917476, 344.89418385646036 -60.59222056493142 M295.84519947821747 2.554653307263293 C310.40913537003456 -16.76294334459867, 327.77325066264274 -34.07049031904082, 341.7446316411648 -53.93422460547625 M296.3374388381164 0.5208335116917846 C311.91024305300306 -16.724783963947004, 325.11681816794646 -33.910322261466504, 344.3701808348822 -52.81713674891126 M300.8287557726714 -1.3901832459214694 C320.46459181597265 -20.187544316311456, 334.9604692193935 -39.07239496742426, 344.3369157502047 -47.079850043934634 M301.37737034692304 -0.24007584631143164 C315.8543791229702 -14.830566870129163, 329.36926579999744 -30.78817743715824, 343.1406174072215 -47.87596485988543 M307.4196838349359 -1.1287298399942927 C316.9714062752083 -12.163026314261554, 325.84716550277534 -21.82396388704708, 342.41992558810756 -41.97753799926078 M307.66933334307635 0.16191514085740222 C320.5418119574319 -15.404858757627906, 333.8207980611738 -28.911965479327847, 343.85803456558403 -40.889038397750646 M310.97514245394467 -1.0182203550241216 C321.8829906540293 -11.278103572086406, 332.9783561107014 -23.68875809623623, 342.20234772493535 -35.23162703485502 M312.26516987690434 -0.4162004710959182 C322.33204431853306 -8.95929502545107, 330.150462303036 -18.51954648494361, 342.92484633606205 -35.73979899034834 M317.64399845261386 -0.629036192167832 C322.7039038221015 -8.250994794256066, 331.27985513941024 -13.533671798395494, 343.7505645120593 -28.250111365131506 M317.007292181328 1.5693417046272824 C328.23184726060174 -11.162016534037406, 338.7194560888021 -21.784049359409607, 343.7367564073659 -29.892258452245997 M322.8603724698026 0.5375360404218332 C330.73023030853875 -7.48957145642164, 336.220878405126 -15.35793068233962, 344.71794001509517 -23.973998320987327 M324.15014681538327 1.1201935940500456 C330.08311553460294 -9.026675068945199, 337.96905381120575 -16.864355809963453, 343.22311847070387 -22.432181668921977 M328.54458805996626 2.551180717315427 C330.73641033731536 -2.8790372275142975, 336.6688076370574 -10.273960873303988, 345.96862395875246 -17.447938586040724 M329.3926536993883 -0.2919279082188222 C331.07162951173456 -2.874181040324729, 334.87638044672946 -6.2097544901355075, 345.03305017302034 -17.730088657412747 M334.72149296694 1.0198523151134096 C336.89542601479934 -4.54871494862299, 340.9155325596666 -7.787022883077884, 342.87592210390284 -12.288548421036872 M332.9895721845175 0.7365297199894447 C336.55126643487824 -3.626727669594361, 340.4062682597149 -6.210074745168761, 343.5840354897252 -11.687812721482747"
            stroke="#e74c3c"
            stroke-width="0.5"
            fill="none"
            id="path4333"
            class="svg-elem-15"
          ></path>
          <path
            d="M200.57 0.01 C201.11796788353325 -1.7688154858037082, 332.93164687960564 0.5163149806065219, 331.3921296062554 -1.3817770963668063 M201.45071146444343 0.6192632986020057 C202.8540958438336 -1.7077209547926568, 330.0792259832093 2.035317425878775, 329.3983213208594 2.2373443246439884 M331.57 0.01 C336.2238518941601 -0.07320271416832093, 344.6768280146144 -7.1985840425253675, 345.42748299094086 -13.716392224741558 M332.8397401739705 -1.0387447399296128 C338.2945374337723 0.6216278759821459, 342.8132755374959 -7.6203488509974395, 342.96513106746033 -9.97237194522952 M343.57 -11.99 C341.87943574886265 -10.329343282497923, 344.6795973225756 -108.59895838532216, 344.2035047933819 -109.11570525290274 M341.84439799819614 -12.296501438990937 C341.5708505812555 -9.942510961442409, 343.5950203523432 -110.60577144212178, 345.07313994071745 -108.96350188168185 M343.57 -108.99 C342.9048521662573 -114.64909122041698, 337.48087805285473 -119.96589150431912, 331.399142485517 -122.36760092910467 M341.9699365015916 -109.04594652057872 C345.71674918028583 -116.86426138141104, 337.4055518217665 -121.8819716539143, 330.4226711559128 -120.9203235239701 M331.57 -120.99 C333.13972309288874 -122.74238145409097, 199.90102881629957 -121.56653188346468, 199.96442032898074 -121.72052774674432 M331.5224852982725 -119.92877129998399 C333.44761490643026 -121.3255297625229, 198.4507593073826 -119.29966819170073, 198.90059883160725 -119.09103793522624 M200.57 -120.99 C193.6862688459263 -122.1179099652222, 187.94793977663892 -114.00623448527026, 186.98948070893704 -110.28774908678429 M198.7736313634458 -122.6156162448847 C195.22821311660277 -118.88634379565336, 187.9975192845635 -115.57106390948371, 190.22431921177173 -110.31123230014913 M188.57 -108.99 C186.7105805030969 -110.71188853333085, 189.57694935258087 -12.531146015974098, 189.5013609675813 -13.528312446800452 M186.647729511699 -107.21732226393436 C189.02059284729413 -110.54387758046455, 188.0451460289861 -12.020108290390855, 187.88205080686583 -13.96948652200956 M188.57 -11.99 C186.6526282047379 -4.521527277916559, 192.9835421566145 -0.7410440193397496, 201.50481714893564 -0.5954803790126773 M189.89661938945883 -10.332417029458965 C187.85039212796488 -5.339753821238855, 196.32597046995608 0.9047464453027689, 200.06985993294188 1.2937397953541143"
            stroke="#e74c3c"
            stroke-width="1"
            fill="none"
            id="path4335"
            class="svg-elem-16"
          ></path>
        </g>
        <g
          aria-label="CrewAI"
          id="text4339"
          style="
            font-size: 14px;
            font-family: Tinos, serif;
            text-anchor: middle;
          "
        >
          <path
            d="m 248.81268,-105.65328 q -2.22851,0 -3.47265,-1.20996 -1.24414,-1.2168 -1.24414,-3.4043 0,-2.36523 1.19629,-3.5752 1.19628,-1.21679 3.54785,-1.21679 1.42871,0 3.06933,0.34863 l 0.041,2.00293 h -0.45117 l -0.20508,-1.18945 q -0.47852,-0.29395 -1.11426,-0.45117 -0.62891,-0.16407 -1.28516,-0.16407 -1.75683,0 -2.56347,1.03223 -0.80664,1.03223 -0.80664,3.19922 0,1.99609 0.84082,3.04883 0.84765,1.05273 2.46093,1.05273 0.7793,0 1.46973,-0.18457 0.69043,-0.19141 1.09375,-0.50586 l 0.25293,-1.36719 h 0.44434 l -0.041,2.15332 q -1.5039,0.43067 -3.2334,0.43067 z"
            id="path4563"
            class="svg-elem-17"
          ></path>
          <path
            d="m 257.39862,-112.38668 v 1.73633 h -0.29394 l -0.39649,-0.75196 q -0.3418,0 -0.81348,0.0957 -0.46484,0.0889 -0.80664,0.23926 v 4.79882 l 1.10059,0.1709 v 0.30762 h -3.04883 v -0.30762 l 0.81348,-0.1709 v -5.46875 l -0.81348,-0.17089 v -0.30762 h 1.87305 l 0.0615,0.7998 q 0.41016,-0.34179 1.10742,-0.65625 0.70411,-0.31445 1.11426,-0.31445 z"
            id="path4565"
            class="svg-elem-18"
          ></path>
          <path
            d="m 259.29901,-109.0234 v 0.12305 q 0,0.94336 0.20508,1.46972 0.21191,0.51954 0.64258,0.79297 0.4375,0.27344 1.1416,0.27344 0.36914,0 0.875,-0.0615 0.50586,-0.0615 0.83398,-0.13672 v 0.38281 q -0.32812,0.21191 -0.8955,0.36914 -0.56055,0.15723 -1.14844,0.15723 -1.49707,0 -2.19434,-0.80664 -0.69043,-0.80664 -0.69043,-2.59082 0,-1.68164 0.7041,-2.50879 0.70411,-0.82715 2.00977,-0.82715 2.46777,0 2.46777,2.80273 v 0.56055 z m 1.4834,-2.81641 q -0.71094,0 -1.09375,0.57422 -0.37598,0.57422 -0.37598,1.69532 h 2.74805 q 0,-1.22364 -0.31445,-1.74317 -0.31446,-0.52637 -0.96387,-0.52637 z"
            id="path4567"
            class="svg-elem-19"
          ></path>
          <path
            d="m 270.9201,-105.65328 h -0.5332 l -1.58594,-4.23828 -1.56543,4.23828 h -0.50585 l -2.22168,-6.08399 -0.75879,-0.17089 v -0.30762 h 3.05566 v 0.30762 l -1.06641,0.18457 1.52442,4.34082 1.55176,-4.19043 h 0.57421 l 1.54493,4.21777 1.45605,-4.38184 -1.05273,-0.17089 v -0.30762 h 2.44726 v 0.30762 l -0.71093,0.14355 z"
            id="path4569"
            class="svg-elem-20"
          ></path>
          <path
            d="m 276.99725,-106.15231 v 0.36231 h -3.01465 v -0.36231 l 1.03907,-0.18457 3.12402,-8.69531 h 1.29883 l 3.24707,8.69531 1.16211,0.18457 v 0.36231 h -3.87598 v -0.36231 l 1.23047,-0.18457 -0.90918,-2.6455 h -3.60937 l -0.92286,2.6455 z m 1.46973,-7.8955 -1.57227,4.45019 h 3.19239 z"
            id="path4571"
            class="svg-elem-21"
          ></path>
          <path
            d="m 286.95038,-106.33688 1.17578,0.18457 v 0.36231 h -3.66406 v -0.36231 l 1.17578,-0.18457 v -8.08007 l -1.17578,-0.17774 v -0.3623 h 3.66406 v 0.3623 l -1.17578,0.17774 z"
            id="path4573"
            class="svg-elem-22"
          ></path>
        </g>
      </g>
      <g id="clust4" class="cluster">
        <title id="title4342">cluster_langchain</title>
        <g fill-opacity="0.250980" stroke-opacity="0.250980" id="g4348">
          <path
            d="M93.8161251001518 -88.04854980577788 C93.8161251001518 -88.04854980577788, 93.8161251001518 -88.04854980577788, 93.8161251001518 -88.04854980577788 M93.8161251001518 -88.04854980577788 C93.8161251001518 -88.04854980577788, 93.8161251001518 -88.04854980577788, 93.8161251001518 -88.04854980577788 M91.97088091782476 -79.12281314720543 C94.20844194940365 -82.22778438655604, 94.74239341868768 -85.86574283233294, 101.5557833635725 -92.08381480539715 M90.33089458544593 -79.43268632105872 C94.16330493716836 -82.80404089740094, 99.34106757372344 -87.23525842304325, 102.85804701100673 -91.57820202891021 M89.90136538801657 -73.21809360989882 C96.694299575588 -79.31553118616459, 100.31177691463283 -84.84302774596975, 106.85391184033197 -92.95091978171261 M92.27035895478421 -73.65369478745225 C98.10535002434128 -79.9609658155587, 102.62774707466998 -87.00658000990819, 107.14585617415531 -92.50740403256953 M92.86992779388734 -66.78601269355057 C99.6936000770709 -76.86896003872822, 106.73662599157876 -86.49951478899638, 112.60666396508793 -92.12093581372484 M91.81695578474366 -65.81121001614548 C96.63619807685535 -74.6655007380628, 103.6246018762457 -82.19120651253239, 113.33246599350214 -91.08289676957558 M92.75708517571832 -60.93679368716699 C101.2603164186127 -71.42805047860743, 108.67241106805967 -82.45787134530352, 119.93517812137809 -93.08962504818088 M90.48783734928644 -61.130935618808394 C98.95849973978733 -67.85715579423731, 105.25581171172769 -75.88628234232618, 118.5300876035293 -91.19327392058393 M90.30330188198118 -54.38880490404161 C101.22620821581316 -68.45612489790587, 109.6265119410611 -78.47052156557515, 123.16190127228097 -91.98015412573243 M91.68206780080523 -55.351675242445516 C98.71579443356599 -63.21641774158859, 105.38598757510323 -72.52231026990206, 123.76000360480418 -91.03431061495898 M91.96950085682637 -46.96468437314624 C101.26083041115268 -61.42055943624424, 113.96131351158382 -76.9128641229701, 129.91899309498746 -91.76883718303131 M90.21536709678529 -48.768932374572685 C102.77849160043905 -62.256915487803774, 115.64993842317563 -76.33211361682311, 128.78056657080492 -91.00461888347897 M90.24471746967407 -42.46119654268132 C101.71582520411593 -57.415961706304664, 116.56989796618952 -70.08417425815477, 134.92251284801011 -92.2386529104559 M91.79675917935373 -42.144414490988524 C101.38454919613747 -54.11918394111677, 109.70924224033615 -64.56655948568796, 134.81388402524573 -91.52210934558352 M89.73648470526368 -35.85401048767033 C103.50941800603401 -50.47640816123262, 115.78172951966647 -66.34011367441192, 137.9583071824963 -90.82924838156609 M90.85655508616642 -35.82862067169422 C103.60423765911817 -50.39608330449123, 116.25603906310677 -64.34227057184124, 139.09844979057095 -91.96003597642438 M91.32951044126096 -28.001912047164332 C110.92819708959507 -52.62561907206001, 132.24613416047873 -77.07247004107217, 145.8298780618253 -90.72848453804144 M91.73969213781434 -29.08968204762348 C101.88347203097334 -42.731434946539636, 113.7153921072895 -56.377044211239664, 145.00752625088887 -91.2170955265533 M93.80256994158934 -26.704511672252956 C112.9655738222684 -49.86678906213116, 134.6988627753117 -72.38381358307501, 152.1006233254631 -91.47169429665797 M93.14900725302664 -25.411711333095624 C115.24808693121082 -52.57754442663255, 136.43682463812618 -76.94522935758152, 150.85200856218336 -91.6268953995126 M95.13665526206583 -20.598711151281496 C113.9872551337025 -46.75791938769569, 138.76035127835007 -70.0047750108573, 154.5052205518212 -92.5444201677416 M94.60615335106192 -21.766604048336728 C116.6419039934773 -47.32185124089518, 139.13911564891828 -72.55572919666302, 154.50707044596612 -91.88457391759074 M97.09217939689817 -17.832621494128922 C109.86659317107775 -35.05564773987033, 128.21152159383666 -52.80068706654969, 158.74650797994713 -90.81622282440017 M96.26851560565738 -17.88226209453228 C117.11840418210079 -39.19586015023769, 135.31015266563008 -62.6550205523482, 159.28848333299607 -90.08983454986925 M102.07437547636722 -18.170707508683947 C114.34110555055575 -36.0528562055471, 130.52815741400244 -54.11882762057534, 164.0404541368797 -88.37791674807058 M100.92600317869157 -15.845526862046277 C118.0274638542361 -37.743273554283185, 135.4100621543155 -56.5340389330983, 162.77376315916166 -88.28963385409281 M106.34388742749589 -15.069100544711219 C125.25437605185009 -38.467797251693554, 143.05378062158388 -62.74823834679553, 165.01160396399038 -86.38360982356154 M105.14891323066422 -14.628466928207565 C116.81357470617782 -29.209718957468844, 129.5884603391378 -44.06750559394376, 166.54768382105402 -85.8994131228214 M111.17459037643367 -13.009286127700836 C132.39226926968385 -40.270259302016754, 152.37074656662142 -64.99672009446428, 169.93623257979007 -82.62286194124522 M110.37472177590759 -15.425462642749027 C129.54087798039677 -38.99317446515554, 152.67910265445923 -62.808016885448694, 168.6265991843703 -81.60146984266298 M116.66378345004597 -15.289690497887326 C134.47595104140436 -35.14184477319813, 151.78590189407612 -57.967733397744915, 169.4734039981879 -78.50638165630166 M116.09292074902362 -15.521584963639008 C133.4278663249949 -36.379404196411606, 151.5377993842789 -56.87367412839608, 169.51797247348827 -77.68713799416655 M121.91039525586174 -14.335200730767799 C131.03217487173183 -28.194272034477045, 146.75185102408264 -45.81793607188157, 168.59918337803808 -71.19081650079788 M119.65274206318868 -15.288457914322544 C135.1886444152949 -29.89680465046115, 148.41725650027178 -47.12348731388818, 169.57827323217114 -70.81010488936283 M127.47710097154867 -14.020293136445087 C142.80789277829243 -34.10576692772426, 160.5074087262958 -52.85673089783016, 169.2715854741237 -64.40062759027302 M125.77093740397386 -15.223922345904128 C137.14994338612834 -27.82610693081871, 147.75357349584556 -41.04991932935011, 170.10332914626463 -65.92192035575137 M131.18376168736543 -14.249645263561323 C142.17861426016339 -27.42550664734039, 151.81239838844465 -38.63726948750794, 170.2637040400733 -60.757271105422944 M131.36452659971178 -14.973873462840096 C140.46013545832787 -24.26539538600551, 149.51594656884754 -34.379650242872756, 168.69823375725966 -59.12738853477777 M134.80960892978374 -13.524116620219228 C149.53422074418978 -29.564745779753046, 159.85983386868568 -41.5990298758794, 168.1677106208065 -54.79731577896898 M135.6785297206934 -14.854086977616367 C147.65998910601098 -28.051399207826012, 158.99910637044496 -40.61649558391801, 169.15661350858704 -53.80915955783152 M139.74681227946692 -16.799674358509183 C151.36999295452034 -24.506305049004105, 158.985174273511 -31.74109770637837, 169.68575861672525 -45.4130224114752 M141.51550495213775 -15.528177610132829 C151.6972376224572 -25.27159545798746, 161.30701073325852 -37.120860787588796, 168.82180549379694 -47.083144721425924 M145.22476428813022 -12.609995696734847 C153.53362691178765 -20.362140860858613, 160.4353883377102 -28.851358877997036, 170.91038528616178 -41.474802280896355 M145.5933641138575 -13.631903587246876 C154.57328023542993 -22.53971749314261, 160.84388033023242 -32.01384494793179, 170.05503958794796 -41.52610775359863 M151.57408327594433 -15.759112667638568 C157.7953342441951 -23.23185180329688, 164.53379988751902 -32.36568615415056, 169.90476792231516 -35.764248460039376 M151.5541805770269 -14.693692374523707 C155.621193236331 -18.747665744989263, 160.65255789861078 -24.009267901289196, 168.90194255616822 -34.484471407304255 M158.30647421182587 -14.543732209370642 C161.13908311914412 -18.78567077025124, 165.41005320165686 -22.14561480242735, 166.776848030463 -27.0642222798425 M157.53769813863107 -14.023899009487693 C160.0379454166307 -18.902751247850578, 163.59264808904257 -22.66715243910103, 167.52059082126735 -28.13827865620525"
            stroke="#f1c40f"
            stroke-width="0.5"
            fill="none"
            id="path4344"
            class="svg-elem-23"
          ></path>
          <path
            d="M102.05 -16.78 C103.31810099148187 -17.031197942992094, 156.18922522622677 -16.876165241925023, 154.35290706367354 -18.69378858124168 M101.4930346142874 -17.531612941914563 C102.48118826798941 -17.785311750384146, 152.87068907071202 -17.65972790833012, 153.4100698219082 -15.06348168735055 M155.05 -16.78 C161.71842722183592 -18.171068989000453, 166.05418844164151 -23.7955609366695, 167.95536877568478 -29.04518506931963 M155.76489516370262 -17.78842348168638 C162.61337427684728 -17.9958235589513, 168.46162558555918 -21.5885880907829, 168.80734980999645 -28.425015026090414 M167.05 -28.78 C167.67768544204 -30.038665686749503, 167.92736141587838 -81.64619347377042, 166.36444709163956 -80.85008472491064 M168.6591195760342 -29.711643168994136 C168.2514159896483 -28.891418987954623, 166.50440916177425 -81.45111226887427, 169.0303743333684 -79.47772753055632 M167.05 -79.78 C168.577947013947 -86.16861113442044, 161.29441530053356 -92.44967165912445, 153.61473703584764 -90.16765340685706 M168.41578085628572 -78.88000048311939 C168.04235554493883 -84.9759522319174, 159.02240690846114 -93.38992853560951, 155.76181399925093 -89.51765777410324 M155.05 -91.78 C155.47342160798354 -93.35685382635937, 101.27772064548363 -90.33305360050426, 102.98583420416105 -92.40236081499812 M153.17295417084577 -92.37863638334257 C156.01239421738063 -93.19672870485017, 103.97358102871917 -89.91993099828046, 103.52547058144786 -92.84820577098273 M102.05 -91.78 C97.28638893118877 -91.2793472424919, 90.22013926392219 -86.58525474506705, 91.2314292801278 -79.75371641227493 M103.30628284914752 -91.41265512218189 C97.33316234090145 -93.23950518278471, 92.25905298568053 -85.40290780971128, 87.97886263774565 -77.62676247153959 M90.05 -79.78 C89.08951950288208 -80.64649338735512, 91.58684802417096 -27.61104354142725, 90.17337632833397 -28.23411219827049 M90.6908584146438 -77.78181693547373 C88.14459796205657 -80.37476692355735, 89.35890781095272 -29.25856417126504, 89.97941922805224 -28.206534807090627 M90.05 -28.78 C91.25596417772714 -24.428947200081975, 96.58862785013686 -15.696537073728932, 100.757182440132 -15.537628188259735 M90.56841057465947 -28.6736377117332 C91.17118028842552 -22.280927283725774, 93.80094024051417 -17.783795080312522, 103.19163943991975 -18.735371479720204"
            stroke="#f1c40f"
            stroke-width="1"
            fill="none"
            id="path4346"
            class="svg-elem-24"
          ></path>
        </g>
        <g
          aria-label="LangChain"
          id="text4350"
          style="
            font-size: 14px;
            font-family: Tinos, serif;
            text-anchor: middle;
          "
        >
          <path
            d="m 101.75996,-85.384689 -1.41504,0.177734 v 8.039063 h 1.80469 q 1.45606,0 2.13965,-0.136719 l 0.42383,-1.907227 h 0.44433 l -0.12304,2.631836 h -7.184572 v -0.362305 l 1.175781,-0.18457 v -8.080078 l -1.175781,-0.177734 v -0.362305 h 3.910152 z"
            id="path4576"
            class="svg-elem-25"
          ></path>
          <path
            d="m 109.17696,-83.149338 q 1.05273,0 1.54492,0.430664 0.49902,0.430664 0.49902,1.319336 v 4.340821 l 0.79981,0.170898 v 0.307617 h -1.76368 l -0.12988,-0.642578 q -0.7793,0.779297 -1.98926,0.779297 -1.64746,0 -1.64746,-1.914063 0,-0.642578 0.2461,-1.05957 0.25293,-0.423828 0.7998,-0.642578 0.54688,-0.225586 1.58594,-0.246094 l 0.96387,-0.02734 v -1.004882 q 0,-0.663086 -0.2461,-0.977539 -0.23926,-0.314454 -0.74512,-0.314454 -0.68359,0 -1.25097,0.32129 l -0.23242,0.799804 h -0.38282 v -1.401367 q 1.10743,-0.239258 1.94825,-0.239258 z m 0.90918,3.294922 -0.89551,0.02734 q -0.91602,0.03418 -1.24414,0.355469 -0.32129,0.321289 -0.32129,1.073242 0,1.203125 0.97754,1.203125 0.46484,0 0.7998,-0.102539 0.3418,-0.109375 0.6836,-0.273438 z"
            id="path4578"
            class="svg-elem-26"
          ></path>
          <path
            d="m 114.42696,-82.486252 q 0.52636,-0.300781 1.12109,-0.492187 0.59473,-0.198243 0.99121,-0.198243 0.83399,0 1.25781,0.485352 0.42383,0.485352 0.42383,1.408203 v 4.22461 l 0.7793,0.170898 v 0.307617 h -2.76856 v -0.307617 l 0.8545,-0.170898 v -4.101563 q 0,-0.567383 -0.28028,-0.888672 -0.27344,-0.328125 -0.85449,-0.328125 -0.61523,0 -1.51074,0.198242 v 5.120118 l 0.86816,0.170898 v 0.307617 h -2.77539 v -0.307617 l 0.77246,-0.170898 v -5.46875 l -0.77246,-0.170899 v -0.307617 h 1.83203 z"
            id="path4580"
            class="svg-elem-27"
          ></path>
          <path
            d="m 125.15938,-80.97551 q 0,1.107422 -0.66309,1.674805 -0.66308,0.567383 -1.90722,0.567383 -0.56055,0 -1.03907,-0.102539 l -0.43066,0.895508 q 0.0205,0.116211 0.2666,0.21875 0.24609,0.102539 0.61523,0.102539 h 1.9004 q 1.03906,0 1.53808,0.451172 0.50586,0.451171 0.50586,1.24414 0,0.717774 -0.40332,1.250977 -0.39648,0.533203 -1.16894,0.820312 -0.77247,0.293946 -1.87305,0.293946 -1.3125,0 -2.00293,-0.403321 -0.6836,-0.40332 -0.6836,-1.148437 0,-0.362305 0.2461,-0.717774 0.24609,-0.348633 0.90234,-0.820312 -0.38965,-0.129883 -0.65625,-0.444336 -0.2666,-0.314453 -0.2666,-0.676758 l 1.08008,-1.216797 q -1.08008,-0.505859 -1.08008,-1.989258 0,-1.052734 0.66309,-1.626953 0.66992,-0.574219 1.9414,-0.574219 0.25293,0 0.64942,0.05469 0.39648,0.04785 0.6084,0.116211 l 1.51074,-0.758789 0.23926,0.293945 -0.9502,0.984375 q 0.45801,0.512695 0.45801,1.510742 z m -0.28028,5.263672 q 0,-0.389648 -0.23925,-0.608398 -0.23926,-0.21875 -0.72461,-0.21875 h -2.48828 q -0.28711,0.246094 -0.47168,0.62207 -0.17774,0.382813 -0.17774,0.710938 0,0.58789 0.42383,0.84082 0.42383,0.259766 1.29883,0.259766 1.1416,0 1.75683,-0.423829 0.62207,-0.423828 0.62207,-1.182617 z m -2.27636,-3.541015 q 0.74511,0 1.05273,-0.423829 0.31445,-0.430664 0.31445,-1.298828 0,-0.909179 -0.32128,-1.291992 -0.32129,-0.389648 -1.03223,-0.389648 -0.71777,0 -1.05274,0.389648 -0.33496,0.389649 -0.33496,1.291992 0,0.902344 0.32813,1.3125 0.32812,0.410157 1.0459,0.410157 z"
            id="path4582"
            class="svg-elem-28"
          ></path>
          <path
            d="m 131.50313,-76.443283 q -2.22852,0 -3.47266,-1.209961 -1.24414,-1.216797 -1.24414,-3.404297 0,-2.365234 1.19629,-3.575195 1.19629,-1.216797 3.54785,-1.216797 1.42871,0 3.06934,0.348633 l 0.041,2.002929 h -0.45117 l -0.20508,-1.189453 q -0.47851,-0.293945 -1.11425,-0.451172 -0.62891,-0.164062 -1.28516,-0.164062 -1.75684,0 -2.56348,1.032226 -0.80664,1.032227 -0.80664,3.199219 0,1.996094 0.84082,3.048828 0.84766,1.052735 2.46094,1.052735 0.7793,0 1.46973,-0.184571 0.69043,-0.191406 1.09375,-0.505859 l 0.25293,-1.367187 h 0.44433 l -0.041,2.15332 q -1.50391,0.430664 -3.2334,0.430664 z"
            id="path4584"
            class="svg-elem-29"
          ></path>
          <path
            d="m 137.77852,-83.511642 q 0,0.710937 -0.0478,1.02539 0.49218,-0.280273 1.11425,-0.485351 0.62891,-0.205079 1.05958,-0.205079 0.83398,0 1.25781,0.485352 0.42383,0.485352 0.42383,1.408203 v 4.22461 l 0.77929,0.170898 v 0.307617 h -2.76855 v -0.307617 l 0.85449,-0.170898 v -4.142579 q 0,-1.175781 -1.13477,-1.175781 -0.64257,0 -1.53808,0.198242 v 5.120118 l 0.86816,0.170898 v 0.307617 h -2.8164 v -0.307617 l 0.81347,-0.170898 v -8.763672 l -0.95703,-0.164063 v -0.307617 h 2.0918 z"
            id="path4586"
            class="svg-elem-30"
          ></path>
          <path
            d="m 145.72871,-83.149338 q 1.05274,0 1.54493,0.430664 0.49902,0.430664 0.49902,1.319336 v 4.340821 l 0.7998,0.170898 v 0.307617 h -1.76367 l -0.12988,-0.642578 q -0.7793,0.779297 -1.98926,0.779297 -1.64746,0 -1.64746,-1.914063 0,-0.642578 0.24609,-1.05957 0.25293,-0.423828 0.79981,-0.642578 0.54687,-0.225586 1.58594,-0.246094 l 0.96386,-0.02734 v -1.004882 q 0,-0.663086 -0.24609,-0.977539 -0.23926,-0.314454 -0.74512,-0.314454 -0.68359,0 -1.25097,0.32129 l -0.23243,0.799804 h -0.38281 v -1.401367 q 1.10742,-0.239258 1.94824,-0.239258 z m 0.90918,3.294922 -0.8955,0.02734 q -0.91602,0.03418 -1.24414,0.355469 -0.32129,0.321289 -0.32129,1.073242 0,1.203125 0.97754,1.203125 0.46484,0 0.7998,-0.102539 0.3418,-0.109375 0.68359,-0.273438 z"
            id="path4588"
            class="svg-elem-31"
          ></path>
          <path
            d="m 151.28633,-77.058517 1.10059,0.170898 v 0.307617 h -3.3291 v -0.307617 l 1.09375,-0.170898 v -5.46875 l -0.90918,-0.170899 v -0.307617 h 2.04394 z m 0.0684,-8.045899 q 0,0.300781 -0.21875,0.519531 -0.21875,0.21875 -0.52637,0.21875 -0.30078,0 -0.51953,-0.21875 -0.21875,-0.21875 -0.21875,-0.519531 0,-0.307617 0.21875,-0.526367 0.21875,-0.21875 0.51953,-0.21875 0.30762,0 0.52637,0.21875 0.21875,0.21875 0.21875,0.526367 z"
            id="path4590"
            class="svg-elem-32"
          ></path>
          <path
            d="m 154.86836,-82.486252 q 0.52637,-0.300781 1.1211,-0.492187 0.59472,-0.198243 0.99121,-0.198243 0.83398,0 1.25781,0.485352 0.42383,0.485352 0.42383,1.408203 v 4.22461 l 0.77929,0.170898 v 0.307617 h -2.76855 v -0.307617 l 0.85449,-0.170898 v -4.101563 q 0,-0.567383 -0.28027,-0.888672 -0.27344,-0.328125 -0.85449,-0.328125 -0.61524,0 -1.51075,0.198242 v 5.120118 l 0.86817,0.170898 v 0.307617 h -2.77539 v -0.307617 l 0.77246,-0.170898 v -5.46875 l -0.77246,-0.170899 v -0.307617 h 1.83203 z"
            id="path4592"
            class="svg-elem-33"
          ></path>
        </g>
      </g>
      <g id="clust5" class="cluster">
        <title id="title4353">cluster_vertexai</title>
        <g fill-opacity="0.250980" stroke-opacity="0.250980" id="g4359">
          <path
            d="M3.386159561779124 -218.33362629006731 C3.386159561779124 -218.33362629006731, 3.386159561779124 -218.33362629006731, 3.386159561779124 -218.33362629006731 M3.386159561779124 -218.33362629006731 C3.386159561779124 -218.33362629006731, 3.386159561779124 -218.33362629006731, 3.386159561779124 -218.33362629006731 M0.7755006340676465 -207.90710439526575 C1.843164065465154 -209.9713609477309, 6.525108111524029 -213.032370729135, 12.644250895529462 -219.94983676151742 M0.03951190287826489 -207.34859699728884 C3.6672871610572666 -211.99476824229924, 7.236882265580197 -216.30233378539305, 12.138323386319913 -221.89539309876105 M0.8910054597158519 -201.8182355125409 C5.470669287664421 -211.53649322546877, 11.58326383866293 -217.36934983634154, 17.367107473143506 -223.41345759805463 M-0.32521841682539376 -201.75989041270336 C3.5389884322879404 -205.8567723430561, 7.058216620818889 -211.12668881856388, 17.232663033972525 -223.0784260737891 M1.707070193117164 -196.55444748651527 C3.4287838899764154 -199.53553421568222, 11.09005216964237 -205.53304025845574, 20.864440152122558 -221.3820367557023 M0.6492280563090858 -195.76424567425707 C6.406373695319128 -202.89169561794859, 12.937826472642989 -211.31927672494734, 23.081785241263677 -222.57090350739898 M0.9939001315248897 -189.25863259445222 C10.946512439331 -201.8868993315287, 19.112856648739747 -215.14638768123152, 28.06020078079635 -220.08160227403567 M-1.2575962388849047 -189.54639795978085 C5.570219537362349 -196.37243960067977, 13.085367223290518 -204.05045933136446, 27.599134558199776 -221.80178134755943 M-1.2887791135995874 -185.86895666325833 C12.188412497817524 -200.3526591752928, 25.65181302223098 -213.06372225233753, 33.86135126807969 -222.82753524239837 M0.07617317201110696 -184.85189843969383 C11.635845213796166 -197.25056580543654, 23.62352646590734 -209.8463237128081, 32.7329409206574 -220.95128312710304 M1.158785707095646 -178.70328892803204 C9.370574223661933 -186.93234032454131, 15.155460715182477 -198.54175021655095, 39.43588908452309 -222.41842405176476 M-0.14083139645882703 -177.50554780620828 C11.934859893390126 -191.69204673285162, 24.362063857216 -205.19998958602167, 38.60263127425358 -221.62453254767033 M0.5881092800998298 -173.11197020594105 C8.292519205958538 -182.46729229840997, 19.749705234623477 -194.81154245976677, 44.57808385623884 -223.4252537512589 M-1.3686298546554845 -171.28493783148502 C13.865338208516496 -187.35260047757706, 26.330712053832464 -203.52256422246967, 43.05028376350007 -221.49471356394972 M0.06496932511934705 -167.59018662107528 C16.110972501812626 -187.54464075275777, 35.68369543022208 -205.8250849086905, 49.0124438537983 -220.80958840608636 M-0.7967705254622404 -166.50774072380392 C14.042969335848438 -181.24118531768343, 29.494001059590474 -198.79348546248195, 48.809413227564264 -221.9353116425366 M-0.955796790227379 -159.97525745405073 C17.518245763439662 -182.18202334166156, 35.951391799574104 -202.37878539605606, 53.84967365446478 -222.43106390629657 M-0.9059071114552419 -159.2613752370061 C16.629357704551975 -177.5228191313027, 31.68301512058278 -195.91931732137473, 53.38649098311144 -221.13711287374227 M1.1070352803427603 -154.34174734231297 C24.3914504384951 -180.38627207417548, 45.20217050277221 -207.5166022169596, 59.294757994162104 -220.45603389695506 M2.220928607835223 -154.2901450863095 C17.08731665227095 -174.25089346896922, 32.88474073956329 -192.08646311213164, 59.761597572245016 -221.86007164341328 M4.496477301146474 -151.0490092475992 C21.317285924326924 -173.6784208269498, 40.81288928638335 -192.1222114776626, 66.53965603743227 -222.82936626119755 M2.9403415284866274 -151.34745910434685 C24.560651872405927 -175.8150372467667, 45.801095212382236 -199.06714152015797, 65.23137513278455 -221.72504123955972 M5.465595219614187 -150.33074169252654 C32.09780721589778 -179.0580980380762, 58.395531984658646 -207.58011683687855, 69.63263910518617 -219.5806032516316 M6.65170703339092 -150.012479679665 C24.11736699150444 -167.9951120932485, 39.928714729356706 -187.6354869970131, 70.65939573773468 -221.3507191615049 M11.518570944012904 -146.27612723781755 C23.322135420140754 -160.2675516610182, 35.76921519526013 -178.3918268877076, 75.16898943098461 -221.43607529023578 M9.905597926829662 -147.11047027073653 C28.27950564233739 -167.4584053368414, 46.20300437998228 -187.9689125791866, 75.77444332599744 -221.96662460025104 M16.05286396722356 -146.0809583509511 C30.45704510587921 -164.6080566722573, 46.190570311735925 -181.60944086380903, 79.61273547113991 -220.1408129296384 M15.19330839443679 -146.77142554507023 C33.78906593642083 -167.7139102867574, 54.01869887336778 -189.98745251395604, 80.45174708080725 -220.9960830236181 M22.188191570611927 -149.0385411862954 C41.479926237900315 -170.84447690952027, 57.753851504235605 -191.14469697053022, 82.44302421492822 -219.72508516645195 M21.64829442442112 -146.44804762466188 C44.64721978193795 -174.14619474702354, 67.21459799344908 -200.42532429133897, 83.4633842808049 -220.1811399692653 M26.312680383098154 -146.96386189273784 C40.699028145193715 -161.47516178962465, 52.22010898147634 -181.01193357826926, 86.57574434438769 -217.897275062123 M25.907527794759286 -146.8531045842812 C41.507983917375384 -164.32211979597702, 55.89976331460665 -182.15007610456266, 87.57997771302396 -217.00043521787958 M32.83341418714695 -147.22685593025145 C51.855802116455095 -172.40735592262638, 71.73848510806678 -198.25150366956507, 89.17554589901606 -212.0991628652321 M32.61002369375766 -146.47963489570338 C48.35923231602539 -165.71006585772662, 62.65457665544833 -183.05108619709557, 90.3088473226091 -214.0895916643028 M34.7673155118822 -145.4771746661499 C49.413888608543715 -159.98504693246838, 61.22999708367274 -173.86410969336882, 90.78807497523543 -209.38569376826246 M36.49167579938768 -147.07112193195317 C58.44845064033346 -171.6076064964425, 79.87037949665766 -195.2781765812936, 90.77608387368278 -209.91614827831364 M40.898361725691316 -144.76324851861898 C55.764208794195056 -163.5402901338713, 72.3247877802398 -178.54966652171572, 89.87860787302417 -201.9757198822072 M42.468207124676226 -146.26827465246282 C57.15708327215864 -164.8653834290892, 73.44046565140651 -182.62617882294157, 91.21650852376672 -204.13569683636948 M48.4923476707835 -145.86499487513828 C63.74893265330374 -163.1848213859411, 75.93073438164926 -182.70707953166746, 93.01372232024967 -196.93220039958817 M48.325639211353966 -147.67524605320546 C62.16831665461011 -164.1268884531131, 76.95365792664393 -181.0838297863803, 90.93660028720772 -198.014085118853 M51.54444364782709 -147.63172014703252 C60.34598927099495 -157.37150639910516, 72.49677525650347 -166.5791766397665, 90.91458771975813 -190.50168291622532 M52.304901480785816 -145.99173208819357 C60.956949478463336 -156.52750700404698, 69.93429056300495 -166.94069654566536, 90.41080342211586 -190.8218617414227 M56.12734628135308 -148.68842836303267 C69.80339166537227 -159.510854488845, 79.71173333405403 -170.25689735047425, 91.5871205815346 -186.43330625232252 M58.11475259522695 -146.47193191005564 C69.17059924699383 -159.79309130732955, 79.86874081811331 -173.6146118126354, 91.43945189160502 -184.6461715485136 M63.33906016337218 -146.78947667662084 C68.44643615876129 -154.39749796836077, 73.55916979998823 -161.06519351499318, 91.88786893978926 -177.4996039027358 M62.52687165411072 -147.46977868185974 C69.54073822768993 -155.2276784914481, 77.33628086695064 -162.45177577169991, 90.66651512847298 -179.43899674729218 M67.03708785235591 -146.8824008881835 C71.95775513832575 -152.61010221306904, 78.47989125978083 -158.0236231536161, 91.95122658591691 -171.32044810519338 M69.46739250025466 -147.57393339780825 C73.43842119293046 -152.921129322672, 80.01557520270312 -159.5550672753265, 90.82935872235635 -172.75072169293526 M72.83093623710538 -147.2007583544486 C77.65638203097338 -154.8172140234108, 83.69555144408454 -160.85073477719155, 92.95655461674345 -168.78755007216714 M72.85557544241993 -147.1554579083033 C78.77682960208944 -152.59413793610292, 83.96540145557022 -159.8888717824554, 91.37815754979991 -167.62740469880865 M79.87092385363644 -146.57588798328206 C81.65491894707633 -151.56730511351685, 83.31194587653087 -152.812737658087, 92.62999796818937 -161.31603483692635 M78.85557362923565 -147.18967228541598 C82.44206872373601 -151.63647547638703, 87.89490699887581 -157.88768791744212, 91.0408328405003 -161.49148569926857"
            stroke="#2ecc71"
            stroke-width="0.5"
            fill="none"
            id="path4355"
            class="svg-elem-34"
          ></path>
          <path
            d="M11.52 -146.95 C13.156811466473563 -147.4236954035773, 77.4070023222088 -147.53518838156148, 79.234970945564 -148.109865084265 M11.933049206426638 -145.559892323462 C10.787495822869428 -148.45075106690504, 78.10704012967408 -148.51622517461615, 76.80476929215621 -145.61101873923582 M78.52 -146.95 C82.81191225600712 -146.18860333094753, 91.00719989736903 -151.1694824844548, 90.07825192185047 -160.23029136845742 M79.44819682830358 -146.33609746495497 C82.59577664841586 -144.81718094656196, 89.35606306102343 -154.52015355631363, 92.0650014623104 -156.82010786820106 M90.52 -158.95 C89.22206847232776 -159.55390970405574, 91.26934141758572 -208.91321954398916, 90.92950181627826 -208.01459460879954 M91.79741610339354 -159.00257871891654 C90.91603138252079 -160.22828774765676, 88.8034790901948 -209.64923974925745, 91.97758350336044 -209.0653246983759 M90.52 -209.95 C92.01870469891863 -215.62185845628994, 84.9653829944505 -220.26364589478197, 79.18117768470401 -220.0244243826417 M89.3124891818839 -211.82234076578987 C91.21958227993312 -217.34403983047952, 86.76200483241752 -222.35290970741775, 80.0104158563196 -219.655737439035 M78.52 -221.95 C78.72941796624481 -223.81434877022787, 13.01248950612061 -222.95569777091188, 11.416057568601206 -221.03248488149285 M77.20087663447195 -223.4175110762066 C80.03932086132228 -221.62737254639947, 10.48733427903127 -224.16541349824044, 10.296945579735954 -221.68022659865375 M11.52 -221.95 C5.612436857383741 -221.34692012881482, -1.723058169238406 -214.74643756909347, 0.22352169723581072 -211.77804125045054 M11.195752442864427 -222.39309817699305 C5.319379891221922 -221.34694960398303, -1.9480882320742636 -216.04334342440103, -1.4010633487022834 -211.4608846319951 M-0.48 -209.95 C0.9415601056769591 -210.8200214631562, 0.5754095825708494 -157.10080237851903, -0.8290217976824334 -160.24354179219017 M0.036518828871634934 -208.24958104182687 C0.3000459643373703 -211.4399672997608, -1.5601781951164801 -159.69153928617482, 0.9119916524852592 -158.59393289010137 M-0.48 -158.95 C1.3988322497649261 -153.4051732482522, 5.392017348533181 -147.50949483602014, 10.248819958844587 -148.54429627301417 M0.6563806189364532 -157.27326531453423 C0.8865744180608108 -154.7800215820423, 4.0864958636915105 -147.28602062682597, 12.818897985923233 -147.63018777647886"
            stroke="#2ecc71"
            stroke-width="1"
            fill="none"
            id="path4357"
            class="svg-elem-35"
          ></path>
        </g>
        <g
          aria-label="Vertex AI"
          id="text4361"
          style="
            font-size: 14px;
            font-family: Tinos, serif;
            text-anchor: middle;
          "
        >
          <path
            d="m 27.954082,-215.91699 v 0.3623 l -1.004882,0.17774 -3.684571,8.83886 h -0.348632 l -3.725586,-8.83886 -1.032227,-0.17774 v -0.3623 h 3.705078 v 0.3623 l -1.230469,0.17774 2.775391,6.74707 2.768555,-6.74707 -1.203125,-0.17774 v -0.3623 z"
            id="path4595"
            class="svg-elem-36"
          ></path>
          <path
            d="m 28.336895,-209.9834 v 0.12305 q 0,0.94336 0.205078,1.46973 0.211914,0.51953 0.642578,0.79296 0.4375,0.27344 1.141602,0.27344 0.36914,0 0.875,-0.0615 0.505859,-0.0615 0.833984,-0.13672 v 0.38281 q -0.328125,0.21192 -0.895508,0.36914 -0.560547,0.15723 -1.148437,0.15723 -1.49707,0 -2.194336,-0.80664 -0.69043,-0.80664 -0.69043,-2.59082 0,-1.68164 0.704102,-2.50879 0.704101,-0.82715 2.009765,-0.82715 2.467774,0 2.467774,2.80273 v 0.56055 z m 1.483398,-2.8164 q -0.710937,0 -1.09375,0.57421 -0.375976,0.57422 -0.375976,1.69532 h 2.748047 q 0,-1.22364 -0.314453,-1.74317 -0.314454,-0.52636 -0.963868,-0.52636 z"
            id="path4597"
            class="svg-elem-37"
          ></path>
          <path
            d="m 37.312481,-213.34668 v 1.73633 h -0.293945 l -0.396485,-0.75195 q -0.341797,0 -0.813476,0.0957 -0.464844,0.0889 -0.806641,0.23926 v 4.79882 l 1.100586,0.1709 v 0.30762 h -3.048828 v -0.30762 l 0.813476,-0.1709 v -5.46875 l -0.813476,-0.17089 v -0.30762 h 1.873047 l 0.06152,0.7998 q 0.410156,-0.34179 1.107422,-0.65625 0.704102,-0.31445 1.114258,-0.31445 z"
            id="path4599"
            class="svg-elem-38"
          ></path>
          <path
            d="m 39.718731,-206.61328 q -0.65625,0 -0.984375,-0.38965 -0.321289,-0.38965 -0.321289,-1.09375 v -4.50488 h -0.84082 v -0.30762 l 0.854492,-0.2666 0.690429,-1.45606 h 0.430664 v 1.45606 h 1.469727 v 0.57422 h -1.469727 v 4.38183 q 0,0.44434 0.198243,0.66993 0.205078,0.22558 0.533203,0.22558 0.396484,0 0.963867,-0.10937 v 0.44433 q -0.239258,0.16406 -0.69043,0.2666 -0.451172,0.10938 -0.833984,0.10938 z"
            id="path4601"
            class="svg-elem-39"
          ></path>
          <path
            d="m 43.10252,-209.9834 v 0.12305 q 0,0.94336 0.205078,1.46973 0.211914,0.51953 0.642578,0.79296 0.4375,0.27344 1.141602,0.27344 0.36914,0 0.875,-0.0615 0.505859,-0.0615 0.833984,-0.13672 v 0.38281 q -0.328125,0.21192 -0.895508,0.36914 -0.560547,0.15723 -1.148437,0.15723 -1.49707,0 -2.194336,-0.80664 -0.69043,-0.80664 -0.69043,-2.59082 0,-1.68164 0.704102,-2.50879 0.704101,-0.82715 2.009765,-0.82715 2.467774,0 2.467774,2.80273 v 0.56055 z m 1.483398,-2.8164 q -0.710937,0 -1.09375,0.57421 -0.375976,0.57422 -0.375976,1.69532 h 2.748047 q 0,-1.22364 -0.314453,-1.74317 -0.314454,-0.52636 -0.963868,-0.52636 z"
            id="path4603"
            class="svg-elem-40"
          ></path>
          <path
            d="m 54.368145,-207.05762 v 0.30762 h -2.912109 v -0.30762 l 0.854492,-0.15722 -1.483399,-2.27637 -1.736328,2.29004 0.881836,0.14355 V -206.75 H 47.66209 v -0.30762 l 0.745117,-0.10937 2.112305,-2.78906 -1.859375,-2.74122 -0.758789,-0.17089 v -0.30762 h 2.912109 v 0.30762 l -0.854492,0.18457 1.237305,1.8457 1.421875,-1.85938 -0.881836,-0.17089 v -0.30762 h 2.310547 v 0.30762 l -0.738281,0.14355 -1.804688,2.33789 2.112305,3.18555 z"
            id="path4605"
            class="svg-elem-41"
          ></path>
          <path
            d="m 60.41795,-207.1123 v 0.3623 h -3.014649 v -0.3623 l 1.039063,-0.18457 3.124023,-8.69532 h 1.298828 l 3.247071,8.69532 1.162109,0.18457 v 0.3623 h -3.875977 v -0.3623 l 1.230469,-0.18457 -0.90918,-2.64551 h -3.609375 l -0.922851,2.64551 z m 1.469726,-7.89551 -1.572265,4.45019 h 3.192382 z"
            id="path4607"
            class="svg-elem-42"
          ></path>
          <path
            d="m 70.371075,-207.29687 1.175781,0.18457 v 0.3623 h -3.664063 v -0.3623 l 1.175782,-0.18457 v -8.08008 l -1.175782,-0.17774 v -0.3623 h 3.664063 v 0.3623 l -1.175781,0.17774 z"
            id="path4609"
            class="svg-elem-43"
          ></path>
        </g>
      </g>
      <!-- ares -->
      <g id="node1" class="node">
        <title id="title4364">ares</title>
        <g id="g4370">
          <path
            d="M167.72078711238393 -254.35646809844698 C167.72078711238393 -254.35646809844698, 167.72078711238393 -254.35646809844698, 167.72078711238393 -254.35646809844698 M167.72078711238393 -254.35646809844698 C167.72078711238393 -254.35646809844698, 167.72078711238393 -254.35646809844698, 167.72078711238393 -254.35646809844698 M166.77540375738047 -248.6872655636896 C169.2159558770736 -249.5238210651358, 170.17645557294537 -251.4388932565102, 172.4509129316166 -253.85418578516715 M167.25970828389552 -248.2685069136543 C169.57411248564844 -250.3350287723364, 171.55481048844752 -252.88180937088546, 172.94788968995744 -254.33331495607754 M168.84946396272045 -241.46957000907307 C172.67287094722494 -246.7472391075067, 174.1990955494037 -250.43539044237696, 177.15649697809158 -255.54202275062073 M168.06745647595736 -241.67923731243079 C169.41344861266646 -245.27159298467575, 172.74843875257827 -248.27187691740477, 179.0307157679168 -254.1401482375326 M168.2460223751468 -234.5871722725794 C172.15635454128804 -241.56380614624013, 175.24886256343638 -243.37227318341385, 181.34931340698694 -252.54709087811486 M168.53033289795673 -235.98300868651543 C173.6017225015381 -241.7134077953457, 178.21216257604013 -247.80598006035527, 183.5088183037468 -253.31910743364108 M169.02598718261623 -230.50965052458645 C175.68364157548658 -237.1321548890438, 182.67475925428445 -245.00431916153332, 187.85716050063573 -256.38979000395597 M166.71389385760764 -228.93060299884763 C172.1716117517133 -236.25605715735207, 178.15336694146652 -242.8006971351179, 189.63909903601336 -255.2984366936044 M168.388611562484 -225.48493956840173 C176.5259214069345 -235.120587839061, 185.2190786934346 -240.81310849637993, 193.5301776485235 -254.16582384521968 M168.10255874590348 -223.05335029184332 C174.3113781835834 -231.56080011745857, 180.87905926014955 -237.83275519983434, 193.72498791406287 -254.91567607271637 M167.00537732398902 -216.8382314782836 C179.81258345638042 -232.85881667145628, 190.0965435695147 -243.69118863520347, 200.4588436942124 -253.86880437285177 M168.2989575604983 -219.0183453737995 C174.42019333101905 -226.48149929333178, 182.85893520962017 -234.74984217709869, 200.17396501213227 -254.24069071432268 M171.1473883007994 -218.92777866479383 C183.14372889020225 -229.08564260856824, 197.13628436780772 -244.22287603640785, 205.22985653653848 -253.4227262285538 M173.87414300865467 -217.41449820206088 C181.20466851799296 -228.07040159016015, 189.83749442164296 -237.51475532760233, 204.23903955016695 -254.63429300922655 M177.81018350108394 -218.52122831547837 C190.6837013325978 -232.22473869153418, 202.0660872532284 -245.3450043104055, 210.20580937765175 -256.1090845388109 M179.30523414085758 -218.2505788068663 C185.16214676886753 -224.61387666209558, 191.00668456963945 -232.0384478866153, 210.69806551538946 -253.95107916147117 M183.90285016904113 -216.4425746867173 C193.7345913886856 -231.01436180309474, 204.63878468329938 -243.488934614318, 215.81822600252312 -255.61641800850475 M184.36180389656678 -217.29714871363066 C193.55262467225427 -228.8221390222264, 201.3844241151938 -238.9439945996587, 215.7164457253539 -254.28693775705446 M190.55267142687046 -217.1687869618752 C194.9401973613458 -227.9748320779045, 202.19976993904356 -236.72784709875296, 219.82718795570838 -251.75009103309608 M188.00335779722522 -217.73263376797283 C197.37015004748997 -226.8865932486665, 203.7635566175879 -235.91684667725295, 217.54041780889602 -250.73405540605978 M194.77794589901433 -219.37124217501102 C203.59386422465136 -226.72383153316534, 210.41037305611462 -236.11505514347925, 221.08082350941018 -248.28236006939414 M193.82681525161357 -218.30125321581272 C204.26121977837698 -228.21932017661638, 213.0587238244989 -240.38857543173475, 220.38247753540327 -248.5718491393312 M199.91875325199925 -218.2501883642388 C206.04886646748417 -224.18035690864366, 209.68294607054864 -229.05222251799822, 222.28505563569166 -245.17153601461675 M198.9037661504914 -217.03483246048282 C205.7342218755964 -226.48212065218928, 214.03325459867935 -234.70261569903542, 222.58002621250458 -243.04356844197287 M204.51072080330619 -219.03193757292388 C210.02121675745923 -226.02092319168648, 217.5615876656847 -233.91262295821008, 220.1389693216006 -236.04969782627572 M204.05760070820892 -217.61145519049617 C211.91678222589886 -224.9337762363633, 216.9162294462792 -233.4764131419709, 221.06254980698532 -237.01054352970547 M210.8219237927054 -217.51355050307157 C215.4878865925934 -221.88382752365106, 219.72237475358068 -227.81924817441205, 221.4586689054336 -230.97587171070467 M210.56496420569596 -218.1229383069441 C214.33441138642726 -222.1322162613866, 219.27817631219045 -228.59920822523125, 221.6143863065788 -230.93218974599904 M215.37734880005377 -217.45198155308935 C217.33708036021306 -219.73094221801153, 218.72294753608503 -221.1772797907639, 222.03003557506491 -224.59072398597402 M215.47631929270406 -217.93636928364944 C217.52735412747015 -220.79722940480983, 219.75221936597237 -223.0538763355368, 221.40863813710374 -225.0119167903491 M220.62214169097817 -217.85043732797374 C220.8877201120838 -217.9750803156657, 221.32527746304226 -218.23842050012684, 221.84580223643965 -219.05135269538275 M220.68734330420187 -217.5946381379212 C220.93842819557906 -218.07004429582605, 221.14186572560925 -218.42055156542065, 221.98940373947616 -219.25549273047235"
            stroke="none"
            stroke-width="0.5"
            fill="none"
            id="path4366"
            class="svg-elem-44"
          ></path>
          <path
            d="M215.81085433551965 -254.0749944509057 C203.7109124912032 -253.36463401856838, 188.00445092829142 -252.50917125242435, 169.1204637127352 -255.2921844158646 M215.47971452703325 -254.94051180905788 C203.8009759111025 -254.39653763488846, 194.03671947860013 -255.27272561931352, 167.71794907343758 -254.74361848799802 M168.73737125907405 -255.3550936134125 C166.90497996487545 -245.85845380195687, 167.16970928524822 -233.37876946045904, 167.54079033562098 -219.93200384816706 M167.2461530845092 -253.74769535887094 C167.75717303233168 -240.56791221260124, 166.67309626632792 -225.0963650579577, 167.90042176496965 -219.13910848901062 M167.47369963698264 -216.37860957604153 C183.96988156376807 -218.96659908434523, 198.69260215920494 -217.62955200409615, 222.9417793916186 -217.66578092062716 M167.47262872843714 -218.76378197927687 C183.98756619018684 -217.35751106060127, 199.7113742884377 -218.29797852507252, 221.9159619315923 -217.7048295139444 M221.18915015325564 -218.82689530254677 C219.97470778025112 -226.34530195644396, 223.10924140266437 -232.84427605748843, 222.5101678549285 -248.23381893836586 M221.11043187903465 -218.1904997569459 C221.7815084384756 -229.31582926020263, 221.7676639604345 -240.9785676843856, 220.95502622610388 -248.87856458890414 M220.98956303967228 -248.99022511987496 C219.75454728990493 -250.69935912091273, 216.82211858301517 -253.40160584371296, 216.27896590640995 -253.6446509592438 M221.8075834214609 -248.31835663790366 C220.13435116650302 -249.7687339078312, 218.8076004284001 -250.26104580371916, 215.87898547486117 -254.31925730332378 M215.55 -254.16 C215.55 -254.16, 215.55 -254.16, 215.55 -254.16 M215.55 -254.16 C215.55 -254.16, 215.55 -254.16, 215.55 -254.16"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4368"
            class="svg-elem-45"
          ></path>
        </g>
        <g id="g4374">
          <path
            d="M216.0423102885333 -254.5513292404796 C215.13761368562083 -252.74375207903665, 215.41998727901444 -250.00316777333288, 215.35317375338448 -248.1465907965932 M215.29767994481685 -254.10480211697453 C215.29346214563 -252.22881017209536, 215.74691260527538 -249.8478162872423, 215.47948589466108 -247.89548889494577"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4372"
            class="svg-elem-46"
          ></path>
        </g>
        <g id="g4378">
          <path
            d="M221.7173788210982 -248.24432679654996 C220.53111538861836 -247.61036596217556, 218.2827720115608 -248.07241885231636, 215.82729068848266 -248.1539910449293 M221.40551272156915 -248.3198798605183 C219.6174677396826 -247.98259331861343, 217.60386970741217 -247.8259435063492, 215.78873551806902 -248.42025452243897"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4376"
            class="svg-elem-47"
          ></path>
        </g>
        <g
          aria-label="Ares"
          id="text4380"
          style="
            font-size: 14px;
            font-family: Tinos, serif;
            text-anchor: middle;
          "
        >
          <path
            d="m 184.48409,-232.82231 v 0.3623 h -3.01465 v -0.3623 l 1.03906,-0.18457 3.12402,-8.69531 h 1.29883 l 3.24707,8.69531 1.16211,0.18457 v 0.3623 h -3.87598 v -0.3623 l 1.23047,-0.18457 -0.90918,-2.64551 h -3.60937 l -0.92285,2.64551 z m 1.46972,-7.89551 -1.57226,4.4502 h 3.19238 z"
            id="path4612"
            class="svg-elem-48"
          ></path>
          <path
            d="m 195.98213,-239.05669 v 1.73633 h -0.29394 l -0.39649,-0.75195 q -0.34179,0 -0.81347,0.0957 -0.46485,0.0889 -0.80664,0.23926 v 4.79883 l 1.10058,0.1709 v 0.30761 h -3.04883 v -0.30761 l 0.81348,-0.1709 v -5.46875 l -0.81348,-0.1709 v -0.30762 h 1.87305 l 0.0615,0.79981 q 0.41016,-0.3418 1.10743,-0.65625 0.7041,-0.31446 1.11425,-0.31446 z"
            id="path4614"
            class="svg-elem-49"
          ></path>
          <path
            d="m 197.88252,-235.69341 v 0.12305 q 0,0.94336 0.20508,1.46973 0.21191,0.51953 0.64258,0.79297 0.4375,0.27343 1.1416,0.27343 0.36914,0 0.875,-0.0615 0.50586,-0.0615 0.83398,-0.13672 v 0.38281 q -0.32812,0.21192 -0.8955,0.36915 -0.56055,0.15722 -1.14844,0.15722 -1.49707,0 -2.19434,-0.80664 -0.69043,-0.80664 -0.69043,-2.59082 0,-1.68164 0.70411,-2.50879 0.7041,-0.82715 2.00976,-0.82715 2.46777,0 2.46777,2.80274 v 0.56054 z m 1.4834,-2.8164 q -0.71094,0 -1.09375,0.57422 -0.37598,0.57422 -0.37598,1.69531 h 2.74805 q 0,-1.22363 -0.31445,-1.74316 -0.31445,-0.52637 -0.96387,-0.52637 z"
            id="path4616"
            class="svg-elem-50"
          ></path>
          <path
            d="m 207.26143,-234.26469 q 0,0.95703 -0.6084,1.44921 -0.60156,0.49219 -1.78418,0.49219 -0.47851,0 -1.05957,-0.10254 -0.57422,-0.0957 -0.90234,-0.21875 v -1.5791 h 0.30761 l 0.33496,0.89551 q 0.5127,0.46484 1.33301,0.46484 1.32617,0 1.32617,-1.13476 0,-0.83399 -1.04589,-1.18946 l -0.6084,-0.19824 q -0.69043,-0.22558 -1.00489,-0.45801 -0.31445,-0.23242 -0.48535,-0.56738 -0.1709,-0.3418 -0.1709,-0.82031 0,-0.84766 0.57422,-1.33301 0.58106,-0.49219 1.56543,-0.49219 0.7041,0 1.76368,0.21192 v 1.40136 h -0.32129 l -0.28711,-0.74511 q -0.36231,-0.32129 -1.1416,-0.32129 -0.55372,0 -0.84766,0.27344 -0.28711,0.27343 -0.28711,0.73828 0,0.38965 0.25977,0.65625 0.2666,0.2666 0.7998,0.44433 1.00488,0.3418 1.3125,0.49903 0.30762,0.15722 0.51953,0.38965 0.21875,0.22558 0.33496,0.51953 0.12305,0.29394 0.12305,0.72461 z"
            id="path4618"
            class="svg-elem-51"
          ></path>
        </g>
      </g>
      <!-- game_loop -->
      <g id="node3" class="node">
        <title id="title4383">game_loop</title>
        <g id="g4389">
          <path
            d="M114.21479939838397 -168.36721427710395 C114.21479939838397 -168.36721427710395, 114.21479939838397 -168.36721427710395, 114.21479939838397 -168.36721427710395 M114.21479939838397 -168.36721427710395 C114.21479939838397 -168.36721427710395, 114.21479939838397 -168.36721427710395, 114.21479939838397 -168.36721427710395 M108.2939576556409 -155.9886896664877 C115.30798073505466 -160.6766912539314, 118.72717025214742 -166.9403073106222, 121.85936850528192 -170.47686359944686 M109.7191713980432 -157.96373975772056 C114.94531270736374 -161.9776170003008, 118.57403144562696 -166.20035355196327, 122.07348558585882 -171.67285006414286 M112.38424298689569 -156.84557963405294 C119.8559989243211 -162.86624946903854, 124.89763433932109 -168.66137719552086, 128.73450374344648 -174.78206524700505 M112.92161335952204 -156.34361244218695 C119.46530024483201 -162.75936951577972, 126.82757821334718 -169.84052049959948, 129.36386347025285 -175.18338228901283 M115.48025721269691 -154.34945460241835 C123.67054698488548 -161.5788235741621, 127.97123586705173 -165.07945060677778, 136.4614685643083 -178.83485022771902 M117.43364493044648 -152.83247600207542 C122.2085973604938 -159.8508117192627, 128.0495380536112 -167.18693077190522, 137.903416149675 -177.21572282279868 M118.51836755233658 -151.70623962006724 C127.68779945242301 -159.03484751695385, 137.15043288775124 -166.56803682939045, 143.69957671992324 -178.56540755262 M119.7557013812712 -151.71931429337687 C127.43111577649097 -158.3951374402465, 134.40357868107608 -167.18956090467668, 143.63552996532923 -177.6151441518678 M123.88570460120789 -150.06456337560803 C129.87425709293794 -154.66526663207927, 135.30521573453495 -163.86565513514122, 149.77398303084846 -176.74254547650912 M124.36329865342412 -148.37329254012323 C133.07585463274617 -159.17904599050553, 140.3354968553217 -167.31402771457218, 147.39054441435732 -177.85020734353745 M127.62629118986925 -148.71189899589677 C134.59969920230756 -155.6123569088879, 137.82369005378564 -162.027849027242, 152.96998516560453 -175.22114606485846 M128.53875156411766 -147.37889469374613 C134.2817779990146 -155.25474689537373, 140.07721754073805 -162.1000299726729, 153.25210283186095 -176.62930640595198 M131.41930884746765 -147.88254210569886 C137.39899666455875 -152.5904740638738, 141.91818659611587 -157.41424436799326, 157.9548608355235 -176.408007414372 M132.6908763288069 -146.6597968321269 C142.6921636209005 -156.99553201042553, 150.54367868904993 -169.3740884290953, 158.97034421459745 -176.43627875122903 M135.74803474722958 -147.05738563735807 C145.2440014682811 -156.86880143349475, 155.03061225388296 -164.2156583550442, 164.0070219431443 -177.75478657367574 M136.37201260546865 -145.86917831709704 C144.8154421428994 -154.79299033535887, 151.88035172044005 -162.27294408894463, 164.91159065605828 -176.75451023087396 M140.85828005181216 -146.88470598188303 C148.94211247551505 -153.72922454068717, 159.83684906070425 -162.77288241081416, 170.0089820643246 -178.6309952270748 M142.0112178188094 -144.837584015358 C150.06406115895055 -156.06178654238798, 159.98921069658167 -164.79238373804998, 169.46906888558954 -176.4609282676955 M144.8459498265663 -143.78751043578828 C158.52997305209996 -157.94952718202765, 167.97511665441493 -167.75583696793512, 173.1724897852168 -176.8000250177781 M147.08293893608302 -144.54080700420525 C156.15263950410804 -155.18123061776456, 165.55966983579683 -166.592020564534, 173.00341027097326 -176.55095670873143 M152.8702359107567 -146.02351298969916 C156.57373723159284 -153.6513807151732, 166.86838922106278 -159.8182277183847, 178.08145682623686 -174.18615373254235 M152.14784448082617 -144.10627641917736 C159.72704479965137 -152.26719251292627, 165.28460826319696 -160.62491632295348, 179.64932272059895 -175.39831846644842 M157.77133079577732 -142.46035664970304 C165.77626071235014 -152.10891837192383, 170.66446804556733 -160.92733134550235, 184.84565868690945 -176.13138702047334 M156.9967724028296 -144.08312172363708 C166.7460614084261 -155.18391254286655, 177.4957790797131 -168.37511241892076, 183.404952634811 -175.36060458276506 M162.50552893925692 -143.4080403002971 C168.0981845673857 -153.25837549315654, 176.95764265166187 -161.09768009533798, 187.9888048554861 -173.0892355199593 M161.95313369145524 -145.04035832255397 C168.6245023420025 -153.07700992046938, 176.9591776484746 -161.2878777205342, 188.58343644823708 -173.6441206575428 M165.6383020523515 -144.95621204281105 C176.4487637345202 -152.21065467957106, 184.19148979386256 -162.61706740033202, 193.57322474625914 -175.85221831882694 M168.3703358847691 -143.55390332531277 C178.348183792988 -155.44457609290296, 188.03412325384875 -166.75705901987422, 192.95521515368281 -173.47167881810245 M174.88229949613773 -145.22795850901971 C180.36482241336165 -154.51306182036967, 189.29921264943258 -162.80339550112444, 196.36417497068075 -171.94960140569478 M173.73209269239996 -145.06225657612964 C182.02112977968122 -154.68496658724362, 191.80740147327754 -166.54495710787873, 197.35508193297824 -172.05770031301483 M179.3095830114529 -145.86111647729547 C185.08993795484767 -151.98973519204952, 189.52932865628244 -155.11519775133897, 200.51142194525227 -170.74133058489352 M178.83791265401263 -145.23878405828816 C183.30415613091952 -151.83348373317298, 187.69996603237726 -156.19592400702922, 200.3938652864183 -170.37133406633296 M186.5501174912416 -145.0645932800734 C188.25268723704653 -149.6417734088448, 194.73694270839272 -155.82265825475451, 205.0728224925246 -168.24223814103112 M184.2704640494892 -145.87383129030795 C190.45733780482644 -152.2804776459571, 193.9007496636734 -157.37899776102242, 204.8749294138664 -168.35859224154922 M193.9632268663627 -148.90544957150837 C197.94805508299632 -152.650247843388, 200.71715708992224 -158.55112085449298, 208.86691605351635 -166.91070657599903 M191.98095464227754 -149.1355358741747 C196.05101703434994 -153.86724641080133, 199.381523802036 -157.4415429634461, 206.790817530013 -165.91580800580516 M200.39640420354334 -151.20217602110256 C204.65419112610294 -156.21968923629115, 206.40850090323264 -159.018824752511, 212.40758752007275 -165.24751467344103 M199.9963658439409 -151.08130984342955 C201.15739552340048 -153.4528074955092, 205.8112828746544 -156.28458969238565, 210.86685483520196 -164.39177108170975"
            stroke="none"
            stroke-width="0.5"
            fill="none"
            id="path4385"
            class="svg-elem-52"
          ></path>
          <path
            d="M168.9349427794405 -177.41183939168985 C178.1160623011181 -177.1173066855987, 187.97781105128018 -176.39679384886875, 194.91832871129 -174.14766903347544 C201.85884637129982 -171.89854421808212, 208.91824325211925 -167.5123694428513, 210.57804873949942 -163.91709049932987 C212.2378542268796 -160.32181155580844, 209.56898478890582 -155.62089887934718, 204.87716163557107 -152.5759953723469 C200.18533848223632 -149.53109186534664, 191.19986057083622 -147.11085024803214, 182.42710981949094 -145.6476694573282 C173.65435906814565 -144.18448866662425, 161.93690959166756 -143.2417008610074, 152.24065712749942 -143.79691062812321 C142.54440466333128 -144.35212039523904, 131.39845662919126 -146.64109550693814, 124.24959503448207 -148.9789280600232 C117.1007334397729 -151.31676061310827, 110.9801279435342 -154.5467108501126, 109.34748755924434 -157.82390594663357 C107.71484717495449 -161.10110104315456, 109.66893529526808 -165.36395025692195, 114.45375272874291 -168.6420986391491 C119.23857016221774 -171.92024702137627, 126.97523318532498 -176.27029451052996, 138.05639216009328 -177.4927962399966 C149.13755113486158 -178.71529796946325, 172.15483312170224 -176.45546932613175, 180.94070657735273 -175.9771090159489 C189.72658003300322 -175.49874870576608, 191.12830801375443 -174.90826393240906, 190.77163289399618 -174.62263437889965 M165.50797099925123 -178.11891013873833 C175.03468673741654 -178.08619279944355, 188.55553799341772 -177.42964547660358, 195.76298187032012 -174.87039076031044 C202.97042574722252 -172.3111360440173, 206.85985689526214 -166.41250745021821, 208.7526342606656 -162.76338184097955 C210.64541162606903 -159.11425623174088, 210.93200540341877 -155.74828002051086, 207.1196460627408 -152.9756371048784 C203.30728672206283 -150.2029941892459, 194.649233508288 -147.69419733754157, 185.87847821659773 -146.12752434718467 C177.10772292490745 -144.56085135682778, 164.54878026569327 -143.38259290180213, 154.49511431259913 -143.575599162737 C144.441448359505 -143.7686054236719, 132.66325728694454 -144.8896163212827, 125.55648249803289 -147.28556191279387 C118.44970770912124 -149.68150750430505, 113.6725586824241 -154.4390971425507, 111.85446557912925 -157.95127271180402 C110.03637247583441 -161.46344828105734, 110.8404903487169 -165.30845578728258, 114.64792387826388 -168.35861532831373 C118.45535740781087 -171.40877486934488, 126.34025430449731 -174.4973828570394, 134.69906675641118 -176.25222995799083 C143.05787920832506 -178.00707705894226, 159.59084247676375 -178.69955643478247, 164.8007985897472 -178.88769793402233 C170.01075470273062 -179.0758394332622, 165.7127334634507 -177.63902838842006, 165.95880343431185 -177.38107895343003"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4387"
            class="svg-elem-53"
          ></path>
        </g>
        <g
          aria-label="Game loop"
          id="text4391"
          style="
            font-size: 14px;
            font-family: Tinos, serif;
            text-anchor: middle;
          "
        >
          <path
            d="m 137.92865,-157.64851 q -0.79297,0.25976 -1.64746,0.4375 -0.85449,0.17773 -1.83887,0.17773 -2.22851,0 -3.47265,-1.20312 -1.24415,-1.20313 -1.24415,-3.41114 0,-2.40625 1.20313,-3.5957 1.20996,-1.19629 3.54102,-1.19629 1.66796,0 3.21972,0.41016 v 1.96875 h -0.45801 l -0.18457,-1.13477 q -0.47168,-0.33496 -1.13476,-0.51269 -0.65625,-0.18457 -1.3877,-0.18457 -1.75,0 -2.56347,1.04589 -0.80664,1.03907 -0.80664,3.18555 0,2.0166 0.83398,3.0625 0.83398,1.03906 2.46777,1.03906 0.57422,0 1.20313,-0.13672 0.6289,-0.13671 0.95703,-0.32812 v -2.60449 l -1.17578,-0.17774 v -0.36914 h 3.38379 v 0.36914 l -0.89551,0.17774 z"
            id="path4621"
            class="svg-elem-54"
          ></path>
          <path
            d="m 142.44037,-163.73933 q 1.05273,0 1.54492,0.43066 0.49902,0.43066 0.49902,1.31934 v 4.34082 l 0.79981,0.17089 v 0.30762 h -1.76367 l -0.12989,-0.64258 q -0.77929,0.7793 -1.98925,0.7793 -1.64746,0 -1.64746,-1.91406 0,-0.64258 0.24609,-1.05957 0.25293,-0.42383 0.7998,-0.64258 0.54688,-0.22559 1.58594,-0.24609 l 0.96387,-0.0274 v -1.00488 q 0,-0.66309 -0.2461,-0.97754 -0.23925,-0.31445 -0.74511,-0.31445 -0.6836,0 -1.25098,0.32129 l -0.23242,0.7998 h -0.38281 v -1.40137 q 1.10742,-0.23925 1.94824,-0.23925 z m 0.90918,3.29492 -0.89551,0.0273 q -0.91602,0.0342 -1.24414,0.35547 -0.32129,0.32129 -0.32129,1.07324 0,1.20313 0.97754,1.20313 0.46484,0 0.7998,-0.10254 0.3418,-0.10938 0.6836,-0.27344 z"
            id="path4623"
            class="svg-elem-55"
          ></path>
          <path
            d="m 147.70404,-163.07625 q 0.5127,-0.29394 1.08691,-0.49219 0.57422,-0.19824 1.01172,-0.19824 0.47168,0 0.86817,0.17774 0.40332,0.17773 0.60156,0.56738 0.52637,-0.29395 1.23047,-0.51953 0.71094,-0.22559 1.17578,-0.22559 1.64062,0 1.64062,1.89356 v 4.22461 l 0.82715,0.17089 v 0.30762 h -2.91894 v -0.30762 l 0.95703,-0.17089 v -4.10157 q 0,-1.17578 -1.09375,-1.17578 -0.17774,0 -0.41699,0.0274 -0.23242,0.0273 -0.47168,0.0615 -0.23242,0.0342 -0.45117,0.082 -0.21192,0.041 -0.35547,0.0684 0.11621,0.36914 0.11621,0.81348 v 4.22461 l 0.96386,0.17089 v 0.30762 h -3.04882 v -0.30762 l 0.95019,-0.17089 v -4.10157 q 0,-0.56738 -0.29394,-0.86816 -0.28711,-0.30762 -0.86817,-0.30762 -0.60156,0 -1.49707,0.19824 v 5.07911 l 0.96387,0.17089 v 0.30762 h -2.91211 v -0.30762 l 0.81348,-0.17089 v -5.46875 l -0.81348,-0.1709 v -0.30762 h 1.87988 z"
            id="path4625"
            class="svg-elem-56"
          ></path>
          <path
            d="m 158.14252,-160.4034 v 0.12305 q 0,0.94336 0.20508,1.46973 0.21191,0.51953 0.64257,0.79297 0.4375,0.27343 1.1416,0.27343 0.36915,0 0.875,-0.0615 0.50586,-0.0615 0.83399,-0.13672 v 0.38281 q -0.32813,0.21192 -0.89551,0.36914 -0.56055,0.15723 -1.14844,0.15723 -1.49707,0 -2.19433,-0.80664 -0.69043,-0.80664 -0.69043,-2.59082 0,-1.68164 0.7041,-2.50879 0.7041,-0.82715 2.00977,-0.82715 2.46777,0 2.46777,2.80274 v 0.56054 z m 1.4834,-2.8164 q -0.71094,0 -1.09375,0.57422 -0.37598,0.57421 -0.37598,1.69531 h 2.74805 q 0,-1.22363 -0.31446,-1.74317 -0.31445,-0.52636 -0.96386,-0.52636 z"
            id="path4627"
            class="svg-elem-57"
          ></path>
          <path
            d="m 168.58783,-157.64851 1.10059,0.17089 v 0.30762 h -3.32911 v -0.30762 l 1.09375,-0.17089 v -8.76368 l -1.09375,-0.16406 v -0.30762 h 2.22852 z"
            id="path4629"
            class="svg-elem-58"
          ></path>
          <path
            d="m 176.43549,-160.41707 q 0,3.38379 -3.00782,3.38379 -1.44922,0 -2.1875,-0.86816 -0.73828,-0.86817 -0.73828,-2.51563 0,-1.62695 0.73828,-2.48828 0.73828,-0.86133 2.24219,-0.86133 1.46289,0 2.20801,0.84766 0.74512,0.84082 0.74512,2.50195 z m -1.23047,0 q 0,-1.47656 -0.43067,-2.13965 -0.43066,-0.66308 -1.34668,-0.66308 -0.8955,0 -1.29882,0.63574 -0.39649,0.63574 -0.39649,2.16699 0,1.55176 0.40332,2.20117 0.41016,0.64258 1.29199,0.64258 0.90235,0 1.33985,-0.66992 0.4375,-0.66992 0.4375,-2.17383 z"
            id="path4631"
            class="svg-elem-59"
          ></path>
          <path
            d="m 183.43549,-160.41707 q 0,3.38379 -3.00782,3.38379 -1.44922,0 -2.1875,-0.86816 -0.73828,-0.86817 -0.73828,-2.51563 0,-1.62695 0.73828,-2.48828 0.73828,-0.86133 2.24219,-0.86133 1.46289,0 2.20801,0.84766 0.74512,0.84082 0.74512,2.50195 z m -1.23047,0 q 0,-1.47656 -0.43067,-2.13965 -0.43066,-0.66308 -1.34668,-0.66308 -0.8955,0 -1.29882,0.63574 -0.39649,0.63574 -0.39649,2.16699 0,1.55176 0.40332,2.20117 0.41016,0.64258 1.29199,0.64258 0.90235,0 1.33985,-0.66992 0.4375,-0.66992 0.4375,-2.17383 z"
            id="path4633"
            class="svg-elem-60"
          ></path>
          <path
            d="m 185.00775,-163.11726 -0.73144,-0.1709 v -0.30762 h 1.80468 l 0.0137,0.37598 q 0.2871,-0.2461 0.76562,-0.39649 0.48535,-0.15039 0.98438,-0.15039 1.23046,0 1.90039,0.85449 0.67675,0.8545 0.67675,2.45411 0,1.63378 -0.73828,2.52929 -0.73144,0.89551 -2.11914,0.89551 -0.77246,0 -1.46972,-0.15039 0.041,0.49219 0.041,0.77246 v 1.73633 l 1.12109,0.16406 v 0.32129 h -3.0625 v -0.32129 l 0.81348,-0.16406 z m 4.1836,2.65918 q 0,-1.3125 -0.43067,-1.94825 -0.42383,-0.64257 -1.29199,-0.64257 -0.79981,0 -1.33301,0.22558 v 5.13379 q 0.6084,0.11621 1.33301,0.11621 1.72266,0 1.72266,-2.88476 z"
            id="path4635"
            class="svg-elem-61"
          ></path>
        </g>
      </g>
      <!-- ares&#45;&gt;game_loop -->
      <g id="edge1" class="edge">
        <title id="title4394">ares-&gt;game_loop</title>
        <g id="g4398">
          <path
            d="M186.2 -217.93 C180.64213647215334 -207.92554233806376, 177.8716149773599 -196.243203751135, 173.4195372648325 -188.58006404538483 M186.95812765550917 -218.6757833205811 C181.0365122541273 -210.30456483507365, 177.9676132074455 -198.67550733911665, 173.7264363453357 -187.2385626990658"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4396"
            class="svg-elem-62"
          ></path>
        </g>
        <g id="g4404">
          <path
            d="M169.31807985566562 -189.36733901955918 C169.31807985566562 -189.36733901955918, 169.31807985566562 -189.36733901955918, 169.31807985566562 -189.36733901955918 M169.31807985566562 -189.36733901955918 C169.31807985566562 -189.36733901955918, 169.31807985566562 -189.36733901955918, 169.31807985566562 -189.36733901955918 M168.70182777260186 -181.56149330897858 C169.5326249399542 -183.72428069816473, 170.5176481965751 -184.73317931773505, 172.83146459091645 -188.1908230658168 M168.54646548216044 -182.2376997144283 C169.63495077249146 -183.25999554584067, 170.53114169564537 -184.72455032118444, 173.04663067943787 -187.14967284008213"
            stroke="black"
            stroke-width="0.5"
            fill="none"
            id="path4400"
            class="svg-elem-63"
          ></path>
          <path
            d="M175.70717259527956 -186.92793460600956 C174.3792877114038 -185.37188448735284, 171.97003734175433 -183.77978660288971, 168.47551640575645 -178.3123949077314 M175.46586912419983 -186.14310120654355 C172.30345832513132 -183.0871683195373, 170.5663455085416 -180.39072331727394, 168.48328604571435 -178.8306065603771 M167.84274975878628 -178.80898914725745 C168.62167553261332 -181.2284965042253, 167.7102718151754 -184.60949240748113, 168.40388051675492 -188.6021041173863 M168.56824511817902 -178.45433596128146 C168.6613401103658 -181.68248123943408, 169.23651555516975 -184.4842927515107, 169.49790658880374 -189.54217138728754 M169.28839547147615 -188.61495479966214 C171.10031733573996 -187.6412188050939, 173.724051669107 -186.3761476844942, 175.15527989743495 -186.34017928562076 M168.9919422749138 -189.2176485139552 C170.82317258661496 -188.9413813652624, 171.90170623746894 -188.32431359124155, 175.62688101268012 -186.1416498087856 M175.56 -186.3 C175.56 -186.3, 175.56 -186.3, 175.56 -186.3 M175.56 -186.3 C175.56 -186.3, 175.56 -186.3, 175.56 -186.3"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4402"
            class="svg-elem-64"
          ></path>
        </g>
      </g>
      <!-- athena -->
      <g id="node2" class="node">
        <title id="title4407">athena</title>
        <g id="g4413">
          <path
            d="M8.3882560295988 -121.23446063489746 C8.3882560295988 -121.23446063489746, 8.3882560295988 -121.23446063489746, 8.3882560295988 -121.23446063489746 M8.3882560295988 -121.23446063489746 C8.3882560295988 -121.23446063489746, 8.3882560295988 -121.23446063489746, 8.3882560295988 -121.23446063489746 M9.392805570887996 -115.31451342454865 C11.292089357834826 -118.33068693578305, 11.660564128909131 -119.5553047553191, 13.776122257482726 -121.64641731772367 M8.533479395205633 -115.36941703239224 C10.37522003032337 -118.11044784683685, 12.756373364650512 -120.11036602941392, 14.370301434602307 -121.80191549839309 M9.601128813589007 -110.59040267357258 C12.2608319431186 -111.63266934876937, 16.3056763064147 -118.09393151381182, 20.370411562121227 -121.39995761127112 M8.987690967458253 -108.62122725069457 C11.304427774184749 -112.82495632631164, 14.213793578230465 -116.44291887751324, 18.731775335218195 -121.40175359863925 M8.700062941833195 -103.30811593938282 C11.518204077960183 -107.33747528737193, 16.609910871018155 -114.68097021874877, 26.657939643576277 -121.40317199066175 M8.96972041434021 -102.04001987608356 C15.074603880225837 -109.64018922648357, 20.166179644490917 -118.33786459393586, 24.911948550326002 -122.24104857329634 M7.838400380713474 -98.81881346187008 C16.089712076595696 -106.68029131146123, 24.45260335483424 -112.55778543973406, 27.711327099171335 -119.46772156608708 M8.610567250115137 -96.69871359648411 C14.856292870695086 -103.77448216036456, 19.036574938848755 -109.31080923855836, 28.700492016362393 -121.23555620154251 M8.142798011839108 -90.2283489583627 C13.329512217875193 -96.91439902828704, 21.426562590981355 -104.31041342094748, 33.805755473144785 -120.04421741478261 M8.671099696778862 -90.86167811436289 C18.48399999558415 -102.39964731095962, 29.212045356355077 -114.35737711434564, 35.062405081961 -121.97003910118069 M9.012670144068935 -84.07546811228924 C17.00231064181956 -96.4358171410028, 24.851101555748258 -106.60818975431116, 40.578613335244874 -119.90075777089909 M9.072193190099078 -85.8185543690032 C19.53489150043155 -96.88867836427943, 27.2084994188162 -106.17213872371256, 40.53391463150075 -120.3663678309601 M15.14973557177801 -82.75568004659962 C26.10828252480948 -95.87355400900329, 36.586908427338116 -107.99998653467347, 43.932105008595414 -122.4980399777833 M13.025365301077162 -85.14541609339861 C24.65406491473793 -95.86982737631077, 33.51939802305019 -108.4232713074356, 44.713887908407585 -120.99778978396654 M21.224100676248938 -85.43244493453147 C31.31473413351114 -98.04685134821418, 42.18749068459165 -111.11115349996183, 52.583459775190505 -120.0395298163076 M19.456011027708204 -84.82556146079996 C27.40353600884646 -92.60429862215854, 33.94473447188313 -100.92888005684398, 51.34091186326605 -120.87347404429453 M25.181640979920914 -83.75244508096043 C33.23775134065311 -96.60896622159161, 44.538953814577724 -106.5738082108377, 56.52220914502899 -120.68592864250745 M24.76788100990616 -84.02957179021195 C34.697126804362696 -96.92732691970704, 46.457779940703865 -110.8976375416315, 56.43226465479415 -120.29251392694161 M28.32213769448364 -83.7263226594908 C38.88920816108837 -95.54488786746256, 49.031813477800455 -107.10246088688287, 58.45473414030607 -119.10998755978756 M30.277574684545637 -84.68763916827056 C37.750373234052674 -94.4555920223917, 45.41032766048205 -102.96885380347109, 60.681268880277266 -119.66040236663099 M34.90092302982204 -84.03339334882442 C43.93157182092726 -96.22604927570235, 57.116454279687616 -108.473096118361, 63.67677933861637 -116.791738957345 M35.95031099378833 -84.1950378804256 C41.631219591185754 -91.46460447893848, 48.43648104592681 -99.95939931374066, 62.742358752663264 -117.089090372523 M41.08598213261338 -85.01694779351251 C49.17863780770584 -93.77236708253163, 52.90393765722563 -102.67005905583068, 67.23052688335609 -112.33191625518573 M40.91934894939889 -85.04892790347934 C48.66230196686189 -94.98238601254143, 57.46027592760486 -104.80958198800025, 66.15451339942551 -113.33969611000967 M44.92093512624586 -86.50963626139075 C49.13683103366054 -91.61324936080506, 54.30185468270617 -94.48202914413311, 65.44435548775476 -109.51187854981562 M46.31462815826434 -84.72311319063047 C52.866792543485005 -91.81150679050329, 60.07390008389874 -101.27635318304016, 66.05182240580412 -107.4818384131693 M52.69144444530651 -86.84931231901453 C55.707973430500374 -90.76134624321676, 59.32010856345566 -92.63945883777296, 66.98785818837894 -100.14274148953359 M50.31492757172998 -85.44893156564618 C56.6867059138639 -91.18595348631658, 61.40614854170278 -97.67646104208285, 66.72096234603393 -101.80340608503091 M56.38153269842344 -84.48524647362157 C59.417301436304406 -89.0114224661285, 64.17119892313201 -92.63309908560669, 67.37593439449927 -96.95490342139344 M56.46170367646341 -84.32084102955896 C59.65146028929108 -88.27163971025108, 63.39225138572719 -93.01093496495146, 65.8343840752832 -96.50260641009703 M61.808301062560226 -85.08231219058776 C63.29314831258365 -87.48177001245205, 65.46110712178256 -89.24436318183405, 65.37962641990876 -89.8279052849946 M61.78240984043462 -85.27641498524193 C62.48208972146182 -86.36058532340053, 63.71387478001386 -87.44456643731455, 65.91850606351015 -89.60436022944785"
            stroke="none"
            stroke-width="0.5"
            fill="none"
            id="path4409"
            class="svg-elem-65"
          ></path>
          <path
            d="M57.043947820805876 -122.90171719418488 C42.161847541676245 -119.97059728457857, 22.891532875179568 -119.93376168984862, 8.022367916635593 -120.54586537203494 M58.43952989397856 -120.62541317999488 C43.41409658190646 -120.7727686254911, 29.75027403633935 -120.67280356663774, 8.11954828728547 -120.83112581399412 M7.93854505185325 -121.07986857964138 C8.553350862035963 -111.1634016147646, 7.241918323968601 -96.9928803455483, 7.9365023466387905 -87.12000330261748 M8.549909387444309 -121.36960866328201 C7.898488546081225 -108.61736398609864, 8.175925206558608 -94.69490392445395, 7.845811795734296 -86.09823677090385 M6.744630319088241 -86.91115004033408 C24.18595723550538 -86.01971771174628, 39.894926917535486 -84.52681589836682, 63.619912179026514 -84.23368523628574 M7.767008185959089 -85.90361070210473 C29.94864411098231 -84.84057162082927, 53.334548908441306 -86.28074941745788, 65.07885557417623 -84.4119324996136 M64.58055125242745 -87.15355446141778 C64.35036359622725 -95.4377304634742, 62.822219196328234 -102.30855041921988, 62.61702814092132 -115.12396296718609 M64.85715766517546 -86.22474263209804 C63.89614088596971 -93.41581879414042, 64.15621222140649 -101.29913556684869, 63.777411358808166 -115.77904572773107 M64.11521027065388 -114.66544452152856 C62.30323428547726 -117.23116185870678, 60.198938307923996 -119.48131701833329, 58.307390539525905 -122.17760458876596 M64.87080131519288 -115.71776093374018 C63.28300982716722 -116.9502172774497, 61.98757370869419 -118.13485035981144, 58.19342218543003 -121.70473277944801 M58.48 -121.34 C58.48 -121.34, 58.48 -121.34, 58.48 -121.34 M58.48 -121.34 C58.48 -121.34, 58.48 -121.34, 58.48 -121.34"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4411"
            class="svg-elem-66"
          ></path>
        </g>
        <g id="g4417">
          <path
            d="M58.707276921844475 -120.8463758174568 C58.019085520517066 -119.40819701295675, 58.86195987490963 -118.20050718092186, 58.02450862992275 -114.95918160906851 M58.56794261904662 -121.6267354572457 C58.41160154841814 -119.88526747063875, 58.30119913979696 -118.42199198316362, 58.34888075342402 -115.17475676087403"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4415"
            class="svg-elem-67"
          ></path>
        </g>
        <g id="g4421">
          <path
            d="M64.86717329975193 -115.70124070274352 C63.22952323748985 -114.8134735835879, 61.78246375094706 -115.27222405311556, 58.88907380676274 -114.76800446096655 M64.1837629811468 -115.27798837929139 C62.15236731351196 -115.39337599755473, 60.20484520508478 -115.43283998837984, 58.63792273153193 -115.55334898284951"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4419"
            class="svg-elem-68"
          ></path>
        </g>
        <g
          aria-label="Athena"
          id="text4423"
          style="
            font-size: 14px;
            font-family: Tinos, serif;
            text-anchor: middle;
          "
        >
          <path
            d="m 19.4175,-100.0023 v 0.362301 h -3.014649 v -0.362301 l 1.039063,-0.18457 3.124023,-8.69532 h 1.298828 l 3.24707,8.69532 1.16211,0.18457 v 0.362301 h -3.875977 v -0.362301 l 1.230469,-0.18457 -0.90918,-2.64551 h -3.609375 l -0.922851,2.64551 z m 1.469726,-7.89551 -1.572266,4.45019 h 3.192383 z"
            id="path4638"
            class="svg-elem-69"
          ></path>
          <path
            d="m 28.659687,-99.503281 q -0.65625,0 -0.984375,-0.389648 -0.321289,-0.389651 -0.321289,-1.093751 v -4.50488 h -0.84082 v -0.30762 l 0.854492,-0.2666 0.69043,-1.45606 h 0.430664 v 1.45606 h 1.469726 v 0.57422 h -1.469726 v 4.38183 q 0,0.44434 0.198242,0.66993 0.205078,0.22558 0.533203,0.22558 0.396484,0 0.963867,-0.10937 v 0.444333 q -0.239258,0.164062 -0.69043,0.266601 -0.451171,0.109375 -0.833984,0.109375 z"
            id="path4640"
            class="svg-elem-70"
          ></path>
          <path
            d="m 32.494648,-106.57164 q 0,0.71094 -0.04785,1.02539 0.492188,-0.28027 1.114258,-0.48535 0.628906,-0.20508 1.059571,-0.20508 0.833984,0 1.257812,0.48535 0.423828,0.48535 0.423828,1.40821 v 4.2246 l 0.779297,0.170903 v 0.307618 h -2.768555 v -0.307618 l 0.854493,-0.170903 v -4.14257 q 0,-1.17578 -1.134766,-1.17578 -0.642578,0 -1.538086,0.19824 v 5.12011 l 0.868164,0.170903 v 0.307618 h -2.816406 v -0.307618 l 0.813476,-0.170903 v -8.76367 l -0.957031,-0.16406 v -0.30762 h 2.091797 z"
            id="path4642"
            class="svg-elem-71"
          ></path>
          <path
            d="m 39.043476,-102.8734 v 0.12305 q 0,0.94336 0.205078,1.46973 0.211914,0.51953 0.642578,0.79296 0.4375,0.27344 1.141602,0.27344 0.369141,0 0.875,-0.0615 0.505859,-0.0615 0.833984,-0.13672 v 0.38281 q -0.328125,0.211916 -0.895508,0.369143 -0.560546,0.157226 -1.148437,0.157226 -1.49707,0 -2.194336,-0.806639 -0.69043,-0.80664 -0.69043,-2.59082 0,-1.68164 0.704102,-2.50879 0.704101,-0.82715 2.009766,-0.82715 2.467773,0 2.467773,2.80274 v 0.56054 z m 1.483399,-2.8164 q -0.710938,0 -1.09375,0.57421 -0.375977,0.57422 -0.375977,1.69532 h 2.748047 q 0,-1.22364 -0.314453,-1.74317 -0.314453,-0.52636 -0.963867,-0.52636 z"
            id="path4644"
            class="svg-elem-72"
          ></path>
          <path
            d="m 45.694843,-105.54625 q 0.526367,-0.30078 1.121094,-0.49219 0.594727,-0.19824 0.991211,-0.19824 0.833984,0 1.257812,0.48535 0.423829,0.48535 0.423829,1.40821 v 4.2246 l 0.779296,0.170903 v 0.307618 h -2.768554 v -0.307618 l 0.854492,-0.170903 v -4.10156 q 0,-0.56738 -0.280273,-0.88867 -0.273438,-0.32812 -0.854493,-0.32812 -0.615234,0 -1.510742,0.19824 v 5.12011 l 0.868164,0.170903 v 0.307618 h -2.77539 v -0.307618 l 0.772461,-0.170903 v -5.46875 l -0.772461,-0.17089 v -0.30762 h 1.832031 z"
            id="path4646"
            class="svg-elem-73"
          ></path>
          <path
            d="m 53.65871,-106.20934 q 1.052735,0 1.544922,0.43067 0.499024,0.43066 0.499024,1.31933 v 4.34082 l 0.799804,0.170903 v 0.307618 h -1.763671 l -0.129883,-0.642581 q -0.779297,0.779299 -1.989258,0.779299 -1.647461,0 -1.647461,-1.914059 0,-0.64258 0.246094,-1.05957 0.252929,-0.42383 0.799804,-0.64258 0.546875,-0.22559 1.585938,-0.2461 l 0.963867,-0.0273 v -1.00488 q 0,-0.66309 -0.246094,-0.97754 -0.239257,-0.31445 -0.745117,-0.31445 -0.683594,0 -1.250976,0.32128 l -0.232422,0.79981 h -0.382813 v -1.40137 q 1.107422,-0.23926 1.948242,-0.23926 z m 0.90918,3.29493 -0.895508,0.0273 q -0.916015,0.0342 -1.24414,0.35547 -0.321289,0.32129 -0.321289,1.07324 0,1.20313 0.977539,1.20313 0.464843,0 0.799804,-0.10254 0.341797,-0.10938 0.683594,-0.27344 z"
            id="path4648"
            class="svg-elem-74"
          ></path>
        </g>
      </g>
      <!-- athena&#45;&gt;game_loop -->
      <g id="edge2" class="edge">
        <title id="title4426">athena-&gt;game_loop</title>
        <g id="g4430">
          <path
            d="M64.52 -116.39 C79.78735421209116 -124.85534975804563, 101.23101059210384 -132.75427279179266, 121.68938733036886 -140.58986791521536 M65.08928264646971 -117.67461537886973 C81.87393598957617 -125.46217447517202, 100.77554335550762 -134.4536140386907, 118.97931814742695 -144.24824528640266"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4428"
            class="svg-elem-75"
          ></path>
        </g>
        <g id="g4436">
          <path
            d="M118.86614307176737 -145.773681001923 C118.86614307176737 -145.773681001923, 118.86614307176737 -145.773681001923, 118.86614307176737 -145.773681001923 M118.86614307176737 -145.773681001923 C118.86614307176737 -145.773681001923, 118.86614307176737 -145.773681001923, 118.86614307176737 -145.773681001923 M120.11282840766367 -141.0887378819033 C122.40787269337977 -143.08176250373077, 123.25606653923874 -144.62128379061346, 124.59851104888415 -146.6841260290199 M120.4962991232504 -141.36108007296585 C121.55731447561682 -142.4925358342944, 122.27631657568986 -143.23697779994626, 124.77927372708218 -146.10864049315285"
            stroke="black"
            stroke-width="0.5"
            fill="none"
            id="path4432"
            class="svg-elem-76"
          ></path>
          <path
            d="M118.62396455726888 -144.96476381568243 C121.82001766228683 -145.33912010424362, 124.06854261048309 -146.12513540830298, 129.35648593459777 -146.09774731059724 M118.07107769084523 -145.32452809684247 C121.51677129940863 -145.73504048933407, 125.58410278064285 -146.2206064386536, 128.72461981132966 -146.62439869988887 M129.3372157334073 -146.8301710456434 C126.29535962834191 -143.17481704271313, 124.13608060705158 -141.88314816448928, 121.85667961065019 -139.01149178168913 M128.70515661047463 -146.16892239715386 C126.9405859434999 -144.23182333795748, 123.78302577631706 -141.72000749310715, 121.74442114311002 -139.57046215464592 M121.1242405171525 -139.4779774890771 C120.78019026186342 -140.5211182225917, 119.3882095499806 -142.31487138680765, 118.9804538067662 -144.77960442715687 M121.7478281596108 -138.72796434052503 C121.25966935402916 -140.62173965042382, 120.53648427555623 -141.6409258325641, 118.65669453018512 -145.70168918254646 M118.55 -145.41 C118.55 -145.41, 118.55 -145.41, 118.55 -145.41 M118.55 -145.41 C118.55 -145.41, 118.55 -145.41, 118.55 -145.41"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4434"
            class="svg-elem-77"
          ></path>
        </g>
      </g>
      <!-- agents -->
      <g id="node4" class="node">
        <title id="title4439">agents</title>
        <g id="g4445">
          <path
            d="M201.27495280964962 -80.76186058430531 C201.27495280964962 -80.76186058430531, 201.27495280964962 -80.76186058430531, 201.27495280964962 -80.76186058430531 M201.27495280964962 -80.76186058430531 C201.27495280964962 -80.76186058430531, 201.27495280964962 -80.76186058430531, 201.27495280964962 -80.76186058430531 M199.4276474249643 -72.7716954412222 C203.44819506506337 -76.68391100119534, 208.2646283338816 -80.38728348709803, 210.1316381329482 -83.8908500224325 M199.52193268874453 -73.17380836638567 C203.73564702548364 -76.97803137320288, 208.0448529280895 -81.99314912732974, 210.49456778365072 -84.62415867768836 M198.44790364162387 -66.77591083856088 C207.07486759194552 -72.63635411037535, 210.66082239446527 -80.473730395835, 217.57310296826287 -88.76220746082761 M199.28615171275285 -65.5622362872691 C204.40362848982147 -72.97444113639432, 209.7756178304937 -78.51739470313213, 218.91131215861523 -88.88208105245687 M202.63495325805704 -62.009625550239655 C209.46608642231388 -68.82912991521576, 212.23430634598975 -77.53582446841241, 225.96096730529206 -89.52431218901677 M201.89832285681445 -63.55876695534076 C211.51660070294844 -73.74445582151843, 219.387379650854 -83.32026785322881, 224.403376593733 -88.34394840448883 M204.16901583295257 -62.93015461626011 C213.08945841099046 -68.6098303819954, 219.471539667409 -77.41593123144096, 230.83941447586523 -87.45379566982713 M206.99438355172924 -61.86631534283025 C215.4889894584526 -71.95875364143494, 224.0380806180592 -80.9059142510819, 229.32728160749528 -89.9392984829485 M209.36573450099655 -57.81240921679166 C217.43741691594585 -68.24641458101495, 224.32382814988148 -74.57716347666171, 236.9061098613598 -90.47985379610782 M209.09770557679025 -60.063008421491546 C217.88656740396758 -70.1261919960178, 226.64233146667846 -79.82318802126149, 234.96760937522558 -89.59916201722777 M210.77223838572093 -55.196778167748626 C218.2136047894797 -62.31555415801931, 223.22848728792331 -68.8842765345256, 241.82680316269585 -90.59095314972515 M213.0357335578401 -57.67208523966147 C222.75391990129953 -68.55761203064074, 232.9880776737408 -81.76640962096984, 240.1107376056979 -90.81974953486404 M215.97207529792655 -55.41886446428586 C225.68518070174537 -68.5460504839185, 236.2644949179323 -80.6366361356598, 243.73362937608687 -86.38753215791206 M217.73966758751203 -55.83384486910907 C228.40217867630514 -68.34931032178682, 238.67319748456146 -81.33846505920815, 243.4096656218636 -87.3745248187979 M219.66317270092398 -53.916625862850026 C227.16050635460064 -60.33342903963087, 232.85692842912903 -68.46646294728453, 248.33042883782824 -86.43302849136832 M221.19388358185955 -55.95230702553891 C229.37626246265012 -65.61628300812082, 238.3999547582681 -75.86939081588625, 247.54561696714683 -86.17581758920464 M224.49061828841883 -56.870420156065414 C234.87188898587996 -65.19473227366156, 242.56319856042623 -76.33487247596192, 253.0792665496291 -85.995033343542 M226.23026896763173 -55.84683107745153 C233.4572491129037 -62.2671710644504, 239.58689382187856 -70.73849269163861, 251.35104474581422 -84.7841459554688 M232.41188772089927 -52.7846928971212 C237.57469033893116 -62.828780625597425, 243.86920486863815 -71.35066297125947, 255.66288150631968 -81.46157077954045 M232.3290058315011 -54.4247672087928 C238.2840894710898 -60.80951041195505, 243.9848738414279 -68.65398496686021, 256.5680500858419 -83.47218219141035 M235.4890514443841 -55.09222979430642 C240.86006250508794 -59.37201077864962, 247.02727313168504 -67.19641095175889, 258.9736505675874 -81.00110946585438 M236.451781301908 -53.645559976590185 C240.2773254211165 -58.8944244788862, 246.73325350497552 -66.91818582454265, 260.3180902548286 -81.68091791152345 M237.85786121240758 -52.542709507525984 C246.84411453485245 -60.99265852324433, 255.0545358916976 -67.29873871087773, 264.43454035443466 -79.96896804768468 M239.20897524823502 -50.90806218047764 C248.2246987080192 -59.78273587081233, 254.6393917683155 -68.81474558875836, 264.4866834261252 -79.22519696079868 M246.7917279828065 -51.61699815751911 C250.93156951407713 -57.74460647228592, 254.52704886431115 -63.91063917465773, 266.7386328156332 -75.60297708905308 M244.88260657303272 -53.144723031015516 C251.26173183792847 -59.18434082482174, 257.4497746474877 -64.67010379307789, 265.9617597457619 -76.06021385433671 M251.88493976856194 -55.87168983763161 C256.0877356843114 -60.69981052825702, 261.42207027195695 -66.01679305031342, 268.9771850078111 -74.59941826115448 M253.68380954227243 -54.5441758646047 C258.77232932820203 -62.046849572002884, 265.3927204564526 -69.16481719080512, 267.9706489541147 -73.00483867886848"
            stroke="none"
            stroke-width="0.5"
            fill="none"
            id="path4441"
            class="svg-elem-78"
          ></path>
          <path
            d="M217.99486968864483 -88.376044270121 C224.29305251925433 -90.16598861875624, 234.28091063326917 -91.05987136498253, 241.54695817043196 -90.03488588582738 C248.81300570759475 -89.00990040667223, 257.20102989300307 -85.52231704181732, 261.5911549116216 -82.22613139519012 C265.9812799302401 -78.92994574856293, 268.670287410408 -74.21180298679405, 267.88770828214285 -70.25777200606422 C267.1051291538777 -66.30374102533438, 262.1548748183772 -61.27393057821499, 256.89568014203076 -58.50194551081104 C251.6364854656843 -55.729960443407094, 243.7945970440139 -53.84546321034809, 236.33254022406405 -53.62586160164053 C228.8704834041142 -53.406259992932966, 218.37011562813845 -54.96942948039431, 212.12333922233162 -57.184335858565646 C205.8765628165248 -59.39924223673698, 200.69031890792604 -63.02065222998432, 198.85188178922314 -66.91529987066855 C197.01344467052024 -70.80994751135277, 197.2538166756147 -76.61951005664415, 201.09271651011426 -80.552221702671 C204.93161634461381 -84.48493334869787, 217.26071177223596 -89.04797052007868, 221.88528079622048 -90.51156974682971 C226.509849820205 -91.97516897358074, 228.44293878828978 -89.90412646076169, 228.84013065402132 -89.33381706317715 M247.04422676366656 -87.73149232307733 C253.750796275398 -86.65871091203707, 259.79247245625345 -84.18915454376763, 263.2992144585226 -80.84328756123925 C266.8059564607918 -77.49742057871087, 269.44699166235364 -71.23149409112344, 268.0846787772816 -67.65629042790704 C266.7223658922096 -64.08108676469064, 260.98237892282174 -61.805491305161546, 255.12533714809052 -59.39206558194087 C249.2682953733593 -56.97863985872019, 240.58029604008243 -53.13011552923552, 232.9424281288944 -53.175736088582994 C225.30456021770635 -53.22135664793047, 215.09911290459158 -56.79377741258443, 209.2981296809623 -59.66578893802574 C203.497146457333 -62.53780046346705, 199.43110424543977 -66.9049998483564, 198.13652878711872 -70.40780524123085 C196.84195332879767 -73.9106106341053, 197.88549364842564 -77.30585514017706, 201.53067693103594 -80.68262129527243 C205.17586021364625 -84.0593874503678, 212.51348497860474 -89.42342758317051, 220.0076284827806 -90.66840217180304 C227.50177198695647 -91.91337676043557, 242.1869800297139 -88.66509230219201, 246.4955379560912 -88.15246882706762 C250.8040958824685 -87.63984535194324, 246.35040108372104 -87.62146514391793, 245.85897604104431 -87.5926613210567"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4443"
            class="svg-elem-79"
          ></path>
        </g>
        <g
          aria-label="Agents"
          id="text4447"
          style="
            font-size: 14px;
            font-family: Tinos, serif;
            text-anchor: middle;
          "
        >
          <path
            d="m 216.09032,-68.822304 v 0.362305 h -3.01465 v -0.362305 l 1.03906,-0.18457 3.12402,-8.695313 h 1.29883 l 3.24707,8.695313 1.16211,0.18457 v 0.362305 h -3.87597 v -0.362305 l 1.23046,-0.18457 -0.90918,-2.645508 h -3.60937 l -0.92285,2.645508 z m 1.46972,-7.895508 -1.57226,4.450196 h 3.19238 z"
            id="path4651"
            class="svg-elem-80"
          ></path>
          <path
            d="m 228.99657,-72.855507 q 0,1.107422 -0.66309,1.674805 -0.66309,0.567383 -1.90723,0.567383 -0.56054,0 -1.03906,-0.102539 l -0.43066,0.895507 q 0.0205,0.116211 0.2666,0.21875 0.24609,0.102539 0.61523,0.102539 h 1.90039 q 1.03907,0 1.53809,0.451172 0.50586,0.451172 0.50586,1.244141 0,0.717773 -0.40332,1.250976 -0.39649,0.533204 -1.16895,0.820313 -0.77246,0.293945 -1.87304,0.293945 -1.3125,0 -2.00293,-0.40332 -0.6836,-0.40332 -0.6836,-1.148438 0,-0.362304 0.2461,-0.717773 0.24609,-0.348633 0.90234,-0.820312 -0.38965,-0.129883 -0.65625,-0.444336 -0.2666,-0.314454 -0.2666,-0.676758 l 1.08008,-1.216797 q -1.08008,-0.505859 -1.08008,-1.989258 0,-1.052734 0.66309,-1.626953 0.66992,-0.574219 1.9414,-0.574219 0.25293,0 0.64942,0.05469 0.39648,0.04785 0.60839,0.116211 l 1.51075,-0.758789 0.23925,0.293945 -0.95019,0.984375 q 0.45801,0.512695 0.45801,1.510742 z m -0.28028,5.263672 q 0,-0.389648 -0.23925,-0.608398 -0.23926,-0.21875 -0.72461,-0.21875 h -2.48829 q -0.2871,0.246093 -0.47167,0.62207 -0.17774,0.382812 -0.17774,0.710937 0,0.587891 0.42383,0.840821 0.42383,0.259765 1.29883,0.259765 1.1416,0 1.75683,-0.423828 0.62207,-0.423828 0.62207,-1.182617 z m -2.27636,-3.541016 q 0.74511,0 1.05273,-0.423828 0.31445,-0.430664 0.31445,-1.298828 0,-0.90918 -0.32129,-1.291992 -0.32128,-0.389649 -1.03222,-0.389649 -0.71778,0 -1.05274,0.389649 -0.33496,0.389648 -0.33496,1.291992 0,0.902344 0.32813,1.3125 0.32812,0.410156 1.0459,0.410156 z"
            id="path4653"
            class="svg-elem-81"
          ></path>
          <path
            d="m 231.82664,-71.693398 v 0.123047 q 0,0.94336 0.20508,1.469727 0.21192,0.519531 0.64258,0.792969 0.4375,0.273437 1.1416,0.273437 0.36914,0 0.875,-0.06152 0.50586,-0.06152 0.83399,-0.136719 v 0.382812 q -0.32813,0.211915 -0.89551,0.369141 -0.56055,0.157227 -1.14844,0.157227 -1.49707,0 -2.19433,-0.806641 -0.69043,-0.806641 -0.69043,-2.59082 0,-1.681641 0.7041,-2.508789 0.7041,-0.827149 2.00976,-0.827149 2.46778,0 2.46778,2.802735 v 0.560546 z m 1.4834,-2.816406 q -0.71093,0 -1.09375,0.574219 -0.37597,0.574219 -0.37597,1.695312 h 2.74804 q 0,-1.223632 -0.31445,-1.743164 -0.31445,-0.526367 -0.96387,-0.526367 z"
            id="path4655"
            class="svg-elem-82"
          ></path>
          <path
            d="m 238.47801,-74.366249 q 0.52637,-0.300781 1.1211,-0.492188 0.59472,-0.198242 0.99121,-0.198242 0.83398,0 1.25781,0.485352 0.42383,0.485351 0.42383,1.408203 v 4.224609 l 0.77929,0.170899 v 0.307617 h -2.76855 v -0.307617 l 0.85449,-0.170899 v -4.101562 q 0,-0.567383 -0.28027,-0.888672 -0.27344,-0.328125 -0.85449,-0.328125 -0.61524,0 -1.51075,0.198242 v 5.120117 l 0.86817,0.170899 v 0.307617 h -2.77539 v -0.307617 l 0.77246,-0.170899 v -5.46875 l -0.77246,-0.170898 v -0.307617 h 1.83203 z"
            id="path4657"
            class="svg-elem-83"
          ></path>
          <path
            d="m 245.54637,-68.32328 q -0.65625,0 -0.98437,-0.389649 -0.32129,-0.389648 -0.32129,-1.09375 v -4.504883 h -0.84082 v -0.307617 l 0.85449,-0.266601 0.69043,-1.456055 h 0.43066 v 1.456055 h 1.46973 v 0.574218 h -1.46973 v 4.381836 q 0,0.444336 0.19825,0.669922 0.20507,0.225586 0.5332,0.225586 0.39648,0 0.96387,-0.109375 v 0.444336 q -0.23926,0.164063 -0.69043,0.266602 -0.45118,0.109375 -0.83399,0.109375 z"
            id="path4659"
            class="svg-elem-84"
          ></path>
          <path
            d="m 252.0952,-70.264687 q 0,0.957032 -0.6084,1.449219 -0.60156,0.492188 -1.78418,0.492188 -0.47851,0 -1.05957,-0.102539 -0.57422,-0.0957 -0.90234,-0.21875 v -1.579102 h 0.30761 l 0.33497,0.895508 q 0.51269,0.464844 1.333,0.464844 1.32618,0 1.32618,-1.134766 0,-0.833984 -1.0459,-1.189453 l -0.6084,-0.198242 q -0.69043,-0.225586 -1.00488,-0.458008 -0.31446,-0.232422 -0.48536,-0.567383 -0.17089,-0.341797 -0.17089,-0.820312 0,-0.847657 0.57421,-1.333008 0.58106,-0.492188 1.56543,-0.492188 0.70411,0 1.76368,0.211914 v 1.401367 h -0.32129 l -0.28711,-0.745117 q -0.36231,-0.321289 -1.1416,-0.321289 -0.55372,0 -0.84766,0.273438 -0.28711,0.273437 -0.28711,0.738281 0,0.389648 0.25977,0.65625 0.2666,0.266602 0.7998,0.444336 1.00488,0.341797 1.3125,0.499023 0.30762,0.157227 0.51953,0.389649 0.21875,0.225586 0.33496,0.519531 0.12305,0.293945 0.12305,0.724609 z"
            id="path4661"
            class="svg-elem-85"
          ></path>
        </g>
      </g>
      <!-- game_loop&#45;&gt;agents -->
      <g id="edge3" class="edge">
        <title id="title4450">game_loop-&gt;agents</title>
        <g id="g4454">
          <path
            d="M174.42 -143.35 C183.97360213275516 -129.07420577916557, 202.28063548300233 -113.01272453888274, 212.39620401121235 -97.4098156449983 M176.17661522820296 -143.2044076103378 C183.73581075765193 -129.58339489558787, 199.31737371844608 -111.599219546581, 212.57801309451511 -97.65955856323195"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4452"
            class="svg-elem-86"
          ></path>
        </g>
        <g id="g4460">
          <path
            d="M209.84128798366385 -94.51546691942707 C209.84128798366385 -94.51546691942707, 209.84128798366385 -94.51546691942707, 209.84128798366385 -94.51546691942707 M209.84128798366385 -94.51546691942707 C209.84128798366385 -94.51546691942707, 209.84128798366385 -94.51546691942707, 209.84128798366385 -94.51546691942707 M213.18459883093468 -92.36976973915077 C215.10506974609234 -94.73843419410723, 216.67954096652684 -95.7227003283178, 216.93487832155887 -96.723836035059 M213.28517560371674 -92.88200648578841 C214.9101280162389 -94.50339049445401, 216.29633944959588 -95.95940695229018, 217.72045401720518 -96.87481902255423 M216.81076392273883 -90.01715701346914 C217.24095158483632 -91.17906661322095, 218.15096928224216 -92.11614237971534, 219.02597714949903 -93.2304078469985 M216.53437347099307 -89.97394663038175 C217.53205520988817 -91.07528653358688, 218.27497405436236 -92.02615438495486, 219.06350222376375 -93.14473277842647"
            stroke="black"
            stroke-width="0.5"
            fill="none"
            id="path4456"
            class="svg-elem-87"
          ></path>
          <path
            d="M215.49450385512577 -99.93209451932871 C216.19322839485739 -96.79471825164356, 216.60592952925145 -93.91482244769273, 218.189877552468 -88.31447625598302 M215.37360361966597 -99.06713634705577 C216.586712413776 -95.30793611833785, 217.60721544788487 -92.51002057126131, 218.94494374725434 -88.75493090737162 M218.0506334110048 -89.94811544831953 C215.63551537629363 -90.45290308939171, 213.09158926861988 -93.33551552901721, 210.67178091904296 -93.87416368080092 M219.07290729294402 -88.74670665554335 C215.80754201244156 -90.37259062046223, 212.82380728195835 -92.21736298165288, 209.61915856763204 -94.43852417810191 M209.67193127290466 -94.9026545304119 C212.01563377454426 -95.95080806829193, 213.81770903594608 -97.49213665904867, 214.99724462256503 -98.85775430559214 M210.1869281722472 -94.45846989028472 C211.27693441303316 -95.78397830787661, 213.52443776333752 -97.08373638214061, 215.61419326729475 -98.98381007114529 M215.3 -99 C215.3 -99, 215.3 -99, 215.3 -99 M215.3 -99 C215.3 -99, 215.3 -99, 215.3 -99"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4458"
            class="svg-elem-88"
          ></path>
        </g>
      </g>
      <!-- tasks -->
      <g id="node5" class="node">
        <title id="title4463">tasks</title>
        <g id="g4469">
          <path
            d="M278.44607603215314 -37.52826050487978 C278.44607603215314 -37.52826050487978, 278.44607603215314 -37.52826050487978, 278.44607603215314 -37.52826050487978 M278.44607603215314 -37.52826050487978 C278.44607603215314 -37.52826050487978, 278.44607603215314 -37.52826050487978, 278.44607603215314 -37.52826050487978 M273.2871230517994 -27.427452426130923 C278.22325096703156 -31.046910786404187, 281.02602322662665 -31.49574068091566, 285.0545461766785 -39.313415129585266 M274.0958987144865 -26.738840918987076 C277.03957872514604 -30.07869391487789, 278.45431753333713 -31.912885555188712, 286.95119332211914 -40.398612346979256 M276.71343595636046 -22.538599802325336 C283.52762860204206 -28.858811884334525, 288.38750536949493 -36.887284603456784, 294.0616745997349 -43.90552970439101 M275.353249730254 -21.85196009514716 C280.95457899284884 -28.258991168517326, 286.6890742579471 -34.981719944500774, 293.7909735878864 -42.92456838345083 M277.80904969861444 -16.444605075083377 C281.3680819846565 -26.092799405371192, 287.6602713027984 -29.92528506787729, 299.4161543704028 -44.5939814138481 M277.03439628929317 -18.27402505461579 C282.5878128803228 -23.579651023082086, 288.5831585442637 -30.902252726722665, 300.4710411426061 -43.23060932409796 M277.8436682882756 -16.086074816529127 C285.26281787310995 -21.87909315569379, 292.38006346930007 -27.56064631092318, 304.50803704473697 -42.440760578311384 M280.0768465654644 -13.268473214764843 C288.43671220981753 -24.640393324820455, 297.89871271460424 -37.33334488858034, 304.36803525430446 -43.8554658784386 M282.14251600644843 -12.376776033749191 C294.7542383690099 -25.035486231454556, 304.7223811481029 -37.2483463613686, 309.3206708916985 -41.35142870975951 M282.0277734321658 -12.573374774455308 C288.540555406815 -19.23908030004309, 295.8046125838028 -26.278638357994485, 310.6158524549717 -43.58626588928849 M288.67904121185444 -10.548448280989938 C295.8032103508195 -16.95169694622411, 299.85152175211965 -25.31925314808158, 313.39183040679734 -42.26246058042856 M287.6087071805892 -10.675642362149429 C293.6385733637731 -18.541557923539447, 299.48567685227425 -27.193619755447852, 314.38229196020507 -42.46779485366891 M289.27399056191655 -10.244650754224725 C298.0030337889601 -17.145642458266163, 305.1528424567334 -27.028588286167285, 318.8604184459849 -42.03430751315703 M291.7449683303871 -9.944054395767585 C301.0764537689815 -21.05529853475815, 309.49419537278385 -31.96667500251099, 320.28681165354453 -43.273565739889655 M294.9750285234733 -8.642644280489307 C304.02540237008986 -21.75807918372562, 316.57502665517507 -31.365580139211822, 325.02710379971586 -41.73775516673149 M294.41275033827645 -8.917692756488561 C304.13063421632944 -19.274054544341002, 312.6121788078537 -29.37887518050102, 323.55791412422724 -40.51379614992259 M298.6366811917228 -7.973710129405299 C309.3227568942009 -17.099337559338363, 315.8897263918168 -25.015595915033188, 326.5275167224768 -39.94724574825938 M300.3217896094141 -6.839708893834402 C307.4153000030274 -15.878905826407465, 315.77749471785097 -25.4747255519701, 327.56975764865234 -38.52007308445414 M306.4413077043181 -6.500007004094877 C309.56206714589774 -12.742017938192525, 317.2199999022562 -19.81476167128025, 329.7417365124802 -36.57268938563206 M306.2839405572222 -7.240336544977383 C312.82170991709455 -15.970707810441604, 319.6272691793225 -23.957942816365623, 329.58062436551415 -35.54541195488313 M312.2821906413169 -8.786205878356974 C318.60881549047826 -15.326096749280685, 324.90438482018527 -23.708583423714764, 334.040047079626 -33.51320195733952 M311.4495373322114 -9.013264307246557 C317.72120537495476 -13.958538650471542, 322.26433360444764 -21.14356163352744, 334.8308782905708 -34.3871397003816 M316.838702806599 -10.649723636931967 C325.51531797670606 -14.770974721246798, 330.53454579079437 -24.115019902177476, 333.2438063681443 -28.474642579596985 M317.2683101948422 -10.572077101428818 C322.88176082855637 -13.46985885395656, 326.8205127945859 -18.56043471042713, 333.5734171743722 -28.929789821929944 M327.0612193448411 -13.278542233789866 C328.4685884038625 -14.76789384174303, 331.66947554402867 -19.133596512560437, 333.92271078715316 -21.847414023007012 M325.9084442075871 -13.703534683417056 C328.6011200188125 -15.286702707759083, 330.78401960388953 -17.80583117635558, 335.2165924668589 -23.403747578938077"
            stroke="none"
            stroke-width="0.5"
            fill="none"
            id="path4465"
            class="svg-elem-89"
          ></path>
          <path
            d="M296.84412569264214 -44.32410228185042 C303.0708239328884 -45.612513780492165, 312.48856195606277 -44.889572631207045, 318.6491381875211 -43.2339621448629 C324.8097144189794 -41.578351658518756, 331.10587298103496 -38.18036012763123, 333.80758308139224 -34.39043936378556 C336.5092931817495 -30.600518599939893, 336.7988091543332 -24.38398058230231, 334.85939878966485 -20.49443756178889 C332.9199884249965 -16.604894541275467, 327.9092315391172 -13.25106009314709, 322.17112089338207 -11.053181240705024 C316.43301024764696 -8.855302388262958, 307.26016882272796 -7.161070784220605, 300.43073491525405 -7.30716444713649 C293.60130100778014 -7.453258110052374, 285.72332772156415 -9.062218806138079, 281.1945174485386 -11.929743218200333 C276.66570717551303 -14.797267630262587, 273.69569843073987 -20.222598233945234, 273.25787327710077 -24.512310919510014 C272.8200481234617 -28.802023605074794, 273.8585502656582 -34.31452706687892, 278.5675665267042 -37.66801933158901 C283.27658278775016 -41.0215115962991, 296.9812905257966 -43.47473806502773, 301.51197084337673 -44.63326450777055 C306.04265116095684 -45.79179095051337, 305.7425231716938 -45.08086195454371, 305.7516484321848 -44.61917798804592 M291.58973633036226 -41.5734137899269 C297.43765571003627 -42.96423504399209, 305.836543689992 -43.76931345311779, 312.51461085998505 -42.824991240501966 C319.1926780299781 -41.88066902788614, 327.80702894702773 -39.220635307867596, 331.6581393503205 -35.90748051423196 C335.50924975361323 -32.59432572059633, 336.65646321568727 -26.743274791442058, 335.6212732797417 -22.946062478688162 C334.5860833437961 -19.148850165934267, 330.26701383683667 -15.703426357205627, 325.4469997346469 -13.12420663770859 C320.62698563245715 -10.544986918211555, 313.289947962898 -7.895408168222424, 306.70118866660323 -7.4707441617059445 C300.11242937030846 -7.046080155189465, 291.73017318341783 -8.459356189601506, 285.9144439568783 -10.57622259860971 C280.09871473033877 -12.693089007617916, 273.3281802575723 -16.445059954833788, 271.8068133073659 -20.17194261575517 C270.28544635715957 -23.898825276676554, 273.52427752331437 -29.050337492306287, 276.78624225564033 -32.93751856413801 C280.0482069879663 -36.82469963596973, 288.73870822664765 -42.06202990917581, 291.3786017013218 -43.4950290467455 C294.018495175996 -44.92802818431519, 292.58479852430787 -41.73678375342437, 292.62560310368536 -41.535513389556144"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4467"
            class="svg-elem-90"
          ></path>
        </g>
        <g
          aria-label="Tasks"
          id="text4471"
          style="
            font-size: 14px;
            font-family: Tinos, serif;
            text-anchor: middle;
          "
        >
          <path
            d="m 290.67102,-22.110001 v -0.362304 l 1.45606,-0.184571 v -8.032226 h -0.34864 q -1.72949,0 -2.36523,0.136719 l -0.18457,1.428711 h -0.45801 v -2.153321 h 8.06641 v 2.153321 h -0.46485 l -0.18457,-1.428711 q -0.20508,-0.04785 -0.89551,-0.08203 -0.69043,-0.04101 -1.51074,-0.04101 h -0.33496 v 8.018554 l 1.45606,0.184571 v 0.362304 z"
            id="path4664"
            class="svg-elem-91"
          ></path>
          <path
            d="m 299.27063,-28.679337 q 1.05273,0 1.54492,0.430665 0.49903,0.430664 0.49903,1.319335 v 4.340821 l 0.7998,0.170898 v 0.307617 h -1.76367 l -0.12988,-0.642578 q -0.7793,0.779297 -1.98926,0.779297 -1.64746,0 -1.64746,-1.914062 0,-0.642578 0.24609,-1.059571 0.25293,-0.423828 0.7998,-0.642578 0.54688,-0.225586 1.58594,-0.246094 l 0.96387,-0.02734 v -1.004883 q 0,-0.663086 -0.24609,-0.977539 -0.23926,-0.314453 -0.74512,-0.314453 -0.6836,0 -1.25098,0.321289 l -0.23242,0.799804 h -0.38281 v -1.401367 q 1.10742,-0.239258 1.94824,-0.239258 z m 0.90918,3.294922 -0.89551,0.02734 q -0.91601,0.03418 -1.24414,0.355469 -0.32129,0.321289 -0.32129,1.073242 0,1.203125 0.97754,1.203125 0.46484,0 0.79981,-0.102539 0.34179,-0.109375 0.68359,-0.273438 z"
            id="path4666"
            class="svg-elem-92"
          ></path>
          <path
            d="m 307.24817,-23.914688 q 0,0.957031 -0.6084,1.449219 -0.60156,0.492187 -1.78418,0.492187 -0.47851,0 -1.05957,-0.102539 -0.57422,-0.0957 -0.90234,-0.21875 v -1.579101 h 0.30761 l 0.33496,0.895507 q 0.5127,0.464844 1.33301,0.464844 1.32617,0 1.32617,-1.134766 0,-0.833984 -1.04589,-1.189453 l -0.6084,-0.198242 q -0.69043,-0.225586 -1.00489,-0.458008 -0.31445,-0.232422 -0.48535,-0.567382 -0.1709,-0.341797 -0.1709,-0.820313 0,-0.847656 0.57422,-1.333008 0.58106,-0.492187 1.56543,-0.492187 0.7041,0 1.76368,0.211914 v 1.401367 h -0.32129 l -0.28711,-0.745117 q -0.36231,-0.321289 -1.1416,-0.321289 -0.55372,0 -0.84766,0.273437 -0.28711,0.273438 -0.28711,0.738281 0,0.389649 0.25977,0.65625 0.2666,0.266602 0.7998,0.444336 1.00488,0.341797 1.3125,0.499024 0.30762,0.157226 0.51953,0.389648 0.21875,0.225586 0.33496,0.519532 0.12305,0.293945 0.12305,0.724609 z"
            id="path4668"
            class="svg-elem-93"
          ></path>
          <path
            d="m 310.10559,-25.20668 2.63184,-2.836914 -0.66993,-0.184571 v -0.307617 h 2.26954 v 0.307617 l -0.79981,0.157227 -1.83203,1.873047 2.35156,3.623047 0.69727,0.157226 v 0.307617 h -2.63184 v -0.307617 l 0.58789,-0.170898 -1.76367,-2.768555 -0.84082,0.922852 v 1.845703 l 0.68359,0.170898 v 0.307617 h -2.63183 v -0.307617 l 0.81348,-0.170898 v -8.763672 l -0.9502,-0.164063 v -0.307617 h 2.08496 z"
            id="path4670"
            class="svg-elem-94"
          ></path>
          <path
            d="m 319.69641,-23.914688 q 0,0.957031 -0.6084,1.449219 -0.60156,0.492187 -1.78418,0.492187 -0.47851,0 -1.05957,-0.102539 -0.57422,-0.0957 -0.90234,-0.21875 v -1.579101 h 0.30762 l 0.33496,0.895507 q 0.51269,0.464844 1.333,0.464844 1.32618,0 1.32618,-1.134766 0,-0.833984 -1.0459,-1.189453 l -0.6084,-0.198242 q -0.69043,-0.225586 -1.00488,-0.458008 -0.31446,-0.232422 -0.48535,-0.567382 -0.1709,-0.341797 -0.1709,-0.820313 0,-0.847656 0.57422,-1.333008 0.58105,-0.492187 1.56543,-0.492187 0.7041,0 1.76367,0.211914 v 1.401367 h -0.32129 l -0.28711,-0.745117 q -0.36231,-0.321289 -1.1416,-0.321289 -0.55371,0 -0.84766,0.273437 -0.28711,0.273438 -0.28711,0.738281 0,0.389649 0.25977,0.65625 0.2666,0.266602 0.7998,0.444336 1.00488,0.341797 1.3125,0.499024 0.30762,0.157226 0.51953,0.389648 0.21875,0.225586 0.33496,0.519532 0.12305,0.293945 0.12305,0.724609 z"
            id="path4672"
            class="svg-elem-95"
          ></path>
        </g>
      </g>
      <!-- agents&#45;&gt;tasks -->
      <g id="edge4" class="edge">
        <title id="title4474">agents-&gt;tasks</title>
        <g id="g4478">
          <path
            d="M255.03 -57.75 C261.166050043735 -54.62935839991662, 269.36111215827214 -50.09152495627406, 273.8749997366007 -44.94576578268843 M254.71792721754778 -56.427155036535936 C262.23748468811544 -55.07561499288133, 267.9059348391124 -47.98314060211502, 273.43600087017916 -42.89943426068672"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4476"
            class="svg-elem-96"
          ></path>
        </g>
        <g id="g4484">
          <path
            d="M277.0484493177479 -48.01828982557166 C277.0484493177479 -48.01828982557166, 277.0484493177479 -48.01828982557166, 277.0484493177479 -48.01828982557166 M277.0484493177479 -48.01828982557166 C277.0484493177479 -48.01828982557166, 277.0484493177479 -48.01828982557166, 277.0484493177479 -48.01828982557166 M275.4814445630921 -40.142904503810726 C275.8122995230217 -40.93388912431102, 277.8240665987782 -42.380662877957235, 279.7230762949959 -44.91010162138466 M275.7382521281297 -40.199567675668945 C276.4365632331296 -41.27079446089093, 277.18394676530204 -41.96453554806319, 279.6408659881414 -44.718806691997344 M279.767016695954 -39.16785378013757 C280.2296359074063 -39.603268623527455, 281.20190216063327 -40.47395139623154, 281.69352508135097 -41.30963947870394 M279.9404611309619 -39.01898299304508 C280.59960543335666 -39.61860647444105, 281.01868638021114 -40.42822531445962, 281.7134226977216 -41.34274926262317"
            stroke="black"
            stroke-width="0.5"
            fill="none"
            id="path4480"
            class="svg-elem-97"
          ></path>
          <path
            d="M276.10573347459365 -48.26609287995645 C279.1493380340547 -45.74081880849281, 280.2423546698686 -43.03057720096045, 282.7828971110366 -40.07575038666273 M276.80625866245975 -48.08318837218305 C277.7629502177365 -45.63477767536286, 279.23187604305747 -44.2833993074695, 283.7930314962255 -39.89557720859378 M282.7551776959333 -38.42980020588709 C279.7347128625702 -39.41696997299687, 277.0782047340903 -39.97084997167636, 272.2498847022857 -42.32888608047561 M283.2199766395679 -39.73888004026828 C280.11990431240287 -40.09537830001664, 276.22862049098984 -41.54389809202371, 273.48202598902986 -42.236474547599926 M273.61508940638765 -41.529491842472176 C274.8246338708941 -43.124320848357634, 275.05641734178903 -45.412491192741236, 276.5173820328763 -48.17712995152815 M273.10231908042175 -41.87791001423505 C273.9880423027698 -43.430857632590666, 275.3210882516435 -44.96462879743542, 277.1091414226511 -47.65674431296104 M276.85 -47.79 C276.85 -47.79, 276.85 -47.79, 276.85 -47.79 M276.85 -47.79 C276.85 -47.79, 276.85 -47.79, 276.85 -47.79"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4482"
            class="svg-elem-98"
          ></path>
        </g>
      </g>
      <!-- tools -->
      <g id="node6" class="node">
        <title id="title4487">tools</title>
        <g id="g4493">
          <path
            d="M104.22715083860628 -53.82313633064861 C104.22715083860628 -53.82313633064861, 104.22715083860628 -53.82313633064861, 104.22715083860628 -53.82313633064861 M104.22715083860628 -53.82313633064861 C104.22715083860628 -53.82313633064861, 104.22715083860628 -53.82313633064861, 104.22715083860628 -53.82313633064861 M96.83907750546433 -40.703914657695925 C101.33354053979048 -43.21307424351294, 105.64854153655523 -49.26752394358313, 111.41592715993251 -58.75726137299489 M98.97452451777296 -42.02556747242779 C103.42552011247231 -47.85011343706449, 109.03813459338289 -52.95184741200108, 111.80948478287466 -57.72171739791632 M101.5791470976147 -39.069367984421916 C107.23136897691774 -44.177140346622956, 112.09152703584637 -49.93425477188232, 121.27266137733744 -58.35192946996939 M100.90450072607693 -37.38839212073263 C109.11599571804064 -45.696174459323416, 116.05294533991771 -54.46664782959288, 120.16477579656215 -59.329781325982964 M104.30249457663388 -35.54723445425536 C109.6200737950458 -40.61934689246531, 113.92773589240105 -47.578900129319614, 127.07552856661714 -60.76798752109535 M102.48798071004599 -33.80939946903826 C107.40451891076201 -40.44390692030871, 111.47520452627684 -45.79930651330106, 126.74605028753099 -60.9763619773506 M107.25913580113068 -31.34166816267045 C113.32241320956581 -40.00374834710717, 120.74730677430497 -47.08183468023422, 129.1821310049663 -59.6553537573262 M106.17250513562853 -31.964888913583295 C113.24599667064413 -38.9102320417182, 119.79792657418552 -47.06209086871219, 129.98818995064246 -59.550603812360684 M112.0256908425778 -31.69778179896404 C119.59807099852262 -40.30519798984609, 130.01018596216153 -51.02678658634446, 136.05642623790763 -59.224045136473364 M110.50138924317831 -29.83062247841456 C116.9594351646146 -37.58626887511762, 123.27580781290557 -45.709688867428824, 135.3123305087108 -59.65090370744933 M114.44963382940928 -29.423008501318744 C121.23223421118335 -38.34979327757427, 126.43938481127138 -45.394908473711084, 138.92668170700674 -58.48521123144422 M114.41102045381417 -28.592073084397075 C120.13895759317508 -36.03388847066766, 127.66384129482074 -42.75656056612555, 139.90174411222378 -59.10357924594966 M117.35610943341108 -26.215115233421177 C127.07660732511518 -34.55308923722656, 134.70619492052853 -46.03720235735668, 144.13008152747048 -58.353849504258434 M117.27651524812826 -27.76997817049197 C127.77037064347572 -37.67263613090743, 137.74234264087477 -50.50318300922588, 144.85946567456867 -56.76628166079436 M120.49290593493687 -25.52281302038829 C126.69631575665173 -34.04881324541949, 134.6997924798156 -37.743440069773364, 147.9265611870974 -55.59013379445151 M123.07375562413877 -25.532191520657797 C131.5725100659878 -38.0358675810758, 141.32637776408095 -47.54049390518621, 148.8191724013012 -55.01115728544437 M128.15979621442352 -26.80329259753256 C133.0550389058158 -30.047673979176718, 139.43969504732902 -38.83961420797806, 151.4142735150103 -55.01732458626797 M128.23204689496046 -26.530606430048138 C136.05020033472567 -35.06556730046815, 145.4790367040678 -45.303658295885775, 151.5547638403606 -52.64397006638636 M132.2200840585489 -26.727091024100858 C139.0517021696657 -32.168339195897, 147.2229750162639 -41.626606238239255, 153.8859530067969 -50.95295661779666 M133.17354859318954 -27.776772423363578 C141.70791597250903 -36.81345582017196, 151.04803236715608 -45.694621908447004, 154.73511286713494 -51.2067755216885 M137.53478571539745 -28.296145816512162 C146.30473298020317 -32.61459735063387, 151.0829370616135 -40.91778841469291, 159.87352317921054 -50.562550914945206 M139.32344925381992 -26.831196049660598 C144.95096356548402 -33.410798851960294, 152.63977382897096 -42.272777433216845, 160.01313737929382 -49.5594672855662 M147.64179012307497 -27.531600448511238 C150.75098990146196 -33.40761195729887, 154.93072868228717 -39.782560447083334, 157.77698997521208 -42.60615914014465 M146.58173152318952 -27.94884078646995 C149.20835897080858 -33.68019921525017, 153.58240878073855 -38.65531736248723, 159.6732846746594 -43.59976064389561"
            stroke="none"
            stroke-width="0.5"
            fill="none"
            id="path4489"
            class="svg-elem-99"
          ></path>
          <path
            d="M121.83579803727399 -60.38700890342129 C127.97698681253452 -61.283231674685645, 137.09209600266593 -60.38619727049514, 143.24065355585816 -58.67713228159176 C149.3892111090504 -56.96806729268838, 156.08168177009634 -53.56765887674001, 158.72714335642746 -50.13261897000102 C161.37260494275858 -46.697579063262026, 161.3444880983588 -41.71080452848109, 159.11342307384496 -38.066892841157795 C156.88235804933112 -34.4229811538345, 151.1127963599654 -30.363896120612242, 145.3407532093445 -28.269148846061253 C139.56871005872364 -26.174401571510263, 131.1030757045381 -24.85183213236791, 124.48116417011968 -25.49840919385186 C117.85925263570127 -26.14498625533581, 110.11227818885709 -29.27482801595471, 105.60928400283402 -32.148611214964944 C101.10628981681094 -35.02239441397518, 97.64574147392025 -39.073684847058196, 97.46319905398121 -42.74110838791327 C97.28065663404217 -46.40853192876835, 99.648016349347 -51.226888080178576, 104.5140294831998 -54.15315246009539 C109.38004261705261 -57.07941684001221, 121.87081650058106 -59.22950017552576, 126.65927785709805 -60.29869466741415 C131.44773921361502 -61.36788915930255, 133.13417736905024 -60.91045637931465, 133.24479762230175 -60.568319411425776 M134.6468252534282 -59.094182637115836 C141.2000093923321 -58.325736371436506, 150.0790342353667 -55.85020088722149, 154.1406917028135 -52.97502710016703 C158.20234917026033 -50.099853313112575, 159.21006657523668 -45.57593543914088, 159.0167700581091 -41.8431399147891 C158.82347354098152 -38.11034439043732, 157.19553114328156 -33.157817768980365, 152.98091260004801 -30.578253954056343 C148.76629405681447 -27.99869013913232, 140.4918612056316 -26.718481736352285, 133.7290587987078 -26.365757025244967 C126.96625639178399 -26.01303231413765, 118.40592890748302 -26.709270230769746, 112.40409815850515 -28.46190568741244 C106.40226740952728 -30.214541144055133, 100.08619571711034 -33.534264118968416, 97.71807430484061 -36.88156976510112 C95.34995289257088 -40.22887541123382, 95.68129804689073 -44.83132878600628, 98.19536968488681 -48.54573956420866 C100.7094413228829 -52.26015034241104, 106.66485863055232 -57.45307710448927, 112.80250413281706 -59.168034434315395 C118.94014963508181 -60.88299176414152, 131.3938273610231 -58.98396480621659, 135.02124269847533 -58.83548354316541 C138.64865803592755 -58.68700228011423, 134.78017878872143 -58.21970214535022, 134.5669961575304 -58.277146856008315"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4491"
            class="svg-elem-100"
          ></path>
        </g>
        <g
          aria-label="Tools"
          id="text4495"
          style="
            font-size: 14px;
            font-family: Tinos, serif;
            text-anchor: middle;
          "
        >
          <path
            d="m 115.40727,-39.27 v -0.362305 l 1.45606,-0.18457 v -8.032227 h -0.34864 q -1.72949,0 -2.36523,0.136719 l -0.18457,1.428711 h -0.45801 v -2.153321 h 8.06641 v 2.153321 h -0.46485 l -0.18457,-1.428711 q -0.20507,-0.04785 -0.8955,-0.08203 -0.69043,-0.04102 -1.51075,-0.04102 h -0.33496 v 8.018555 l 1.45606,0.18457 V -39.27 Z"
            id="path4675"
            class="svg-elem-101"
          ></path>
          <path
            d="m 127.29497,-42.517071 q 0,3.383789 -3.00781,3.383789 -1.44922,0 -2.1875,-0.868164 -0.73829,-0.868164 -0.73829,-2.515625 0,-1.626953 0.73829,-2.488281 0.73828,-0.861328 2.24218,-0.861328 1.46289,0 2.20801,0.847656 0.74512,0.84082 0.74512,2.501953 z m -1.23047,0 q 0,-1.476562 -0.43067,-2.139648 -0.43066,-0.663086 -1.34667,-0.663086 -0.89551,0 -1.29883,0.635742 -0.39649,0.635742 -0.39649,2.166992 0,1.551758 0.40332,2.201172 0.41016,0.642578 1.292,0.642578 0.90234,0 1.33984,-0.669922 0.4375,-0.669922 0.4375,-2.173828 z"
            id="path4677"
            class="svg-elem-102"
          ></path>
          <path
            d="m 134.29497,-42.517071 q 0,3.383789 -3.00781,3.383789 -1.44922,0 -2.1875,-0.868164 -0.73829,-0.868164 -0.73829,-2.515625 0,-1.626953 0.73829,-2.488281 0.73828,-0.861328 2.24218,-0.861328 1.46289,0 2.20801,0.847656 0.74512,0.84082 0.74512,2.501953 z m -1.23047,0 q 0,-1.476562 -0.43067,-2.139648 -0.43066,-0.663086 -1.34667,-0.663086 -0.89551,0 -1.29883,0.635742 -0.39649,0.635742 -0.39649,2.166992 0,1.551758 0.40332,2.201172 0.41016,0.642578 1.292,0.642578 0.90234,0 1.33984,-0.669922 0.4375,-0.669922 0.4375,-2.173828 z"
            id="path4679"
            class="svg-elem-103"
          ></path>
          <path
            d="m 137.33696,-39.748516 1.10059,0.170898 V -39.27 h -3.32911 v -0.307618 l 1.09375,-0.170898 v -8.763672 l -1.09375,-0.164062 v -0.307618 h 2.22852 z"
            id="path4681"
            class="svg-elem-104"
          ></path>
          <path
            d="m 143.6602,-41.074688 q 0,0.957031 -0.6084,1.449219 -0.60156,0.492187 -1.78418,0.492187 -0.47851,0 -1.05957,-0.102539 -0.57422,-0.0957 -0.90234,-0.21875 v -1.579101 h 0.30762 l 0.33496,0.895507 q 0.51269,0.464844 1.33301,0.464844 1.32617,0 1.32617,-1.134765 0,-0.833985 -1.0459,-1.189454 l -0.6084,-0.198242 q -0.69043,-0.225586 -1.00488,-0.458008 -0.31446,-0.232421 -0.48535,-0.567382 -0.1709,-0.341797 -0.1709,-0.820313 0,-0.847656 0.57422,-1.333008 0.58105,-0.492187 1.56543,-0.492187 0.7041,0 1.76367,0.211914 v 1.401367 h -0.32129 l -0.28711,-0.745117 q -0.3623,-0.321289 -1.1416,-0.321289 -0.55371,0 -0.84766,0.273437 -0.28711,0.273438 -0.28711,0.738282 0,0.389648 0.25977,0.65625 0.2666,0.266601 0.7998,0.444336 1.00489,0.341796 1.3125,0.499023 0.30762,0.157227 0.51953,0.389648 0.21875,0.225586 0.33497,0.519532 0.12304,0.293945 0.12304,0.724609 z"
            id="path4683"
            class="svg-elem-105"
          ></path>
        </g>
      </g>
      <!-- tasks&#45;&gt;tools -->
      <g id="edge5" class="edge">
        <title id="title4498">tasks-&gt;tools</title>
        <g id="g4502">
          <path
            d="M273.36 -28.84 C245.2248551945093 -33.010468801185766, 199.30291234302038 -36.0412905116394, 168.10690961480415 -38.17431624828435 M271.8960733760912 -26.90889739786052 C242.55353695126507 -32.83880502687224, 203.02585181155757 -36.88981669724303, 170.18707771964648 -37.31930905521956"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4500"
            class="svg-elem-106"
          ></path>
        </g>
        <g id="g4508">
          <path
            d="M159.38382772026029 -40.32650644248099 C159.38382772026029 -40.32650644248099, 159.38382772026029 -40.32650644248099, 159.38382772026029 -40.32650644248099 M159.38382772026029 -40.32650644248099 C159.38382772026029 -40.32650644248099, 159.38382772026029 -40.32650644248099, 159.38382772026029 -40.32650644248099 M162.66831482598857 -38.225587449171286 C163.4093744788734 -39.00804288505235, 164.5230929689485 -39.63399307659517, 165.3508071481862 -41.317199087466825 M163.07812571616986 -38.572989693507445 C163.73277667939584 -39.21032109484775, 164.6626636788485 -40.033325569185905, 165.8591479179875 -41.29369782783089 M167.01505928695505 -36.870919365119605 C167.56643442574995 -37.81916217025861, 168.77103741044115 -38.2697670538855, 170.02697620733386 -39.89080614584748 M166.62523160967567 -36.73562521033181 C167.34069634247965 -37.5071659320456, 168.47293900996084 -38.367626935977896, 170.2431513363773 -40.124902299162514"
            stroke="black"
            stroke-width="0.5"
            fill="none"
            id="path4504"
            class="svg-elem-107"
          ></path>
          <path
            d="M168.11105412482615 -35.90479578033646 C166.10851789287008 -36.91545223190731, 161.29356893755607 -38.138021188317325, 158.73851086006573 -39.854155833251866 M169.08733858584745 -35.644823131277946 C165.274419617852 -37.566129878172404, 162.37884834306792 -39.171112339084175, 158.99314780683042 -40.03219700466243 M160.097522036869 -39.178405741278894 C162.25134822044333 -40.57068449477111, 164.21656926572732 -41.72481105877457, 169.52928639785307 -42.18672172941325 M159.6268450424069 -40.40665319174462 C160.94942704639703 -40.76893891160116, 163.06430002523692 -40.68956463206559, 169.915360890403 -42.1182078680573 M168.8951097344415 -43.17342581982763 C168.9269190760261 -40.5487300071358, 168.25317651813288 -37.57102688567076, 168.9374637112976 -35.10938263514321 M169.40658404131503 -42.495101282861796 C169.3801664154754 -40.556698971435225, 168.9299893626574 -37.652384705233196, 168.89509587229983 -35.28414200543027 M168.72 -35.55 C168.72 -35.55, 168.72 -35.55, 168.72 -35.55 M168.72 -35.55 C168.72 -35.55, 168.72 -35.55, 168.72 -35.55"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4506"
            class="svg-elem-108"
          ></path>
        </g>
      </g>
      <!-- gemini -->
      <g id="node7" class="node">
        <title id="title4511">gemini</title>
        <g id="g4517">
          <path
            d="M7.021963177126551 -175.42268062547714 C7.021963177126551 -175.42268062547714, 7.021963177126551 -175.42268062547714, 7.021963177126551 -175.42268062547714 M7.021963177126551 -175.42268062547714 C7.021963177126551 -175.42268062547714, 7.021963177126551 -175.42268062547714, 7.021963177126551 -175.42268062547714 M7.926880101015982 -172.18662624425613 C15.011262649797873 -176.34524896195697, 16.76713677918041 -182.57274853826027, 21.43728361021939 -186.63015719692862 M9.108239053782913 -171.8260784519546 C13.295264567021658 -176.08519534433918, 17.549252443647582 -181.41906925653865, 22.18773268932957 -186.44137529343857 M11.0874262556776 -169.40317637350353 C18.248846342944088 -175.918180323977, 22.65860171985512 -181.3409257703823, 28.667583333863856 -187.20586552898146 M11.126361606511416 -168.8057964298999 C17.449887348087024 -175.6497796993953, 22.60966681445127 -181.63299905055072, 27.437604771319283 -188.42772099234764 M13.353287198710778 -163.1370936842918 C22.13089980746056 -174.082000410908, 28.64927845495611 -181.51059284938052, 34.401119972593094 -188.75579635017044 M14.006056001640589 -164.53614583432295 C19.754804684565933 -172.166538006268, 25.708845275654127 -179.29304442515812, 34.73631098827281 -188.0587952774966 M16.11766707232305 -160.72828218084666 C24.883825217348715 -170.52814345013113, 27.816726675602435 -174.9710376906976, 38.92522493819356 -187.91390655422566 M16.311284663437856 -162.44129763764175 C23.925527261939088 -170.84138591434282, 30.09115740262271 -177.01353010946912, 40.48508425294003 -189.29127663229943 M21.708980999566712 -162.05634796660803 C25.73261910463643 -168.93302351947082, 30.600591644942753 -175.11651234635065, 47.14750454419346 -190.33442057442093 M21.301756179370013 -161.20187483861278 C30.619551717290133 -171.20564379800302, 38.80332827111651 -182.39736750676542, 46.434730475772504 -190.13410683913025 M25.22907610422318 -160.72406133637875 C31.84728471225452 -166.40895098896928, 37.84303473719443 -172.1354340652352, 51.11994540241138 -188.7080164240768 M24.911121852453697 -159.8246301532356 C34.88526870390495 -171.09993996712842, 43.43676352837583 -182.27251012190004, 50.59798239585815 -189.42120018564864 M26.558635972158964 -157.38975123175658 C37.78359281530914 -169.27054393881397, 46.79281712181241 -181.45371975898618, 56.22867656403995 -188.83968147974275 M28.202309418600848 -156.5091893040432 C33.36682274757094 -162.89869554332998, 39.24733757551042 -170.67021560069423, 55.997630785292905 -187.08140045283216 M31.027950444778472 -156.56008649286878 C37.7604338928287 -163.1499250440005, 45.84806046005578 -170.98809058507393, 58.25621193808737 -186.12509562489967 M33.19128010210591 -155.97715268945524 C43.75076447465054 -168.80093114038172, 53.39973261826034 -180.65062778993646, 60.18536144695612 -186.4380562602947 M38.4149512263871 -156.49901751100774 C49.6657696345017 -168.30972508339636, 57.31372139002391 -180.82938045985793, 65.01786832200854 -185.24802757303303 M38.97093215750506 -157.13056999385577 C48.49488604221396 -166.77091542207765, 55.91394970286565 -177.8319229898497, 65.01095037853416 -186.4172171138084 M43.988011526431556 -156.67586817249486 C47.796161830877395 -164.5162633960489, 56.418432906351 -171.18190419188855, 69.87776073480727 -184.77721012653976 M43.38426086645852 -155.6935814846436 C52.578574764626694 -166.58976516299356, 59.948935353119516 -175.5916274914267, 68.57990306862119 -185.00982818130754 M49.39079242782016 -153.91168140077696 C59.56283027635914 -165.05042490306678, 68.5004558037178 -176.05675900842283, 71.31618553131257 -185.19844621913697 M48.77836261678996 -154.81107553126532 C54.825538661244245 -162.58818225188114, 61.60464843080217 -168.97499116587494, 71.93469097763759 -183.95084830071838 M53.86041731528241 -156.48888281459924 C59.389773370174154 -159.36022081653928, 61.31619090675791 -165.65045447810436, 76.94182596838125 -180.35883329833 M54.59083618802841 -156.768496087422 C62.073474364791096 -163.75980317973364, 69.96312078775904 -174.26253594667062, 75.21947076319302 -180.03765322348178 M60.809364855680386 -159.2731210888993 C65.12090466026031 -161.4639626011793, 67.1116345124685 -168.51597357280127, 78.04433539945275 -177.2520902803459 M61.51025711418465 -158.84219855745286 C67.18417446452659 -165.20512327225939, 75.4642927443341 -174.01940161210914, 78.47681480010839 -179.88688716592247 M67.20709860917297 -159.15103401682418 C74.76179540204872 -165.40099270045536, 77.74935504590923 -171.96087199330145, 80.90392136812254 -177.36325584506383 M66.92056741938862 -159.74027751346355 C70.24172006081713 -164.54518827914575, 74.24155236591373 -166.91917423895524, 82.83113067967602 -176.72824641642967 M75.46579224973394 -162.29022440997366 C75.98606176934852 -163.46205275623748, 77.29698575492246 -164.96906772881516, 78.5208292374055 -165.90099738824904 M75.1657180535088 -162.53909389686837 C76.21492442878342 -163.7356359891863, 77.6468706109057 -165.10563143907729, 78.52344349065068 -166.00311908254014"
            stroke="none"
            stroke-width="0.5"
            fill="none"
            id="path4513"
            class="svg-elem-109"
          ></path>
          <path
            d="M46.936918999720554 -190.56450118209227 C54.6212173594937 -190.4150677440296, 64.44434785902513 -187.53862224398162, 70.48538466561175 -185.02080122789408 C76.52642147219836 -182.50298021180654, 82.29393754681539 -179.17553072916434, 83.18313983924025 -175.4575750855671 C84.07234213166512 -171.73961944196986, 80.50740464373627 -165.91547315948634, 75.82059842016098 -162.71306736631067 C71.13379219658569 -159.510661573135, 62.76195169482605 -157.2670025482331, 55.062302497788565 -156.243140326513 C47.36265330075108 -155.21927810479286, 36.80276812579814 -155.09064289280295, 29.622703237936044 -156.56989403598988 C22.442638350073953 -158.0491451791768, 15.70594188978851 -161.92732484921154, 11.981913170616018 -165.1186471856346 C8.257884451443525 -168.30996952205763, 5.6713061715828434 -172.20295815208033, 7.278530922901091 -175.7178280545281 C8.885755674219338 -179.23269795697587, 14.785712256680661 -183.81884887968369, 21.6252616785255 -186.2078666003213 C28.46481110037034 -188.5968843209589, 43.31391376554923 -189.46406236985013, 48.31582745397013 -190.05193437835368 C53.31774114239103 -190.63980638685723, 51.56422168446882 -189.85504782628263, 51.63674380905088 -189.7350986513426 M39.39912336455605 -190.45978399508394 C47.132571096357296 -191.15837569072346, 58.15148103809934 -190.00911838639223, 65.29305658689499 -187.84952852224808 C72.43463213569063 -185.68993865810393, 79.70912217040114 -181.09755907913956, 82.24857665732995 -177.50224481021894 C84.78803114425875 -173.90693054129832, 84.1137973206607 -169.66739006516235, 80.5297835084678 -166.2776429087243 C76.94576969627491 -162.88789575228623, 68.29382298658443 -158.94555392718837, 60.744493784172576 -157.16376187159048 C53.19516458176072 -155.3819698159926, 42.69583932788881 -154.6013204292049, 35.23380829399667 -155.58689057513703 C27.771777260104525 -156.57246072106918, 20.89369555849597 -160.04634205781485, 15.97230758081972 -163.07718274718337 C11.05091960314347 -166.1080234365519, 5.576274345833592 -170.4283861970024, 5.705480427939165 -173.77193471134805 C5.834686510044738 -177.1154832256937, 10.920984047949787 -180.3494438970633, 16.747544073453156 -183.13847383325734 C22.574104098956525 -185.92750376945136, 36.57802383452997 -189.57757016679065, 40.66484058095938 -190.50611432851218 C44.751657327388784 -191.43465849023372, 41.47861842929545 -189.0275250799003, 41.2684445520296 -188.70973880358648"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4515"
            class="svg-elem-110"
          ></path>
        </g>
        <g
          aria-label="Gemini"
          id="text4519"
          style="
            font-size: 14px;
            font-family: Tinos, serif;
            text-anchor: middle;
          "
        >
          <path
            d="m 32.500763,-169.59851 q -0.792969,0.25976 -1.647461,0.4375 -0.854492,0.17773 -1.838867,0.17773 -2.228516,0 -3.472656,-1.20312 -1.244141,-1.20313 -1.244141,-3.41113 0,-2.40625 1.203125,-3.59571 1.209961,-1.19629 3.541016,-1.19629 1.667968,0 3.219726,0.41016 v 1.96875 h -0.458008 l -0.18457,-1.13477 q -0.47168,-0.33496 -1.134766,-0.51269 -0.65625,-0.18457 -1.387695,-0.18457 -1.75,0 -2.563476,1.0459 -0.806641,1.03906 -0.806641,3.18554 0,2.01661 0.833984,3.0625 0.833985,1.03907 2.467774,1.03907 0.574218,0 1.203125,-0.13672 0.628906,-0.13672 0.957031,-0.32813 v -2.60449 l -1.175781,-0.17773 v -0.36914 h 3.383789 v 0.36914 l -0.895508,0.17773 z"
            id="path4686"
            class="svg-elem-111"
          ></path>
          <path
            d="m 35.611115,-172.35339 v 0.12304 q 0,0.94336 0.205078,1.46973 0.211914,0.51953 0.642578,0.79297 0.4375,0.27344 1.141601,0.27344 0.369141,0 0.875,-0.0615 0.50586,-0.0615 0.833985,-0.13672 v 0.38282 q -0.328125,0.21191 -0.895508,0.36914 -0.560547,0.15722 -1.148438,0.15722 -1.49707,0 -2.194336,-0.80664 -0.690429,-0.80664 -0.690429,-2.59082 0,-1.68164 0.704101,-2.50879 0.704102,-0.82714 2.009766,-0.82714 2.467773,0 2.467773,2.80273 v 0.56055 z m 1.483398,-2.81641 q -0.710938,0 -1.09375,0.57422 -0.375977,0.57422 -0.375977,1.69531 h 2.748047 q 0,-1.22363 -0.314453,-1.74316 -0.314453,-0.52637 -0.963867,-0.52637 z"
            id="path4688"
            class="svg-elem-112"
          ></path>
          <path
            d="m 42.276154,-175.02625 q 0.512695,-0.29394 1.086914,-0.49218 0.574218,-0.19824 1.011718,-0.19824 0.47168,0 0.868164,0.17773 0.403321,0.17773 0.601563,0.56738 0.526367,-0.29394 1.230469,-0.51953 0.710937,-0.22558 1.175781,-0.22558 1.640625,0 1.640625,1.89355 v 4.22461 l 0.827148,0.1709 v 0.30761 h -2.918945 v -0.30761 l 0.957031,-0.1709 v -4.10156 q 0,-1.17578 -1.09375,-1.17578 -0.177734,0 -0.416992,0.0273 -0.232422,0.0273 -0.47168,0.0615 -0.232421,0.0342 -0.451171,0.082 -0.211914,0.041 -0.355469,0.0684 0.116211,0.36914 0.116211,0.81348 v 4.22461 l 0.963867,0.1709 V -169.12 H 43.99881 v -0.30761 l 0.950195,-0.1709 v -4.10156 q 0,-0.56739 -0.293945,-0.86817 -0.28711,-0.30761 -0.868164,-0.30761 -0.601563,0 -1.497071,0.19824 v 5.0791 l 0.963868,0.1709 v 0.30761 h -2.91211 v -0.30761 l 0.813477,-0.1709 v -5.46875 l -0.813477,-0.1709 v -0.30762 h 1.879883 z"
            id="path4690"
            class="svg-elem-113"
          ></path>
          <path
            d="m 53.459747,-169.59851 1.100586,0.1709 v 0.30761 h -3.329101 v -0.30761 l 1.09375,-0.1709 v -5.46875 l -0.90918,-0.1709 v -0.30762 h 2.043945 z m 0.06836,-8.0459 q 0,0.30078 -0.21875,0.51953 -0.21875,0.21875 -0.526367,0.21875 -0.300782,0 -0.519532,-0.21875 -0.21875,-0.21875 -0.21875,-0.51953 0,-0.30762 0.21875,-0.52637 0.21875,-0.21875 0.519532,-0.21875 0.307617,0 0.526367,0.21875 0.21875,0.21875 0.21875,0.52637 z"
            id="path4692"
            class="svg-elem-114"
          ></path>
          <path
            d="m 57.041779,-175.02625 q 0.526367,-0.30078 1.121093,-0.49218 0.594727,-0.19824 0.991211,-0.19824 0.833985,0 1.257813,0.48535 0.423828,0.48535 0.423828,1.4082 v 4.22461 l 0.779297,0.1709 v 0.30761 h -2.768555 v -0.30761 l 0.854492,-0.1709 v -4.10156 q 0,-0.56739 -0.280273,-0.88868 -0.273438,-0.32812 -0.854492,-0.32812 -0.615235,0 -1.510743,0.19824 v 5.12012 l 0.868165,0.1709 v 0.30761 h -2.775391 v -0.30761 l 0.772461,-0.1709 v -5.46875 l -0.772461,-0.1709 v -0.30762 h 1.832031 z"
            id="path4694"
            class="svg-elem-115"
          ></path>
          <path
            d="m 64.349396,-169.59851 1.100586,0.1709 V -169.12 H 62.12088 v -0.30761 l 1.09375,-0.1709 v -5.46875 l -0.90918,-0.1709 v -0.30762 h 2.043946 z m 0.06836,-8.0459 q 0,0.30078 -0.21875,0.51953 -0.21875,0.21875 -0.526367,0.21875 -0.300781,0 -0.519531,-0.21875 -0.21875,-0.21875 -0.21875,-0.51953 0,-0.30762 0.21875,-0.52637 0.21875,-0.21875 0.519531,-0.21875 0.307617,0 0.526367,0.21875 0.21875,0.21875 0.21875,0.52637 z"
            id="path4696"
            class="svg-elem-116"
          ></path>
        </g>
      </g>
      <!-- tools&#45;&gt;gemini -->
      <g id="edge6" class="edge">
        <title id="title4522">tools-&gt;gemini</title>
        <g id="g4526">
          <path
            d="M117.73 -59.95 C103.18152805717793 -80.61846481349022, 76.95901867867484 -122.19069423250963, 62.25013410833753 -147.46092446635183 M119.72310965361781 -61.41837477340555 C103.2692813541033 -83.42071096832585, 76.77364579765447 -119.73835194809554, 61.46153379449869 -145.2544726611438"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4524"
            class="svg-elem-117"
          ></path>
        </g>
        <g id="g4532">
          <path
            d="M55.954166732654414 -155.41178590946257 C55.954166732654414 -155.41178590946257, 55.954166732654414 -155.41178590946257, 55.954166732654414 -155.41178590946257 M55.954166732654414 -155.41178590946257 C55.954166732654414 -155.41178590946257, 55.954166732654414 -155.41178590946257, 55.954166732654414 -155.41178590946257 M56.80185394812734 -150.7366865883202 C57.80964940367401 -151.7229506625876, 58.655901325264566 -152.345516013595, 59.00993130459753 -152.54473992113665 M57.14728361357572 -150.55959991898638 C57.50033467769579 -151.2710256147071, 58.338409466883355 -151.87895438431008, 58.88293212240584 -152.83394404336798 M58.56088765203823 -146.054305961033 C60.01511129003741 -147.83141364849226, 61.04368631071429 -148.84802644245974, 61.800798923276346 -149.94666379644423 M58.15040424986931 -145.83317623503433 C59.505150739066316 -147.01509213620636, 61.01164995389143 -148.75559338868356, 61.779317956260535 -150.41668238535874"
            stroke="black"
            stroke-width="0.5"
            fill="none"
            id="path4528"
            class="svg-elem-118"
          ></path>
          <path
            d="M58.802959136746125 -144.57207502914 C57.394442369487216 -147.51381778046442, 56.19264245369927 -150.4553710066557, 55.67644380591503 -154.8421113108769 M58.524331261743086 -145.58017448014692 C57.694916465787955 -149.1378164873844, 56.49112296004053 -153.4800456411713, 55.447850949891105 -155.3160218553212 M55.79892485861835 -154.83318513665918 C58.46974514926682 -153.61739086274122, 62.243961063955716 -151.0705733019746, 64.14033536819399 -149.25464825753843 M55.64990739579491 -155.32578906717643 C58.65090747546873 -153.32595334585565, 62.84297091116471 -150.92976761278254, 63.99865435717169 -149.11048553009854 M64.01728905169847 -148.7438435343838 C62.83701396869648 -147.94398835858627, 60.8817957551594 -146.66127435951447, 57.985222264226415 -144.79768858283242 M64.66658451901037 -149.06150847877302 C63.14579837054866 -148.2304427515354, 61.84907342035582 -147.70935436911932, 58.12578958181204 -144.9556645140918 M58.46 -145.13 C58.46 -145.13, 58.46 -145.13, 58.46 -145.13 M58.46 -145.13 C58.46 -145.13, 58.46 -145.13, 58.46 -145.13"
            stroke="black"
            stroke-width="1"
            fill="none"
            id="path4530"
            class="svg-elem-119"
          ></path>
        </g>
      </g>
    </g>
  </svg>
</div>

<figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 5</strong>: Stack including <span v-mark.highlight.yellow="{ at: 2 }">PettingZoo</span>, <span v-mark.highlight.yellow="{ at: 3 }">CrewAI</span>, <span v-mark.highlight.yellow="{ at: 4 }">LangChain</span>, <span v-mark.highlight.yellow="{ at: 5 }">VertexAI</span>.</figcaption>

</figure>

<script setup>
  import { ref, onMounted, onUnmounted } from 'vue';

  const stackFigure = ref(null);

  onMounted(() => {
    if (stackFigure.value) {
      const observer = new MutationObserver(mutations => {
        // Handle mutations here
        mutations.forEach(mutation => {
          if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
            // Do something when class attributes change
            const svgElement = document.getElementById("stack-svg");

            if (!svgElement) return;

            const isActive = stackFigure.value.classList.contains(
                "slidev-vclick-current",
            ) || stackFigure.value.classList.contains(
                "slidev-vclick-prior",
            );
            svgElement.classList.toggle("active", isActive);
          }
        });
      });

      observer.observe(stackFigure.value, { attributes: true });

      // Cleanup observer when component unmounts
      onUnmounted(() => {
        observer.disconnect();
      });
    }
  });
</script>

---
layout: two-cols-header
---

# Try the agents on Discord!

::left::

<div class="flex justify-center items-center h-full" v-click=1>
  <iframe src="https://e.widgetbot.io/channels/1160095731831537714/1160095732766871564" allow="clipboard-write; fullscreen" class="w-full h-96 md:h-full md:w-full" style="border: none;"></iframe>
</div>

::right::

<figure class="p-5">
  <img src="/discord-qr.png" class="w-4/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 6</strong>: <a href="https://discord.gg/e8R6ydcgqd">discord.gg/e8R6ydcgqd</a></figcaption>
</figure>

---
layout: two-cols-header
---

# Check out the code!

::left::

<div class="relative h-full w-full">
  <div class="absolute inset-0 overflow-hidden">
    <img src="/github.png" class="h-full w-full object-cover rounded shadow-lg" style="object-position: top;" />
  </div>
</div>

::right::

<figure class="p-5">
  <img src="/discord-qr.png" class="w-4/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 7</strong>: <a href="https://github.com/google-gemini/workshops/tree/main/games">github.com/google-gemini/workshops</a></figcaption>
</figure>

---
layout: two-cols-header
---

# Join our Gemini meetup!

::left::

<div class="relative h-full w-full">
  <div class="absolute inset-0 overflow-hidden">
    <img src="/gemini-analyzes-data.png" class="h-full w-full object-cover rounded shadow-lg" style="object-position: top;" />
  </div>
</div>

::right::

<figure class="p-5">
  <img src="/meetup-qr.png" class="w-4/5 mx-auto" />
  <figcaption class="mt-2 text-center text-sm text-gray-500"><strong>Figure 8</strong>: <a href="https://lu.ma/geminimeetup">lu.ma/geminimeetup</a></figcaption>
</figure>
