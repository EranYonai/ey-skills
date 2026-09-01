# ey-skills

Open-source skill definitions for AI coding agents.

## Skills

### `/todo` — Persistent Task Management

A markdown-based TODO system that the AI agent maintains for you.
Designed for people who've tried every TODO app and given up.

**How it works:**
- Tasks live in `~/.todo/TODO.md` — one flat file, always
- Agent reads it every session, surfaces what matters
- Completed tasks auto-archive to `DONE.md` and quarterly files
- Built-in staleness detection, reorg, and priority management
- Zero maintenance from the user — the agent does the bookkeeping

**Quick start:** Copy `todo/SKILL.md` into your agent's skill/instruction set.
The agent will initialize `~/.todo/` on first run.

See [`todo/SKILL.md`](todo/SKILL.md) for the full specification.

### `notepad` — AI Note Enhancement

A Granola-style notepad. You type scrappy, fragmentary notes; the agent turns
them into structured, polished notes while preserving every word you wrote
verbatim in a `## Raw` block.

**How it works:**
- On first use, the agent asks where to store notes — an existing Obsidian
  vault, any folder you choose, or a default (`~/Documents/notepad-ai`)
- The choice is remembered in `~/.config/ai-notepad/config` — no hardcoded paths
- One markdown file per note, catalogued in `INDEX.md` (newest-first, capped)
- Optional transcript merging: anchors define what you cared about, the
  transcript fills in the detail you didn't write down
- Works with plain markdown anywhere; uses Obsidian wikilinks/callouts/Bases
  when the backend is a vault

**Quick start:** Copy `notepad/SKILL.md` (and `notepad/templates/`) into your
agent's skill set. The agent runs first-run setup the first time you save a note.

See [`notepad/SKILL.md`](notepad/SKILL.md) for the full specification.

### `engineering-review` - Evidence-Backed Reviewer Judgment

Learn how real engineers review code from historical GitLab or GitHub feedback,
then apply that learned judgment without confusing preferences with defects.

**How it works:**
- Collects substantive review discussions into atomic evidence events
- Builds separate reviewer, team-principle, convention, and code-surface concepts
- Preserves disagreements, uncertainty, evidence gaps, and self-labeled severity
- Runs learned judgment alongside an independent correctness and security pass
- Keeps raw review evidence local and gitignored

The repository contains only the generic workflow and collection/analysis
tools. It includes no corpus, principles, reviewers, surfaces, or learned model.

**Quick start:** Copy the `engineering-review/` directory into your agent's skill
set, then follow [`engineering-review/modes/learn.md`](engineering-review/modes/learn.md)
to build a model from your own review history.

See [`engineering-review/SKILL.md`](engineering-review/SKILL.md) for the full
workflow.

## Philosophy

These skills follow a few principles:

1. **Zero friction** — if the user has to remember to do something, the system has failed
2. **Flat files** — markdown that works with grep, git, and any editor
3. **Agent-maintained** — the AI does the bookkeeping, the human does the thinking
4. **Bounded growth** — every file has a cap, archives are automatic
5. **Grep-friendly** — consistent tokens (`[P0]`, `T-042`, `[x]`) that tools can find

## License

MIT
