---
name: humanizer
description: >
  Scoped AI-writing cleanup for meeting notes. Use during editorial-qa (Stage 2) to strip
  LLM tells from draft prose — inflated significance, promotional wording, -ing padding,
  AI vocabulary, copula avoidance, filler, and chatbot artifacts. Loads
  references/humanizer-upstream-2.9.1.md for the full pattern definitions and examples.
  This file decides which patterns apply to formal minutes and which are switched off.
compatibility: Designed for use with the meeting-notes-pipeline
metadata:
  version: "1.0"
  upstream: "blader/humanizer 2.9.1 (MIT)"
allowed-tools: Read
---

## What this is

A scoping layer over the vendored `blader/humanizer` skill. The upstream pattern list lives
verbatim in `references/humanizer-upstream-2.9.1.md`. Read this file first — it tells you
which of the 33 patterns apply to meeting notes and which would damage the document.

Upstream is written mainly for blogs and essays. Meeting notes are reference documents.
Upstream itself says so: neutral and plain *is* the correct human voice for reference text.

## Mode — always embedded

Run upstream's draft → audit → final loop silently. Never output the draft, the audit
bullets, a pattern inventory, or a rewrite summary into the document. The pipeline wants
prose, not ceremony.

**PERSONALITY AND SOUL is off.** Never add stance, opinion, humour, asides, first person,
or "unresolved tension" to minutes.

**Voice Calibration is off.** The author voice for this document is defined by the formatter
skill and the supervisor style guide, not by a pasted writing sample.

## Precedence — highest wins

1. Hard rules skill — never overridden by anything below
2. Formatter skill and style-rules (including `references/typography.md` and
   `references/structure.md`)
3. Supervisor style guide
4. This file
5. Upstream humanizer defaults

If a humanizer pattern would change something the layers above specify, the pattern loses.
Silently. Do not flag it, do not argue for it in the draft.

## Rules that outrank every pattern

These come from the hard rules skill. A humanizer rewrite that breaks one of them is a defect,
even if the prose reads better.

- **No new facts.** Upstream's no-fabrication rule already says this. Here it is absolute:
  no name, organisation, date, number, drawing reference, or decision may enter the draft
  that is not in the current transcript. Where upstream says "name a real source" or "ask the
  user for the specific", the meeting-notes answer is: cut the claim or mark it `[not provided]`.
- **No speaker attribution.** Never rewrite toward "he said", "[Name] confirmed", or any
  variant, including as a way to fix passive voice.
- **No individual names in the Action column.** Organisation names only, exactly as they
  appear in CLAUDE.md.
- **Technical terms are frozen.** Terms in the hard rules `references/terminology.md` are
  reproduced exactly. They are never simplified, de-jargoned, or cycled for variety.
- **No content added or removed.** Humanizer rewords. It does not delete a substantive point
  or merge two items into one. Cutting *empty* prose is in scope; cutting *content* is
  editorial-qa's separate job, governed by its own rules.

## Active patterns

Apply these as written upstream. They are the reason this skill is in the pipeline.

| # | Pattern | Why it applies |
|---|---|---|
| 1 | Significance inflation | "marks a pivotal step in the project's evolution" is not a minute |
| 2 | Notability name-dropping | Trim padded lists back to what was actually discussed |
| 3 | Superficial -ing analyses | The single most common tell in generated minutes |
| 4 | Promotional language | Minutes record, they do not sell |
| 6 | Formulaic challenges sections | Prevents an invented "Challenges" or "Next Steps" block |
| 7 | AI vocabulary | Highest-value pattern here: crucial, key, robust, leverage, align with, ensure, streamline |
| 8 | Copula avoidance | "serves as / represents / boasts" → "is / has" |
| 9 | Negative parallelisms and tailing negations | "not just X, it's Y" has no place in a record |
| 12 | False ranges | "from scheduling to procurement" when the two are unrelated |
| 18 | Emojis | Should never reach the draft; strip on sight |
| 20 | Chatbot artifacts | "I hope this helps", "Let me know if you'd like…" |
| 21 | Cutoff disclaimers and speculative gap-filling | Reinforces the hard rule: mark `[not provided]`, never guess |
| 22 | Sycophantic tone | No "Great progress!" in a status column |
| 23 | Filler phrases | "in order to" → "to", "due to the fact that" → "because" |
| 25 | Generic positive conclusions | Directly reinforces the hard rule against unsourced closing remarks |
| 27 | Persuasive authority tropes | "At its core, what really matters is…" |
| 28 | Signposting and announcements | "Let's look at the next item" |
| 31 | Manufactured punchlines and staccato drama | Minutes do not need a closer |
| 32 | Aphorism formulas | "Coordination is the currency of delivery" |
| 33 | Conversational rhetorical openers | "Honestly?", "Here's the thing" |

