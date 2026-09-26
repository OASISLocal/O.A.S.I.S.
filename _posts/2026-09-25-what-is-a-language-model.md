---
title: "What is a language model?"
ref: what-is-a-language-model
lang: en
tags: [basics]
series: foundations
order: 2
reading_minutes: 7
excerpt: "Where a language model's ability comes from, what the billions of numbers inside it are, and the three questions that explain how it behaves."
---

[Last time](/blog/2026/09/25/what-is-ai-and-how-it-works/) we went as deep as "it
predicts the next piece of text". That is true, and it is also the beginning
rather than the end, because three questions come up immediately afterwards:

1. Where does that ability come from?
2. What is actually inside the model?
3. And why does it behave the way it does?

This article answers those three. It assumes nothing.

## Part 1 — The short version

### It comes from reading. An enormous amount of it.

A language model is <span class="term" data-term="training">trained</span> on
text: books, web pages, code, forums, manuals, transcripts. Not by being taught
rules, but by being shown examples and adjusted, slightly, millions of times
whenever its guess was wrong.

The result is not a database of sentences. It is a set of numbers that encode
how language tends to behave. The model never stores "the capital of France is
Paris" as a fact it can look up. It stores a shape that makes *that* likely.

### The model is the numbers, and the numbers are the model

Inside a language model there are no words. No letters, no sentences, no images,
no database. There is a list of numbers — billions of them, its
<span class="term" data-term="parameters">parameters</span> — in a file on your
disk, usually a few gigabytes. Those numbers are what training adjusted. They are
the whole thing, and that file is the
<span class="term" data-term="model-file">model file</span>.

### Three behaviours fall out of that, and nothing more

{% capture behaviours %}
<table class="cmp-table">
  <thead>
    <tr>
      <th scope="col">What you see</th>
      <th scope="col">What it actually is</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">It "knows" facts</th>
      <td>The pattern it learned happens to fit those facts</td>
    </tr>
    <tr>
      <th scope="row">It "forgets" in a long chat</th>
      <td>The beginning left its
        <span class="term" data-term="context-window">context window</span></td>
    </tr>
    <tr>
      <th scope="row">It sometimes invents</th>
      <td>The most fluent continuation is not the truest one</td>
    </tr>
  </tbody>
</table>
{% endcapture %}
{% include components/callout.html type="note" title="Three behaviours, one cause" body=behaviours %}

None of these is a mystery once you accept that there is no database and no
memory. There is a function over numbers, called over and over, one token at a
time.

The vocabulary is fixed and finite, so the model is really choosing among
finitely many next words. It picks the one that best continues the pattern, and
that word can be a strange one.

## Part 2 — One level deeper, still plain language

### Training: adjusting a guess, millions of times

Take a sentence. Cover the last word. Ask the model to guess it. It guesses, and
the guess is wrong, or right, or close. Here is the whole loop:

1. Show the model a chunk of real text.
2. It produces a guess for every possible next token.
3. Measure how wrong the guesses were. That distance from the truth is the key
   thing training tries to make smaller.
4. Nudge **every** parameter a tiny amount in the direction that would have
   improved the guess.
5. Do it again, on a different chunk, on thousands of machines at once, for
   weeks.

Nobody writes the grammar, the facts, or the reasoning. All of it emerges from the
statistics of the text, which is why the model can be fluently wrong: if the
pattern it learned is wrong, the output is wrong in exactly the same fluent way.

{% capture cutoff %}
The training data is a photograph of a moment. A model cannot know anything
published the day it was trained, and it will not warn you about it. That date is
its <span class="term" data-term="knowledge-cutoff">knowledge cutoff</span>, and
it is the reason an assistant should be able to tell you what it does not know
instead of guessing.
{% endcapture %}
{% include components/callout.html type="warning" title="It has a date, and it will not tell you" body=cutoff %}

### Parameters and the model file

The parameters, plus the vocabulary, plus a bit of configuration, are stored as
the model file. That is the whole artifact.

The practical consequence: choosing which model runs is choosing which file is
loaded onto your disk. You can delete it, move it, try another one, and run it
with the network unplugged. Nothing is fetched at query time.

Whether a model publishes its trained numbers is a separate question from whether
its code is open, and the two are constantly confused:

{% capture weights %}
A model with published <span class="term" data-term="open-weights">open
weights</span> lets you download and inspect the trained numbers. It usually does
**not** publish the training code or the data. That is why "open weights" and
"open source" are different claims, and why a model licence is not the app
licence. The [models page](/models.html) spells out which licences apply to what.
{% endcapture %}
{% include components/callout.html type="note" title="Open weights is not open source" body=weights %}

### Tokens: the alphabet it actually works with

Before text reaches the model it is cut into
<span class="term" data-term="token">tokens</span>: chunks that are usually a
word, part of a word, or a piece of punctuation. A
<span class="term" data-term="tokenizer">tokenizer</span> does the cutting, and
it is why every AI product prices things "per token".

Two things follow:

- A token is not a character. The model cannot see spelling. It cannot notice
  that a word and its plural share letters.
