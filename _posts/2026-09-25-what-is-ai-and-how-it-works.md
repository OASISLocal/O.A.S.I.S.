---
title: "What is AI? And how does it work?"
ref: what-is-ai-and-how-it-works
lang: en
tags: [basics]
reading_minutes: 7
excerpt: "What AI actually is, in two levels: the simple version (it predicts the next piece of text) and a deeper one (tokens, probabilities, context)."
---

There is a lot of noise around "artificial intelligence". This article is
deliberately quiet. It explains what a <span class="term" data-term="llm">language
model</span> does, in two passes: the first is the whole idea in plain language,
the second goes one level deeper and still stops short of maths.

Read the first part and you are done. The second is there for the curious.

{% capture one_liner %}
A language model does one thing: it continues text. Everything people call
"intelligence" is that single ability, applied to different problems, plus a very
large number of examples of what the answer usually looks like.
{% endcapture %}
{% include components/callout.html type="note" title="The whole idea, in one box" body=one_liner %}

## Part 1 — In one minute

### It is autocomplete, with a very long memory

You know the feeling. You type half a sentence into a messaging app and it
offers you the rest of the word. That is all a language model does, except the
one you use every day without noticing has read a few hundred billion sentences,
and instead of guessing one word it guesses the next *piece of a sentence*,
repeatedly, until it has written something.

There is no second hidden mechanism.

### It predicts; it does not look things up

This is the part that surprises people. The model has no database of facts
inside it, no list of countries with their capitals, no notes about you. It has
a set of numbers — tens of billions of them, its
<span class="term" data-term="parameters">parameters</span> — which encode the
*patterns* of language: how words tend to follow each other, which sentences are
plausible, which are nonsense.

When it tells you a fact, it is not reading it from a table. It is producing text
that fits the pattern. Often that is exactly right. Sometimes it is not, and the
result is a sentence that is fluent, confident and wrong. We have a name for
that, and it is worth knowing early:

{% capture hallu %}
A **hallucination** is not a bug that gets patched. It is what happens when a
system with no database inside produces the most plausible-looking text instead
of a checked fact. The fix is never "ask it nicely" — it is giving it something
to check against, which is a different design.
{% endcapture %}
{% include components/callout.html type="warning" title="Why it invents" body=hallu %}

### Why that is enough to be useful

If the only skill is "continue this well", how does that become an assistant?
Because almost every task you would ask a machine is a text-shaped task. The
mechanism is identical in all four rows; only the framing changes.

{% capture four_tasks %}
<table class="cmp-table">
  <thead>
    <tr>
      <th scope="col">What you ask for</th>
      <th scope="col">What "continue the text" means here</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Summarise this PDF</th>
      <td>Produce a shorter text that keeps the parts that mattered</td>
    </tr>
    <tr>
      <th scope="row">Explain this error</th>
      <td>Produce text that fits "a competent person explaining an error"</td>
    </tr>
    <tr>
      <th scope="row">Translate this</th>
      <td>Produce text in the other language that fits the meaning</td>
    </tr>
    <tr>
      <th scope="row">Rewrite this email</th>
      <td>Produce text with the same meaning in a different tone</td>
    </tr>
  </tbody>
</table>
{% endcapture %}
{% include components/callout.html type="tip" title="Four tasks, one mechanism" body=four_tasks %}

That is why the same underlying model can summarise a contract, explain code and
draft a reply, without ever having been "trained to be an assistant".

### What it is not

- **It does not understand anything.** There is no moment where the meaning
  clicks. It is arithmetic over numbers, and the good outcome is that the
  arithmetic produces something that reads like understanding.
- **It does not look things up**, so it cannot check whether it is right.
- **It does not remember you between conversations.** Every new conversation
  starts from zero unless something outside the model writes notes down.
- **It is not magic and it is not a database.** It is a very large function that
  turns text into a guess.

## Part 2 — A little deeper, still simple

Now the mechanism, in the same plain language, one step at a time.

### Your text gets cut into tokens

A model does not read letters or whole words. The text is first cut into
<span class="term" data-term="token">tokens</span> by a
<span class="term" data-term="tokenizer">tokenizer</span>: chunks that are usually
a word, part of a word, or a piece of punctuation. This is why every AI product
prices things "per token".

Cutting is also lossy in an interesting way: **tokens are all the model ever
sees**. There are no letters inside the model, no words, no sentences. A model
literally cannot tell that "dog" and "dogs" share letters.

### Every token becomes a list of numbers

Each token is looked up in a table and becomes a long list of numbers — a few
hundred to a couple of thousand values. Those numbers are an
<span class="term" data-term="embedding">embedding</span>: a position in a space
of meaning, where things that behave similarly in language sit near each other.

This is the step that surprises people most: **the model's entire world is a
list of numbers.** No text, no images, no database, just arithmetic on those
numbers.

### It produces a probability for every possible next token

After reading your text, the model outputs a score for every token it knows, then
normalises those scores into probabilities that add up to 100%.

If you write *"The capital of France is"*, something close to this happens:

{% capture probs %}
<tbody>
  <tr><th scope="row">Paris</th><td data-value="94">94%</td></tr>
  <tr><th scope="row">located</th><td data-value="3">3%</td></tr>
  <tr><th scope="row">also</th><td data-value="1">1%</td></tr>
  <tr><th scope="row">a</th><td data-value="1">1%</td></tr>
  <tr><th scope="row">something else</th><td data-value="1">1%</td></tr>
