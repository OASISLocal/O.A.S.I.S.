---
title: "What is AI? And how does it work?"
ref: what-is-ai-and-how-it-works
lang: en
tags: [basics]
excerpt: "What AI actually is, in two levels: the simple version (it predicts the next word) and a slightly deeper one (tokens, probabilities and context)."
---

There is a lot of noise around "artificial intelligence". This article is
deliberately quiet. It explains what a <span class="term" data-term="llm">language
model</span> does, in two passes: the first one is the whole idea in plain
language, the second goes one level deeper and still stops short of maths.

Read the first part and you are done. The second part is there for the curious.

## Part 1 — In one minute

### It is autocomplete, with a very long memory

You know the feeling. You type half a sentence into a messaging app and it
offers you the rest of the word. That is all a language model does, except the
version you use every day without noticing has read a few hundred billion
sentences, and instead of guessing one word it guesses the next *piece of a
sentence*, over and over, until it has written something.

That is the entire trick. There is no second hidden mechanism.

### It predicts; it does not look things up

This is the part that surprises people. The model has no database of facts
inside it, no list of countries with their capitals, no notes about you. It has
a set of numbers — tens of billions of them — which encode the *patterns* of
language: how words tend to follow each other, which sentences are plausible,
which are nonsense.

When it tells you a fact, it is not reading it from a table. It is producing
text that fits the pattern. Often that is exactly right. Sometimes it is not,
and the result is a sentence that is fluent, confident and wrong. We have a name
for that, and this Journal has a whole article about it later on.

### Why that is enough to be useful

If the only skill is "continue this text well", how does that become an
assistant? Because almost every task you would ask a machine is a text-shaped
task:

- *Summarise this PDF* → produce a shorter version that keeps the important parts.
- *Explain this error* → produce text that fits "a competent person explaining an error".
- *Translate this* → produce text in the other language that fits the meaning.
- *Rewrite this email* → produce text with the same meaning in a different tone.

Each of those is a continuation task wearing a different hat. That is why the
same underlying model can summarise a contract, explain code and draft a reply,
without ever having been "trained to be an assistant".

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
<span class="term" data-term="token">tokens</span>: chunks of text that are
usually a word, or a part of a word, or a piece of punctuation. This is the
work of a *tokenizer*, and it is why every AI product prices things "per
token".

Cutting the text is also lossy in an interesting way: **tokens are all the
model ever sees**. There are no letters inside the model, no words, no
sentences. A model literally cannot tell that "dog" and "dogs" share letters,
unless that relationship was already captured when the text was converted.

### Every token becomes a list of numbers

Each token is looked up in a table and becomes a long list of numbers — a few
hundred to a couple of thousand values. Those numbers are an *embedding*: a
position in a space of meaning, where things that behave similarly in language
sit near each other.

This is the step that surprises people most: **the model's entire world is a
list of numbers.** No text, no images, no database, just arithmetic on those
numbers. Everything a language model knows about the world is stored as
geometry in that space.

### It produces a probability for every possible next token

After reading your text, the model outputs a number for every token it knows —
a score for "how likely is this to come next". Those scores get normalised
into probabilities, so they add up to 100%.

If you write *"The capital of France is"*, something close to this happens:

| Candidate | Probability |
|---|---|
| Paris | 94% |
| located | 3% |
| also | 1% |
| a | 1% |
| something else | 1% |

The model is not choosing from a list of *answers*. It is choosing the next
chunk of text, and in this case every sensible continuation of that sentence
happens to be the answer.

### One of them gets picked — that is the only "choice"

A **token** with 94% is usually the one you get. But it is not guaranteed, and
that is where the famous temperature knob lives:

- **Low temperature** → almost always the most likely token. Repetitive, dull,
  predictable. Good for code and for data.
- **High temperature** → the tail gets a chance to appear. More varied, more
  surprising, more likely to be nonsense.

So "creativity" in a language model is not a different brain. It is the same
arithmetic with the tails of the probability distribution allowed to speak.

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
- Filling the window is not free. Bigger inputs are slower and need more
  memory. The context window is a budget you spend, not a capacity you have.

### "Training" is just adjusting those numbers

A model starts as random numbers. Someone then shows it an enormous amount of
text and, after every fragment, adjusts each number slightly in the direction
that would have made the correct next token more likely. Repeat that for months
across thousands of machines and the random numbers become something that
produces fluent language.

Nobody programs the grammar, the facts or the reasoning. They emerge from the
statistics of the text. That is also why a model can be confidently wrong: if
the pattern it learned is wrong, the output is wrong in exactly the same
fluent way.

### Same idea, different computer

Nothing in the mechanism above requires a data centre. The numbers can live in
a server or in a file on your disk, and the
<span class="term" data-term="inference">inference</span> — the
generate-the-next-token loop — runs wherever those numbers are.

What changes is only the context around it: which model, how big, how fast, and
what else needs the network. The honest version of that difference, feature by
feature, is in [the privacy model](/privacy.html); and the part that actually
happens inside the box is in [How O.A.S.I.S. works](/how-it-works.html).

## What changes when it runs on your PC

Three concrete things, no adjectives:

- The <span class="term" data-term="model">model</span> is a file on your disk,
  not a request to someone else's computer. Which model you run is your choice,
  and so is the [size of it](/models.html).
- Local features — chat, voice, memory, documents — run on your own processor
  and keep working with the network unplugged. Features that use the network
  communicate externally only when you use them. O.A.S.I.S. is offline-first,
  not network-blind.
- [Hardware](/requirements.html) becomes a real constraint instead of an
  abstraction. RAM, VRAM and disk space decide which models you can run at all.

If you want to see it rather than read about it, the [beta is free](/download.html)
and the [full feature list](/features.html) is one page long, on purpose.

## In short

- A language model predicts the next piece of text. Everything else is that
  ability in different clothes.
- It works on numbers, not on understanding, and it has no database to check
  itself against — which is why it can be fluently wrong.
- Whether it runs in a data centre or on your disk is a question of *where the
  numbers live*, not of how clever it is.

**Next in this series:** *What is a language model (LLM)?* — the same idea seen
from the model file, the parameters and the names people use for them. It is
being written now; the [Journal index](/blog/) lists what is already out.

<!--
Series: foundations
Number: 1 of 40
Next: 2026-09-25-what-is-a-language-model.md (ref: what-is-a-language-model)
Pillar page: /how-it-works.html (this article is the concept; the page is the product)
-->
