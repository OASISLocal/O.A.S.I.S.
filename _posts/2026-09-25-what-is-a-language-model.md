---
title: "What is a language model?"
ref: what-is-a-language-model
lang: en
tags: [basics]
excerpt: "Where a language model gets its ability, what the billions of numbers inside it actually are, and the three questions that explain most of its behaviour."
reading_minutes: 6
---

[Last time](/blog/2026/09/25/what-is-ai-and-how-it-works/) we went as deep as "it predicts the next piece of text". That is true and it is also the beginning rather than the end, because three questions come up immediately afterwards:

1. Where does that ability come from?
2. What is actually inside the model?
3. And why does it behave the way it does?

This article answers those three. It assumes nothing.

## Part 1 — The short version

### It comes from reading. An enormous amount of it.

A language model is trained on text: books, web pages, code, forums, manuals,
transcripts. Not by being taught rules, but by being shown examples and
adjusted, slightly, millions of times, whenever its guess was wrong.

The result is not a database of sentences. It is a set of numbers that encode
how language tends to behave. The model never stores "the capital of France is
Paris" as a fact it can look up. It stores a shape that makes *that* likely.

### The model is the numbers, and the numbers are the model

Inside a language model there are no words. There is no letter, no sentence, no
image, no database. There is a list of numbers — billions of them, in a file on
your disk, usually a few gigabytes.

Those numbers are called **parameters**. They are what the training adjusted.
They are the whole thing.

### Three behaviours fall out of that, and nothing more

| What you see | What it actually is |
|---|---|
| It "knows" facts | The pattern it learned happens to fit those facts |
| It "forgets" in a long chat | The beginning left its input window |
| It sometimes invents | The most fluent continuation is not the truest one |

None of these are mysteries once you accept there is no database and no
memory. There is a function over numbers, called over and over, one token at a
time.

The vocabulary is fixed and finite, so the model is really choosing among
finitely many next words. It picks the one that best continues the pattern, and
that word can be a strange one.

## Part 2 — One level deeper, still plain language

### Training: adjusting a guess, millions of times

Take a sentence. Cover the last word. Ask the model to guess it. It guesses,
and the guess is wrong, or right, or close.

Here is the whole training loop:

1. Show the model a chunk of real text.
2. It produces a guess for every possible next token.
3. Measure how wrong the guesses were. That distance from the truth is the key
   thing training tries to make smaller.
4. Nudge every parameter a tiny amount in the direction that would have
   improved the guess.
5. Do this again, on a different chunk, on thousands of machines at once, for
   weeks.

Nobody writes the grammar, the facts, or the reasoning. All of it emerges from
the statistics of the text, which is why the model can be fluently wrong: if
the pattern it learned is wrong, the output is wrong in exactly the same
fluent way.

One consequence worth knowing: the training data is a photograph of a moment.
A model cannot know anything published the day it was trained, and it cannot
know what happened last Tuesday.

### Parameters and the model file

The parameters, plus the vocabulary, plus a bit of configuration, are stored as
a **model file**. That is the whole artifact.

The practical consequence: choosing which model runs is choosing which file is
loaded onto your disk. You can delete it, move it, try another one, and run it
with the network unplugged. Nothing is fetched at query time.

### Tokens: the alphabet it actually works with

Before text reaches the model it is cut into **tokens**: chunks that are usually
a word, a part of a word, or a piece of punctuation. A tokenizer does the
cutting, and it is why every AI product prices things "per token".

Two things follow:

- A token is not a character. The model cannot see spelling. It cannot notice
  that a word and its plural share letters.
- Cutting is lossy in a way that matters: common words are one token, unusual
  names are several, and the cost of a request follows the split.

### Context: the only thing it can see

Everything it knows about your conversation arrives in its input: the
instruction, the files you attached, the messages so far. The maximum size of
that input is the **context window**.

There is nothing behind it. When you scroll up, nothing is recalled, because
the text is being sent again every single time. A long conversation can push
the beginning out of the window, and the model will then behave as if it never
happened.

The usual fix is not a bigger window. It is writing things down: notes, a
summary, a file. That is not a trick, it is just how the mechanism works.

{% capture chart_sizes %}
<tbody>
  <tr><th scope="row">1.5B params</th><td data-value="1.0">1.0</td></tr>
  <tr><th scope="row">3B params</th><td data-value="2.0">2.0</td></tr>
  <tr><th scope="row">4B params</th><td data-value="2.5">2.5</td></tr>
  <tr><th scope="row">8B params</th><td data-value="4.8">4.8</td></tr>
</tbody>
{% endcapture %}
{% include components/chart.html body=chart_sizes chart="bar" unit=" GB" title="A bigger model is a bigger file" sub="Q4 quantization, the profiles the app ships with" note="Declared download sizes of the quantized files, not measured benchmarks. The exact figures come from each model's own file, and they change with the quant." %}

A model that learns from more parameters holds more patterns. It does not
automatically become more correct. It becomes heavier first, and the download
you can see is the price of that.

If you are wondering what a specific file weighs, the
[models page](/models.html) lists the profiles the app ships with, and
[requirements](/requirements.html) covers how much RAM and VRAM each of them
needs to load.

### Sampling: the one place where choice enters

The model outputs a probability for every token. Then one is chosen. That choice
is a decision the application makes, not the model, and it is what people mean
when they talk about a model's "creativity":

- **Low temperature** takes almost always the most likely token. Dull, safe,
  right for code and for data.
- **High temperature** lets the unlikely tail speak. More surprising, more
  varied, more likely to be nonsense.

The model itself has no opinion about which is better. That is a decision the
software around it makes, and it is why the same model behaves differently in
two applications.

## So why does it behave like that?

Because every behaviour people find surprising has the same explanation: there
is a pattern, and no lookup table.

- **It cannot check itself.** It has nothing to check against.
- **It repeats itself** when the temperature is low and the pattern is strong.
- **It invents citations** because a plausible citation is a plausible
  continuation.
- **It forgets across sessions** because nothing is written down unless
  something writes it down.

None of that is a bug list. It is the same list of consequences.

## In short

- A language model is a list of numbers, adjusted by reading an enormous amount
  of text until its guesses got good enough.
- There is no database inside, so there is nothing to look up and nothing to
  check itself against.
- Its behaviour follows from three facts: it predicts, it only sees what is in
  its input, and it chooses among a fixed vocabulary.
- Which model runs is which file is on your disk. That is why it can work with
  the network unplugged.

**Next in this series:** *Tokens and the context window* — the mechanism behind
cost, length limits and the strange way a long conversation forgets its own
beginning. It is being written now; the
[Journal index](/blog/) lists what is already out.

<!--
Series: foundations
Number: 2 of 40
Next: tokens-and-the-context-window (ref: tokens-and-the-context-window)
Pillar page: /models.html (this article is the concept; the page is the product)
-->