</tbody>
{% endcapture %}
{% include components/chart.html body=probs chart="bar" unit="%" title="One answer, and a very long tail" sub="Illustrative distribution after 'The capital of France is'" note="Made-up numbers, chosen to show the shape rather than to measure a model: almost all the mass on one token, and a thin tail where the mistakes live. Real distributions differ per model and per wording." %}

The model is not choosing from a list of *answers*. It is choosing the next
chunk of text, and in this case every sensible continuation of that sentence
happens to be the answer. Sort the column and the tail becomes obvious: the
plausible-sounding wrong answers are all sitting in the last few percent.

### One of them gets picked — that is the only "choice"

A token with 94% is usually the one you get. It is not guaranteed, and that is
where the <span class="term" data-term="temperature">temperature</span> knob
lives:

- **Low temperature** → almost always the most likely token. Repetitive, dull,
  predictable. Good for code and for data.
- **High temperature** → the tail gets a chance to appear. More varied, more
  surprising, more likely to be nonsense.

So "creativity" in a language model is not a different brain. It is the same
arithmetic with the tails of the distribution allowed to speak. The step where
the choice is made is called
<span class="term" data-term="sampling">sampling</span>, and it belongs to the
software around the model, not to the model.

### The context window: it can only see the last N tokens

Everything the model knows about *your* conversation arrives in its input: the
instruction, the files you attached, the messages so far. The maximum size of
that input is the
<span class="term" data-term="context-window">context window</span>.

There is no memory behind it. When you scroll up, the model is not "recalling"
anything — the text is being re-sent every single time. Two consequences worth
internalising:

- A long conversation can push the beginning out of the window, and the model
  will behave as if it never happened.
- Filling the window is not free. Bigger inputs are slower and need more memory.
  The context window is a budget you spend, not a capacity you have.

### "Training" is just adjusting those numbers

A model starts as random numbers. Someone then
<span class="term" data-term="training">trains</span> it by showing it an enormous
amount of text and, after every fragment, adjusting each number slightly in the
direction that would have made the correct next token more likely. Repeat that for
months across thousands of machines and the random numbers produce fluent
language.

Nobody programs the grammar, the facts or the reasoning. They emerge from the
statistics of the text. That is also why a model can be confidently wrong: if the
pattern it learned is wrong, the output is wrong in exactly the same fluent way.

### Same idea, different computer

Nothing in the mechanism above requires a data centre. The numbers can live in a
server or in a file on your disk, and the
<span class="term" data-term="inference">inference</span> — the
generate-the-next-token loop — runs wherever those numbers are, on your
<span class="term" data-term="cpu">CPU</span> or your
<span class="term" data-term="gpu">GPU</span>.

What changes is only the context around it: which model, how big, how fast, and
what else needs the network. The honest version of that difference is in
[the privacy model](/privacy.html); what actually happens inside the box is in
[How O.A.S.I.S. works](/how-it-works.html).

## What changes when it runs on your PC

Three concrete things, no adjectives:

- The <span class="term" data-term="model">model</span> is a file on your disk,
  not a request to someone else's computer. Which model you run is your choice,
  and so is the [size of it](/models.html).
- Local features — chat, voice, memory, documents — run
  <span class="term" data-term="on-device">on your own hardware</span> and keep
  working with the network unplugged. Features that use the network communicate
  externally only when you use them. O.A.S.I.S. is
  <span class="term" data-term="offline-first">offline-first</span>, not
  network-blind.
- [Hardware](/requirements.html) becomes a real constraint instead of an
  abstraction. <span class="term" data-term="ram">RAM</span>,
  <span class="term" data-term="vram">VRAM</span> and disk space decide which
  models you can run at all.

If you want to see it rather than read about it, the [beta is free](/download.html)
and the [full feature list](/features.html) is one page long, on purpose.

{% capture faq %}
- **Does it understand what it is saying?**
  No. It produces text that fits the pattern of what understanding looks like.
  Whether that is "understanding" is a philosophy question, not an engineering
  one, and the honest engineering answer is that the mechanism has no database
  and no check.

- **Why is it sometimes wrong if it read so much?**
  Because reading gives it patterns, not facts. A pattern can be confidently
  wrong, and there is nothing inside the model to compare against.

- **Does a bigger model know more?**
  It holds more patterns, and it needs more memory and more time per answer.
  More is not the same as correct.

- **Where does the knowledge come from then?**
  From the text, weighted by how often things appeared. That is also why a model
  has a <span class="term" data-term="knowledge-cutoff">knowledge cutoff</span>:
  it knows nothing published after the newest text it saw.

- **What is quantization?**
  <span class="term" data-term="quantization">Quantization</span> compresses the
  numbers so the file is smaller and runs with less memory, at a small cost in
  quality. It is why a 4B model fits on a normal laptop.
{% endcapture %}
{% include components/details.html title="Questions people actually ask" faq="true" body=faq open-label="Open all" close-label="Close all" %}

## In short

- A language model predicts the next piece of text. Everything else is that
  ability in different clothes.
- It works on numbers, not on understanding, and it has no database to check
  itself against — which is why it can be fluently wrong.
- Whether it runs in a data centre or on your disk is a question of *where the
  numbers live*, not of how clever it is.

**Next in this series:** [What is a language model?](/blog/2026/09/25/what-is-a-language-model/)
— the same idea seen from the model file, the parameters and the names people
use for them.

<!--
Series: foundations
Number: 1 of 40
Next: 2026-09-25-what-is-a-language-model.md (ref: what-is-a-language-model)
Pillar page: /how-it-works.html (this article is the concept; the page is the product)
-->
