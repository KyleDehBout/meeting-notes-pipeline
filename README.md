# Meeting Notes Pipeline

A Claude Code pipeline that transforms raw meeting transcripts into polished, professionally formatted meeting notes — and gets better with every correction your supervisor makes.

## What it does

1. **`/process-notes`** — Drop a transcript in `transcripts/`, run the command. Four sub-agents format, sharpen, validate attributions, and apply your supervisor's preferences. A clean draft lands in `output/`.

2. **`/learn`** — Drop your supervisor's corrected version in `intake/`. The pipeline diffs it against what it produced, opens a browser review form, and proposes specific rule updates for you to approve or reject.

3. **`/apply-learning`** — Paste the form output back into Claude Code. Approved rules write directly to the right skill files. The file archives to `Meeting Notes/`. The system improves.

## How the pipeline improves over time

Every correction your supervisor makes becomes a rule. Rules accumulate in project-level skill files and a supervisor style guide. After enough repetitions, patterns promote to permanent hard rules. The pipeline that formats meeting #20 is meaningfully better than the one that formatted meeting #1.

## What you get per project

- A roster-aware attribution checker (no individual names in the Action column — ever)
- A living supervisor style guide that grows with each issued set of notes
- A pipeline memory log tracking approved and rejected rule changes
- Full data isolation — nothing from one transcript ever bleeds into another

---

## Setup

