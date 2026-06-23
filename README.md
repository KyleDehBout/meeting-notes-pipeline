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
2. Run `/setup-pipeline`
3. Answer the prompts — project name, folder path, team roster, organisation names
4. Open your new project folder in Claude Code and you're live

The installer copies the global agents and commands into your `~/.claude/` directory and scaffolds your project folder from the template. It does not overwrite any existing files.

---

## Repository structure

```
meeting-notes-pipeline/
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
    │   └── hard-rules/
    └── transcripts/ output/ intake/ Meeting Notes/
```

---

## Per-project setup (after install)

The installer scaffolds your project folder with placeholder content. Before running `/process-notes` for the first time, fill in:

1. **`meeting-notes-formatter-skill-[PROJECT].md`** — your document style profile: tone, structure, date format, column rules, typographic conventions. This is the most important file. Base it on a few past meeting notes you're happy with.

2. **`skills/style-rules/`** — preferred tone, action column format, status values, scope discipline.

3. **`skills/hard-rules/`** — non-negotiable rules: attribution, data isolation, output format. Add project-specific technical terminology to `references/terminology.md`.

4. **`supervisor-style-guide-[PROJECT].md`** — leave blank to start. It fills in automatically as you run `/learn` cycles. You can seed it manually with known preferences.

The pipeline's `supervisor-alignment` agent passes the draft through unchanged until 5 corrections are logged in the style guide — so there's no pressure to pre-fill it.

---

## The four-stage pipeline

| Stage | Agent | Job |
|---|---|---|
| 1 | `formatter` | Raw transcript → structured first draft |
| 2 | `editorial-qa` | Sharpen draft — remove filler, tighten wording, reorder by priority |
| 3 | `discipline-checker` | Validate every Action column attribution against the project roster |
| 4 | `supervisor-alignment` | Apply documented supervisor preferences |

---

## Adapting to your style

The pipeline ships with a neutral, formal-professional style profile. It is not pre-configured for any particular industry, organisation, or document format.

Your style profile lives in `meeting-notes-formatter-skill-[PROJECT].md`. Edit it to match however your organisation formats its meeting notes — table structure, header layout, date conventions, wording register, whatever is standard for your context.

The skill files in `skills/` let you separate what is a hard rule (never violated) from what is a preference (applied when the supervisor guide is populated).

---

## Multiple projects

Each project gets its own copy of the project-template folder with its own roster, style guide, and memory log. The global commands and agents are shared across all projects. Running `/process-notes` in a project folder automatically uses that project's CLAUDE.md, skill files, and style guide.