- Cutting is lossy in a way that matters: common words are one token, unusual
  names are several, and the cost of a request follows the split.

### Context: the only thing it can see

Everything it knows about your conversation arrives in its input: the
instruction, the files you attached, the messages so far. The maximum size of
that input is the context window.

There is nothing behind it. When you scroll up, nothing is recalled, because the
text is being sent again every single time. A long conversation can push the
beginning out of the window, and the model will then behave as if it never
happened.

The usual fix is not a bigger window. It is writing things down: notes, a summary,
a file. That is not a trick, it is just how the mechanism works.

{% capture sizes %}
<tbody>
  <tr><th scope="row">1.5B params</th><td data-value="1.0">1.0</td></tr>
  <tr><th scope="row">3B params</th><td data-value="2.0">2.0</td></tr>
  <tr><th scope="row">4B params</th><td data-value="2.5">2.5</td></tr>
  <tr><th scope="row">8B params</th><td data-value="4.8">4.8</td></tr>
</tbody>
{% endcapture %}
{% include components/chart.html body=sizes chart="bar" unit=" GB" title="A bigger model is a bigger file" sub="Q4 quantization, the profiles the app ships with" note="Declared download sizes of the quantized files, not measured benchmarks. The exact figures come from each model's own file, and they change with the quantization." %}

A model that learns from more parameters holds more patterns. It does not
automatically become more correct. It becomes heavier first, and the download you
can see is the price of that. If you are wondering what a specific file weighs,
the [models page](/models.html) lists the profiles the app ships with, and
[requirements](/requirements.html) covers how much RAM and VRAM each needs to
load.

### Sampling: the one place where choice enters

The model outputs a probability for every token. Then one is chosen, and that step
is called <span class="term" data-term="sampling">sampling</span>. It is a
decision the application makes, not the model, and it is what people mean when
they talk about a model's "creativity". Same prompt, two settings:

{% include components/tabs.html id="temperature-demo" aria-label="Temperature compared" labels="Low temperature|High temperature" panels="The model almost always takes the most likely token. You get the obvious answer, the same way every time.

This is what you want for code, for pulling data out of a document, and for anything where a surprising answer costs more than a boring one. It is also faster, because the likely path is the one the hardware is quickest at.

`temperature: 0.1` — the same reply every time, and that reply is usually the right one.|The unlikely tail gets to speak. You get more variety, more surprise, and a higher chance of something that reads well and means nothing.

Useful when you want options rather than an answer: naming ideas, drafting several tones, exploring a problem. Useless when being wrong is expensive.

`temperature: 1.2` — three different replies to one prompt, and maybe one of them is wrong in a new way." %}

{% capture why_temp %}
Not a different brain. The same arithmetic, with more of the distribution allowed
to speak. The knob is set by the software around the model, which is why the same
model behaves differently in two applications.
{% endcapture %}
{% include components/callout.html type="tip" title="One model, two personalities" body=why_temp %}

## So why does it behave like that?

Because every behaviour people find surprising has the same explanation: there is
a pattern, and no lookup table.

- **It cannot check itself.** It has nothing to check against.
- **It repeats itself** when the temperature is low and the pattern is strong.
- **It invents citations** because a plausible citation is a plausible
  continuation.
- **It forgets between sessions** because nothing is written down unless
  something writes it down.

None of that is a bug list. It is the same list of consequences.

{% capture faq2 %}
- **Why does it forget the start of a long conversation?**
  Because the start was pushed out of the context window, and there is no memory
  behind the window. Write the important part down and it will read it every
  time.

- **Can it be made to stop inventing?**
  Not by asking. Give it a source to read and a way to show what it used, and
  the inventing drops a long way.

- **Is a bigger model always better?**
  No. It holds more patterns, needs more memory, and answers more slowly. Bigger
  is a trade, not an upgrade.

- **What are the parameters measured in?**
  Billions, written "7B" or "4B". It counts numbers, not skills.

- **Do I need the newest model?**
  Usually not. A smaller model that answers in under a second on your own
  <span class="term" data-term="gpu">GPU</span> is more useful for daily work than
  a bigger one you have to wait for.
{% endcapture %}
{% include components/details.html title="Questions about models" faq="true" open="first" schema="faqpage" body=faq2 open-label="Open all" close-label="Close all" %}

## In short

- A language model is a list of numbers, adjusted by reading an enormous amount of
  text until its guesses got good enough.
- There is no database inside, so there is nothing to look up and nothing to
  check itself against.
- Its behaviour follows from three facts: it predicts, it only sees what is in its
  input, and it chooses among a fixed vocabulary.
- Which model runs is which file is on your disk. That is why it can work with
  the network unplugged.

**Next in this series:** *Tokens and the context window* — the mechanism behind
cost, length limits and the strange way a long conversation forgets its own
beginning. It is being written now; the [Journal index](/blog/) lists what is
already out.

<!--
Series: foundations
Number: 2 of 40
Next: tokens-and-the-context-window (ref: tokens-and-the-context-window)
Pillar page: /models.html (this article is the concept; the page is the product)
-->