## Modified patterns

Apply the pattern, but with the constraint below. The constraint wins.

**#5 Vague attributions.** Upstream says name a real source or cut. In minutes you may only
attribute to an organisation already listed in the current transcript's attendees. You may
never introduce a source to fix a vague claim. If the attribution cannot be grounded in the
transcript, cut the attribution and keep the fact, or mark it `[not provided]`.

**#10 Rule of three.** Applies only to *rhetorical* triads the draft invented for rhythm.
If the transcript records three items, all three stay. Never delete a real item to break up
a group of three.

**#11 Synonym cycling.** Collapse to one term — but the term you keep must be the one used in
the transcript, and never a substitute for a frozen technical term. Repetition of a technical
term is correct and expected.

**#13 Passive voice.** De-passivise only when the actor is an organisation already named in
the item, or when the sentence works in active voice without naming anyone. If fixing the
passive would require naming a person, leave it passive. The speaker-attribution hard rule
outranks this pattern every time.

**#14 Em and en dashes.** Prose only. Strip em dashes (—), spaced em dashes, and double
hyphens from sentence text. **Do not touch** en dashes inside date ranges, time ranges,
numeric or dimension ranges, drawing and reference numbers, or anything `typography.md`
specifies. If `typography.md` states a dash convention, that convention wins outright.

**#24 Excessive hedging.** Remove only hedging the draft added. Hedged language that reflects
what was actually said ("may be able to confirm by Friday") is the record and stays. When
unsure whether a hedge came from the transcript or the draft, keep it.

## Suppressed patterns — do not apply

Each of these fights a document convention the pipeline deliberately sets.

| # | Pattern | Why it is off |
|---|---|---|
| 15 | Boldface overuse | `typography.md` defines bold for header block, section titles, and labels |
| 16 | Inline-header vertical lists | Bullet lists inside table cells are a specified format |
| 17 | Title case in headings | Heading case belongs to `typography.md` and the formatter skill |
| 19 | Curly quotation marks | The output is DOCX; smart quotes are correct there |
| 26 | Hyphenated word pairs | Risks corrupting technical terms and reference numbers for near-zero gain |
| 29 | Fragmented headers | `structure.md` owns section layout and lead lines |
| 30 | Diff-anchored writing | Minutes legitimately reference prior status and what changed since last meeting |

## False positives — leave these alone

Upstream's false-positive list applies in full. Two additions specific to minutes:

- **Repetition is not synonym-poverty.** Formal minutes repeat organisation names, status
  values, and technical terms by design. That is correct, not a tell.
- **Flat, uniform, unemotional prose is the target state here**, not a defect. Do not add
  rhythm, variety, or personality to compensate.

## Output contract

Return the revised draft only. No preamble, no pattern list, no before/after.

Add one line at the very bottom for the orchestrator's summary, in this exact form:

```
HUMANIZER NOTE: applied patterns [numbers]; [N] rewrites; [N] suppressed by precedence.
```

This line is metadata. It is stripped before the document is rendered and never reaches
the DOCX.

## Updating the vendored copy

`references/humanizer-upstream-2.9.1.md` is a verbatim copy of `SKILL.md` from
https://github.com/blader/humanizer (MIT). To move to a newer release, add the new file
alongside the old one with its version in the filename, review any new pattern numbers
against the tables above, then delete the old file and bump `metadata.upstream` here.
Never edit the vendored file in place — all local policy belongs in this file.