### Prerequisites
- [Claude Code](https://claude.ai/code) installed
- A GitHub account (optional, for version control)

### Install

1. Clone this repo and open it in Claude Code
2. **The setup form opens in your browser automatically** — this is the first-run rule, and it fires once per clone
3. Fill it in: project name, folder path, team roster, organisation names, and your document style defaults
4. Click **Generate setup block**, then **Copy to clipboard** or **Copy & close**
5. Paste the block back into Claude Code — setup runs from there with no further questions
6. Open your new project folder in Claude Code and you're live

The installer copies the global agents and commands into your `~/.claude/` directory and scaffolds your project folder from the template. It does not overwrite any existing files.

Optional: before filling in the form, upload a past `.docx` set of meeting notes to Claude Code. It reads your roster, organisation names, branding, and style out of the file and reopens the form with those fields already filled in and badged **Prefilled**.

### The first-run form

| | |
|---|---|
| Opens | Automatically, on the first Claude Code session after you clone |
| Fires again | Only if you delete `.claude/.setup-state.json`, or run `/setup-pipeline` by hand |
| Skip it | `MNP_SKIP_FIRST_RUN=1` |
| Wired in | `.claude/settings.json` → `SessionStart` → `scripts/first_run_check.py` |
| Form source | `assets/setup-form.html`, rendered to a gitignored `setup-session.html` |

The generated form is fully self-contained — no network, no CDN, works offline. Nothing is written to your project until you paste the block back into Claude Code, so you can close the tab and walk away at any point.

Setting up a second project later does not use the hook — run `/setup-pipeline` yourself and the same form opens.

---

## Repository structure

```
meeting-notes-pipeline/
├── assets/
│   └── setup-form.html    ← the first-run setup form
├── scripts/
│   ├── generate_setup_form.py   ← renders + opens the form
│   └── first_run_check.py       ← SessionStart hook: fires the form once per clone
├── global/
│   ├── commands/          ← installed to ~/.claude/commands/
│   │   ├── process-notes.md
│   │   ├── learn.md
│   │   └── apply-learning.md
│   └── agents/            ← installed to ~/.claude/agents/
│       ├── formatter.md
│       ├── editorial-qa.md
│       ├── discipline-checker.md
│       ├── supervisor-alignment.md
│       └── learning-reviewer.md
└── project-template/      ← copied and renamed per project
    ├── CLAUDE.md
    ├── supervisor-style-guide-[PROJECT].md
    ├── pipeline-memory-[PROJECT].md
    ├── meeting-notes-formatter-skill-[PROJECT].md
    ├── skills/
    │   ├── style-rules/
    │   ├── hard-rules/
    │   ├── humanizer/      ← vendored blader/humanizer + project scoping layer
    │   └── docx-renderer/
    └── transcripts/ output/ intake/ Meeting Notes/
```

---

## The document template

During setup you hand the pipeline one branded `.docx` — any past set of meeting notes or a
letterhead. From it, `/setup-pipeline` builds two things: a blank template carrying your
headers, footers and logo, and three reference files describing the exact XML your documents
use (column widths, fonts, numbering IDs, brand colour, tab stops).

**This happens once.** When setup finishes it writes
`Meeting Notes/skills/docx-renderer/references/.rendered.json`. Every later run — a second
`/setup-pipeline`, every `/process-notes`, anything else in the pipeline — sees that marker
and leaves all four files alone. `/process-notes` only ever reads them.

So once you are set up, those files are yours:

- **Change something** — edit the file in `references/` directly. Your edit is permanent.
- **Start over from a different `.docx`** — re-run setup with `--force`. This discards hand
  edits and re-derives everything.

The reference prose lives in `skills/docx-renderer/templates/` as `{{token}}` templates.
Setup substitutes your project's extracted values into them. Editing a template changes what
*future* projects get; editing a file in `references/` changes this project.

---

## Per-project setup (after install)

The installer scaffolds your project folder with placeholder content. Before running `/process-notes` for the first time, fill in:

1. **`meeting-notes-formatter-skill-[PROJECT].md`** — your document style profile: tone, structure, date format, column rules, typographic conventions. This is the most important file. Base it on a few past meeting notes you're happy with.

2. **`skills/style-rules/`** — preferred tone, action column format, status values, scope discipline.

3. **`skills/hard-rules/`** — non-negotiable rules: attribution, data isolation, output format. Add project-specific technical terminology to `references/terminology.md`.

   `skills/humanizer/` needs no setup. It ships complete and is project-independent.

4. **`supervisor-style-guide-[PROJECT].md`** — leave blank to start. It fills in automatically as you run `/learn` cycles. You can seed it manually with known preferences.

The pipeline's `supervisor-alignment` agent passes the draft through unchanged until 5 corrections are logged in the style guide — so there's no pressure to pre-fill it.

---

## The four-stage pipeline

| Stage | Agent | Job |
|---|---|---|
| 1 | `formatter` | Raw transcript → structured first draft |
| 2 | `editorial-qa` | Sharpen draft — remove filler, tighten wording, reorder by priority, then strip AI-writing tells |
| 3 | `discipline-checker` | Validate every Action column attribution against the project roster |
| 4 | `supervisor-alignment` | Apply documented supervisor preferences |
| 5 | `docx-renderer` | Render the final markdown to a formatted .docx |

---

## Humanizer

Stage 2 runs a second pass over the sharpened draft that removes signs of AI-generated
writing — inflated significance, promotional wording, `-ing` padding, AI vocabulary,
copula avoidance, filler, and chatbot artifacts.

It is vendored, not installed as a dependency. The upstream pattern list from
[blader/humanizer](https://github.com/blader/humanizer) (MIT) sits verbatim in
`skills/humanizer/references/`, and `skills/humanizer/SKILL.md` is the project-owned layer
that decides how it behaves in formal minutes:

- **Personality and voice-matching are off.** Minutes are reference documents. Flat and
  neutral is the target, not a defect to fix.
- **7 patterns are suppressed** because they fight the document format — boldface, inline-header
  lists, heading case, curly quotes, hyphenation, fragmented headers, and diff-anchored
  writing all belong to `typography.md` and `structure.md`.
- **6 patterns are constrained.** The em dash rule stops at prose and never touches date,
  time, or reference-number ranges. The passive-voice rule can never re-introduce a person
  as the actor, because the speaker-attribution hard rule outranks it. Rule-of-three never
  deletes a real item to break up a group of three.
- **Hard rules always win.** Where upstream says "name a real source", the pipeline cuts the
  claim or marks it `[not provided]`. Nothing enters the draft that is not in the transcript.

It runs at Stage 2 and nowhere else, so `discipline-checker` re-validates every attribution
afterwards and `supervisor-alignment` gets the last word on style. Both act as guardrails on
anything the rewrite breaks.

To update the vendored copy, drop the newer upstream `SKILL.md` into
`skills/humanizer/references/` with its version in the filename, reconcile any new pattern
numbers against the tables in `skills/humanizer/SKILL.md`, then bump `metadata.upstream`.
`/audit` reports the vendored version.

---

## Adapting to your style

The pipeline ships with a neutral, formal-professional style profile. It is not pre-configured for any particular industry, organisation, or document format.

Your style profile lives in `meeting-notes-formatter-skill-[PROJECT].md`. Edit it to match however your organisation formats its meeting notes — table structure, header layout, date conventions, wording register, whatever is standard for your context.

The skill files in `skills/` let you separate what is a hard rule (never violated) from what is a preference (applied when the supervisor guide is populated).

---

## Multiple projects

Each project gets its own copy of the project-template folder with its own roster, style guide, and memory log. The global commands and agents are shared across all projects. Running `/process-notes` in a project folder automatically uses that project's CLAUDE.md, skill files, and style guide.
