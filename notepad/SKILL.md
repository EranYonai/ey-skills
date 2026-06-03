---
name: AI Notepad Skill
description: AI enhanced note taking, notepad AI.
---
# AI Notepad Skill

A Granola-style note enhancement system for AI agents. You type scrappy,
fragmentary notes — the agent turns them into structured, polished notes while
preserving every word you wrote.

Notes live in a plain directory of **your** choosing: an existing Obsidian
vault, any folder you like, or a sensible default. The agent figures out where
on first run and remembers it.

Inspired by [Granola](https://granola.ai): raw notes in, polished notes out,
with optional transcript merging.

## Progressive disclosure — read more only when needed

This file is the always-loaded core. Two reference files are read **on demand**:

- **First use only** (no config file yet) or on `notepad: setup` →
  read [`references/setup.md`](references/setup.md).
- **Obsidian backend only** (`NP_BACKEND=obsidian`) →
  read [`references/obsidian.md`](references/obsidian.md) for wikilinks,
  callouts, and the optional `Notes.base` view.

For a plain directory backend you never need `obsidian.md`.

---

## Overview

```
$NP/                                               <- your notepad directory (from config)
  INDEX.md                                         <- catalog of all notes (cap ~200 rows)
  2026-05-27 - Interview with Ido.md               <- one file per note (in root)
  2026-05-28 - 1-1 with Shaked - Infra roadmap.md
  archive/
    2026-Q1.md                                     <- INDEX overflow rows only
```

Notes live **directly in the directory root**, not in a subfolder. The same
markdown works everywhere; an Obsidian backend additionally gets wikilinks,
callouts, and an optional `Notes.base` (see `references/obsidian.md`).

---

## Storage Location (`$NP`)

The notepad has **no hardcoded path**. Resolve it at the start of every
operation:

```bash
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/ai-notepad/config"
if [ -f "$CONFIG" ]; then
  . "$CONFIG"          # defines NP and NP_BACKEND
else
  : # not configured → read references/setup.md and run First Run
fi
```

`$NP` is the resolved directory; `$NP_BACKEND` is `obsidian` or `plain`. If the
config is absent, read [`references/setup.md`](references/setup.md) and run the
First Run flow before saving anything.

**Important:** all note `.md` files live in the **root** of `$NP`, alongside
`INDEX.md`. There is no `notes/` subfolder.

---

## Note Schema

Each note is a standalone markdown file with YAML frontmatter.

### Frontmatter

```yaml
---
id: N-017
title: Intro call — AllFound
date: 2026-05-27 14:32
attendees: Jim, Michaela, +5
tags:
  - notepad-ai
  - sales
  - discovery
transcript: yes
---
```

| Field | Required | Notes |
|-------|----------|-------|
| id | Yes | `N-NNN`, auto-assigned from INDEX Memory |
| title | Yes | Agent infers from raw notes or asks |
| date | Yes | `YYYY-MM-DD HH:MM`, set by agent on creation |
| attendees | No | Free text |
| tags | Yes | YAML list. ALWAYS include `notepad-ai` as the first tag. |
| transcript | Yes | `yes` or `no` |

**Tags must be a YAML list** (not comma-separated). The `notepad-ai` tag is
mandatory on every note — grep filters and Obsidian views rely on it.

### Body Sections

Notes use blockquote callouts for emphasis (TL;DR, decisions) and plain `##`
headers for content. In Obsidian these render as styled callouts; elsewhere
they're ordinary blockquotes.

```markdown
# Intro call — AllFound

#sales

> [!abstract] TL;DR
> Discovery call with AllFound (100 employees). Currently on Tuesday.ai at $180/employee/year — too manual, too expensive. Replacing it is a Q2 priority.

## AllFound Overview
- 100 employees, adding 20 more next quarter
- Currently using Tuesday.ai

## Current Provider
- $180 per employee per year — "too expensive"
- Too manual

> [!check] Decisions
> - Replacing Tuesday.ai is a Q2 priority

## Action Items
- [ ] @me — Send pricing comparison
- [ ] @jim — Schedule follow-up demo

## Open Questions
- HIPAA requirements?

---
## Raw
<!-- NEVER edit below this line. Verbatim user input preserved here. -->
```
100, growing
use tuesday.ai, v manual
180
"a priority for q2"
```

<!-- transcript: ./2026-05-27 - Intro call — AllFound.transcript.txt -->
```

Rules for sections:

- **Empty sections are omitted.** Only include sections that have content.
- **Section headers can be customized.** Prefer content-driven headers (e.g.
  "Current Provider") over generic ones. Generic headers are a fallback.
- **Use callouts for highlights.** TL;DR → `> [!abstract]`, decisions →
  `> [!check]`, warnings → `> [!warning]`.
- **`## Raw` is sacred.** The agent NEVER modifies content below this line. It
  is the user's verbatim input, preserved exactly as typed.

### Filename Convention

```
YYYY-MM-DD - {Title}.md
```

- Date prefix uses **the day only** (no time component).
- Keep the human-readable title; strip filesystem-illegal chars (`/`, `:`,
  `\`, null) and replace em-dashes with ` - ` for cross-platform safety.
- Example: `"1:1 with Shaked — Infra team roadmap"` →
  `2026-05-28 - 1-1 with Shaked - Infra team roadmap.md`

```bash
SAFE_TITLE=$(printf '%s' "$TITLE" | sed 's/:/-/g; s/\//-/g; s/\\/-/g; s/—/-/g' | tr -s ' ')
FILE="$NP/$(date +%Y-%m-%d) - ${SAFE_TITLE}.md"
```

If a file with that name already exists, append ` (2)` before the `.md`.

### Transcript Storage

- Save provided transcripts as a sibling file in the root:
  `$NP/2026-05-27 - Intro call - AllFound.transcript.txt`
- Reference it from the note's `## Raw` section as an HTML comment.
- **Never inline a transcript in the .md file** — they can be 50KB+. They live
  in their own file and the agent reads them on demand.

---

## INDEX.md Schema

`INDEX.md` lives at `$NP/INDEX.md`. The `File` column links to each note:
**plain backend** uses a relative markdown link `[title](./name.md)`;
**Obsidian backend** uses a wikilink `[[name]]` (see `references/obsidian.md`).

```markdown
---
title: Notepad AI Index
tags:
  - notepad-ai
  - index
---

# Notepad AI

| ID | Date | Title | Tags | File |
|----|------|-------|------|------|
| N-017 | 2026-05-27 | Intro call — AllFound | sales, discovery | [Intro call - AllFound](./2026-05-27 - Intro call - AllFound.md) |

---
## Memory
<!-- Agent: read this on notepad invocation. -->
**Next ID:** N-018
**Notes count:** 17
**Last archive:** 2026-04-01
```

- **Newest-first.** New rows go immediately after the table header separator.
- **Cap 200 rows.** When exceeded, oldest rows roll to `archive/YYYY-QN.md`.
  Note *files* are never moved or deleted — only INDEX rows archive.
- **Memory footer** tracks the next ID counter and metadata.
- Never use `notes/...md` paths — notes live in the root.

---

## Agent Behavior

### 1. Capture — Creating a Note

Conversational. The user sends raw notes; the agent enhances them.

**Trigger:** `notepad: ...`, `take a note`, `note: ...`, or a pasted block
clearly meant to be saved.

```
User:  notepad: intro w/ allfound
       100, growing
       use tuesday.ai, v manual
       180
       "a priority for q2"

Agent: [resolve $NP from config; if absent → read references/setup.md, run First Run]
       Got it. Transcript to merge? (paste it, point me at a file, or say "no")

User:  no

Agent: [enhance → write note in $NP root → update INDEX → bump Next ID]
       Saved N-017 → 2026-05-27 - Intro call - AllFound.md
       ...
       Want anything pulled out? (follow-up email / action items / questions)
```

If a transcript is provided: save it to a sibling `.transcript.txt`, set
`transcript: yes`, and enhance using both raw notes and transcript.
If *only* a transcript is provided: summarize it directly; set `## Raw` to
`(none — transcript only)`.

### 2. Enhancement Rules

The Granola model adapted for text:

> 1. **Anchors are sacred.** Every line/fragment the user wrote is an *anchor*.
>    Each MUST appear in the enhanced output — expanded, never dropped, never
>    silently merged.
> 2. **Transcript fills the gaps.** For each anchor, find the surrounding
>    discussion in the transcript and expand it into a detailed bullet.
> 3. **Theme over template.** Group anchors into `##` sections by theme; infer
>    titles from content. Fall back to TL;DR / Key Points / Decisions / Action
>    Items only when content doesn't suggest better structure.
> 4. **Preserve exact words** for quotes and specific terms. Non-English
>    fragments stay verbatim in `## Raw`; translate/paraphrase in the enhanced
>    section and flag uncertainty.
> 5. **Numbers, names, dates are load-bearing.** Never alter them.
> 6. **No invention without transcript.** Ambiguous anchors stay terse, e.g.
>    `- $180 (per seat? annual? — unclear from notes)`.
> 7. **TL;DR is 2-3 sentences in a `> [!abstract]` callout.** Action items use
>    `- [ ] @owner — task`. Omit empty sections.
> 8. **Write in the user's voice.** Concise bullets; match their register.

### 3. Ask Your Notes — Querying

Search across all notes in `$NP` (root, exclude `INDEX.md` — see Grep Patterns).

```
User:  what was allfound's budget?
Agent: [grep matching notes → read → answer with note id + date]

User:  which notes mention auth?
Agent: [grep → list matches with one-line context]

User:  write a follow-up email for N-017
Agent: [read note + transcript → draft inline; does NOT save unless asked]
```

### 4. List & Find

| User says | Agent does |
|-----------|------------|
| `notes` / `list notes` | Show recent ~20 from INDEX.md |
| `notes about sales` | Grep `$NP/*.md` (excluding INDEX) + matching INDEX rows |
| `notes this week` | Filter INDEX by date column ≥ start of week |
| `open N-017` / `show N-017` | Read and display the full note |
| `re-enhance N-017` | Re-read `## Raw` (+ transcript), regenerate above `## Raw`; Raw untouched. **Warn before overwriting** hand edits. |
| `delete N-017` | Remove note file + INDEX row. Confirm first. |
| `tag N-017 sales urgent` | Update `tags:` list (keep `notepad-ai` first) + INDEX row |
| `notepad: setup` / `move notepad` | Read `references/setup.md`, re-run First Run |

### 5. Continuing a Note (Append)

```
User:  append N-017: they also mentioned needing HIPAA compliance
       budget approved by CFO already
Agent: [read N-017 → append to ## Raw → re-enhance top half]
```

Append flow: read `## Raw`, append new text (blank-line separator +
`<!-- appended YYYY-MM-DD -->`), re-enhance the whole note from the updated Raw
block (+ transcript), write back.

---

## Shell Operations

**Critical rule:** When updating INDEX.md, use shell commands — do NOT rewrite
the file by reading and reconstructing it. This prevents accidental row edits.

All commands are macOS-compatible (BSD awk/sed). Every snippet assumes `$NP` is
resolved from config:

```bash
CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/ai-notepad/config"
[ -f "$CONFIG" ] && . "$CONFIG"   # defines NP, NP_BACKEND
```

**Glob hygiene** — notes live in the root; exclude `INDEX.md`:

```bash
for f in "$NP"/*.md; do
  [ "$(basename "$f")" = "INDEX.md" ] && continue
  # ... operate on $f
done
```

### Prepend INDEX row (newest-first)

Insert the new row right after the table header separator. The `File` cell uses
a relative markdown link for plain backends (for Obsidian wikilinks, see
`references/obsidian.md`):

```bash
sed -i '' "/^|----|------|-------|------|------|$/a\\
| N-017 | 2026-05-27 | Intro call — AllFound | sales, discovery | [Intro call - AllFound](./2026-05-27 - Intro call - AllFound.md) |
" "$NP/INDEX.md"
```

### Bump Next ID

```bash
awk '/^\*\*Next ID:\*\*/{
  match($0, /[0-9]+/)
  n = substr($0, RSTART, RLENGTH) + 1
  sub(/N-[0-9]+/, sprintf("N-%03d", n))
} {print}' "$NP/INDEX.md" > "$NP/INDEX.md.tmp" && mv "$NP/INDEX.md.tmp" "$NP/INDEX.md"
```

### Update Notes count

```bash
awk '/^\*\*Notes count:\*\*/{
  match($0, /[0-9]+/)
  n = substr($0, RSTART, RLENGTH) + 1
  sub(/[0-9]+/, n)
} {print}' "$NP/INDEX.md" > "$NP/INDEX.md.tmp" && mv "$NP/INDEX.md.tmp" "$NP/INDEX.md"
```

### Archive overflow (INDEX > 200 rows)

```bash
ROWS=$(grep -c '^| N-' "$NP/INDEX.md")
if [ "$ROWS" -gt 200 ]; then
  OVERFLOW=$((ROWS - 200))
  QUARTER=$(date +%Y-Q)$(( ($(date +%-m)-1)/3+1 ))
  mkdir -p "$NP/archive"
  ARCHIVE="$NP/archive/${QUARTER}.md"
  grep '^| N-' "$NP/INDEX.md" | tail -n "$OVERFLOW" >> "$ARCHIVE"
  tail -r "$NP/INDEX.md" | awk -v max="$OVERFLOW" '
    /^[|] N-/ && count < max { count++; next }
    { print }
  ' | tail -r > "$NP/INDEX.md.tmp" && mv "$NP/INDEX.md.tmp" "$NP/INDEX.md"
fi
```

### Remove INDEX row (for delete)

```bash
grep -v '| N-017 |' "$NP/INDEX.md" > "$NP/INDEX.md.tmp" && mv "$NP/INDEX.md.tmp" "$NP/INDEX.md"
```

### Re-enhance — extract and regenerate

Read the note, split at `^## Raw$`. Regenerate everything above from the Raw
block (+ transcript if referenced). Everything from `## Raw` down is preserved
byte-identical — copy it verbatim from the original read, never reconstruct it.
Note files are written with the Write tool; INDEX.md is always stream-edited.

### General principle

Use `sed`/`awk`/`grep` to update INDEX.md — treat it as a stream (filter in,
filter out, append, prepend). Never reconstruct the full INDEX from memory.
This prevents accidental row modification, dropped rows, and formatting drift.

---

## Grep Patterns

Notes live in the **root** of `$NP`; target `"$NP"/*.md` or use
`--include`/`--exclude` to skip `INDEX.md`.

```bash
# (assumes $NP resolved from config)

# Notes about a topic (excluding INDEX)
grep -ril --include='*.md' --exclude='INDEX.md' 'allfound' "$NP"

# Notes by tag (frontmatter YAML list)
grep -lE '^[[:space:]]*-[[:space:]]+sales$' "$NP"/*.md

# Recent notes (from INDEX)
grep '^| N-' "$NP/INDEX.md" | head -20

# Open action items across all notes
grep -A1 '## Action Items' "$NP"/*.md | grep '^- \[ \]'

# Notes with transcripts
grep -l 'transcript: yes' "$NP"/*.md

# A specific note across INDEX + archive
grep 'N-017' "$NP/INDEX.md" "$NP/archive/"*.md 2>/dev/null

# Notes by date range / attendee
grep '^| N-.*2026-05' "$NP/INDEX.md"
grep -l 'attendees:.*Jim' "$NP"/*.md
```

---

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| First use, no config file | Read `references/setup.md`; ask for location, write config |
| Config points at a missing directory | Recreate it (`mkdir -p`), or ask the user if it moved |
| Custom dir is actually a vault (`.obsidian/`) | Auto-set `NP_BACKEND=obsidian` |
| Only a transcript, no raw notes | Summarize transcript; `## Raw` = `(none — transcript only)` |
| Raw notes only, no transcript | Structure anchors; Rule 6 — no invention for ambiguous fragments |
| Transcript > 50KB pasted inline | Save to sibling `.transcript.txt`, never inline |
| User edited the enhanced section | Fine — `re-enhance` overwrites; warn first |
| Title collision same day | Append ` (2)` before `.md` |
| Ambiguous search match | List matches with one-line context, ask which |
| `## Raw` empty or missing | Refuse to re-enhance; ask user to append |
| INDEX > 200 rows | Archive oldest to `archive/YYYY-QN.md` on next note creation |
| Note file missing from INDEX | On discovery, offer to re-add to INDEX |
| "undo" after enhance | Can't undo — Raw is preserved; offer `re-enhance` or manual edit |
| INDEX.md missing but dir has notes | Re-init INDEX by scanning `$NP/*.md` (excluding INDEX.md) |
| Mixed-language note | Verbatim in `## Raw`; translate/paraphrase in enhanced, flag uncertainty |
| Relocate notepad | `notepad: setup` → re-run First Run; offer to move existing contents |

---

## What This Skill Does NOT Do (v1)

- **No audio capture** — text only (pasted transcripts, raw notes)
- **No custom templates** — `generic` only (1:1, interview, standup are v2)
- **No todo-skill integration** — action items stay in the note
- **No sharing / export** — no Slack, email, CRM
- **No multi-user / team folders** — personal agent skill
- **No "Briefs"** — Granola's pre-meeting prep; possible v2
- **No GUI / web UI** — pure markdown + agent instructions (Obsidian is an
  optional backend/viewer, never a dependency)
