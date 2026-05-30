---
name: todo
description: Persistent markdown-based task management for AI agents. Use this skill when the user wants to manage tasks, add TODOs, check what's open, mark tasks done, or maintain a personal task list across sessions.
---

# AI TODO Skill

A persistent, markdown-based task management system for AI agents.
Designed to be the TODO system that finally sticks — because the AI
maintains it, not you.

## Overview

```
~/.todo/
  TODO.md       <- active tasks only (cap ~50)
  DONE.md       <- recent completions (cap ~100)
  archive/
    2026-Q1.md  <- older completions + session logs
    2026-Q2.md
```

The agent reads `TODO.md` at every session start, maintains it during the
session, and logs a teardown summary before the session ends. The user
never has to manually manage the file — the agent handles all bookkeeping.

---

## Task Schema

Each task is a markdown list item with inline tags:

```
- [ ] `T-042` `[P0]` `[2h]` Fix auth middleware crash on token refresh
  **Why:** Users on Google auth hit 500 every ~4 hours
  **Context:** See services/user-service/auth.py:142
  **Added:** 2026-04-11 | **Due:** 2026-04-13
```

### Fields

| Field | Format | Required | Notes |
|-------|--------|----------|-------|
| Status | `[ ]` `[-]` `[!]` `[x]` | Yes | Checkbox syntax |
| ID | `T-NNN` | Yes | Auto-incrementing, assigned by agent |
| Priority | `[P0]` `[P1]` `[P2]` | Yes | Default P1 on creation |
| Estimate | `[15m]` `[2h]` `[1d]` | No | Agent suggests if omitted |
| Title | Free text | Yes | Short, descriptive |
| Why | `**Why:**` indented line | No | Motivation / impact |
| Context | `**Context:**` indented line | No | Links, file paths, references |
| Added | `**Added:** YYYY-MM-DD` | Yes | Set by agent on creation |
| Due | `**Due:** YYYY-MM-DD` | No | Optional deadline |

### Statuses (4 states)

```
- [ ]   Not started     Task exists, no work begun
- [-]   In progress     Actively being worked on
- [!]   Blocked         Cannot proceed (reason required)
- [x]   Done            Completed — will be archived on teardown
```

Blocked tasks MUST include a reason:
```
- [!] `T-040` `[P0]` `[1d]` Deploy to prod
  **Blocked:** Waiting on GCP credentials from ops
```

### Priority Levels (3 tiers)

```
P0 — Urgent. Do today or it hurts.
     e.g., prod is down, deadline tomorrow

P1 — Important. Default priority.
     e.g., feature work, planned tasks

P2 — Someday. Nice to have.
     e.g., refactors, ideas, low-stakes
```

New tasks default to **P1** unless the user specifies otherwise.

### Time Estimates (optional)

Estimates are encouraged but not required. Use shorthand:

```
[15m]  [30m]  [1h]  [2h]  [4h]  [1d]  [2d]  [1w]
```

When adding a task without an estimate, the agent SHOULD suggest one:
"Sounds like ~2h. Want me to tag it?" — but never block on it.

During reorg, the agent flags unestimated P0/P1 items and offers to
add estimates.

---

## File Structure

### TODO.md

```markdown
# TODO

## Tasks

- [ ] `T-042` `[P0]` `[2h]` Fix auth middleware crash on token refresh
  **Why:** Users on Google auth hit 500 every ~4 hours
  **Context:** See services/user-service/auth.py:142
  **Added:** 2026-04-11 | **Due:** 2026-04-13

- [-] `T-041` `[P1]` `[30m]` Update SDK changelog for v0.9
  **Why:** Blocking manta-sdk release
  **Added:** 2026-04-10

- [!] `T-040` `[P0]` `[1d]` Deploy to prod
  **Blocked:** Waiting on GCP credentials from ops
  **Added:** 2026-04-09

- [ ] `T-039` `[P2]` Refactor queue-manager retry logic
  **Why:** Tech debt — exponential backoff is hand-rolled
  **Added:** 2026-04-08

---
## Memory
<!-- Agent: read this FIRST on session start. Update on teardown. -->
**Sessions since reorg:** 3
**Last reorg:** 2026-04-08
**Next ID:** T-043

| # | Date | Summary |
|---|------|---------|
| 47 | 2026-04-11 | Marked SDK changelog in-progress, added auth fix P0, flagged deploy blocked |
| 46 | 2026-04-10 | Added 2 tasks for SDK release, completed retry refactor |
| 45 | 2026-04-09 | Reorganized — archived 12 done, dropped 3 stale |
```

### DONE.md

```markdown
# Completed Tasks

- [x] `T-038` `[P1]` `[1h]` Set up CI pipeline for manta-sdk
  **Done:** 2026-04-10

- [x] `T-037` `[P2]` `[30m]` Update .gitignore for build artifacts
  **Done:** 2026-04-09

- [x] `T-036` `[P1]` `[2h]` Write integration tests for user-service
  **Done:** 2026-04-08
```

### archive/YYYY-QN.md

```markdown
# Archive — 2026 Q1

## Completed Tasks

- [x] `T-022` `[P1]` `[4h]` Migrate database schema v3
  **Done:** 2026-03-15

## Session Log

| # | Date | Summary |
|---|------|---------|
| 32 | 2026-03-15 | Completed DB migration, started SDK work |
| 31 | 2026-03-14 | Debugging migration script, blocked on staging |
```

---

## Agent Behavior

### Session Start

1. **Read `## Memory` section** in TODO.md (fast — just the footer).
2. **Check "Sessions since reorg"** — if >= 5, auto-run reorg FIRST.
3. **Move leftover `[x]` items** from TODO.md to DONE.md.
   (These are leftovers from a crashed/interrupted previous session.)
4. **Scan `## Tasks`**: count open, overdue, blocked, stale (>14 days).
5. **One-line brief** to user:
   ```
   TODO: 5 open, 1 overdue, 2 stale, 1 blocked.
   ```
   Do NOT list every task. Just the counts. Details on request.

### During Session

- **User completes work matching an open task** → mark `[x]` automatically.
  Only if the match is unambiguous. If unsure, ask: "Does this close T-042?"
- **User mentions new work** → offer to add it: "Want me to add that as a task?"
  Do NOT auto-add without asking.
- **User says "add task: X"** → create with next ID, default P1, set Added date.
  Suggest an estimate if you can infer one.
- **User says "tasks" / "what's open"** → list all active tasks from TODO.md.
- **User says "mark T-042 done"** → mark `[x]`, confirm.
- **User says "block T-042"** → mark `[!]`, ask for blocked reason.
- **User says "unblock T-042"** → mark `[-]` (in progress) or `[ ]`, remove blocked reason.
- **User says "reorganize" / "clean up"** → run full reorg flow (see below).

### Session Teardown

Run this before the session ends. If the user says goodbye, wraps up,
or explicitly ends the conversation — run teardown.

1. **Move all `[x]` items** from TODO.md → prepend to DONE.md with `**Done:** YYYY-MM-DD`.
2. **Increment "Sessions since reorg"** counter in Memory section.
3. **Append 1-line summary** to Memory table (newest first).
   Format: `| {session_number} | YYYY-MM-DD | {what changed this session} |`
4. **Trim Memory table** if > 20 lines — remove oldest lines (FIFO), append them
   to the current quarter's archive file under `## Session Log`.
5. **If reorg ran this session**, reset counter to 0.
6. **Brief**: "Archived N tasks. Session #48 logged."

### Reorg (auto at 5 sessions OR on-demand)

Triggered automatically when "Sessions since reorg" >= 5 on session start,
or manually when the user asks to "reorganize" / "clean up".

1. **Roll DONE.md items older than 90 days** → `archive/YYYY-QN.md`.
   Quarter is based on the Done date.
2. **Re-sort TODO.md** by priority: P0 first, then P1, then P2.
   Within same priority, sort by Added date (oldest first).
3. **Flag stale items** (Added >14 days ago, no status change).
   For each stale item, ask the user:
   - **Keep** as-is
   - **Reprioritize** (e.g., P1 → P2 or P2 → P0)
   - **Drop** (move to DONE.md with status `dropped`, not `done`)
   - **Reschedule** (update Added date to today, resets staleness clock)
4. **Flag unestimated P0/P1 items** → suggest estimates.
5. **Flag past-due items** → ask: extend deadline, reprioritize, or drop.
6. **Reset "Sessions since reorg"** to 0, update **Last reorg** date.
7. **Summary**:
   ```
   Reorg complete: 42 active, 8 stale resolved, 2 overdue addressed.
   DONE.md trimmed from 130 → 45 items. 85 archived to 2026-Q1.md.
   ```

---

## Shell Operations

**Critical rule:** When moving tasks between files, use shell commands — do NOT
rewrite files by reading and reconstructing them. This prevents the agent from
accidentally modifying task content during moves.

All commands are macOS-compatible (BSD awk/sed). No GNU-only features.

### Move all `[x]` items from TODO.md → DONE.md

Single pass: extract completed blocks to DONE.md via stderr, keep the rest
in stdout as the new TODO.md. Handles multi-line task blocks (Why, Context, etc.).

```bash
TODO=~/.todo/TODO.md
DONE=~/.todo/DONE.md
TODAY=$(date +%Y-%m-%d)

awk -v today="$TODAY" '
  /^- \[x\]/ {
    block = $0
    while ((getline line) > 0 && line ~ /^  /) {
      block = block "\n" line
    }
    print block "\n  **Done:** " today > "/dev/stderr"
    if (line != "" && line !~ /^  /) print line
    next
  }
  { print }
' "$TODO" > "${TODO}.tmp" 2>> "$DONE" && mv "${TODO}.tmp" "$TODO"
```

### Increment session counter

```bash
awk '/^\*\*Sessions since reorg:\*\*/{
  match($0, /[0-9]+/);
  n=substr($0, RSTART, RLENGTH)+1;
  sub(/[0-9]+/, n)
} {print}' ~/.todo/TODO.md > ~/.todo/TODO.md.tmp && mv ~/.todo/TODO.md.tmp ~/.todo/TODO.md
```

### Append session log line

The Memory table is newest-first. Insert the new row immediately after the
table header row, not at the end of the file.

```bash
SESSION_NUM=$(awk '/^[|] [0-9]/{print $2+1; exit}' ~/.todo/TODO.md)
sed -i '' "/^|---|------|---------|$/a\\
| ${SESSION_NUM} | $(date +%Y-%m-%d) | SUMMARY_HERE |
" ~/.todo/TODO.md
```

The agent replaces `SUMMARY_HERE` with an actual summary of what changed.

### Trim Memory table (FIFO, cap 20)

```bash
LOG_LINES=$(grep -c '^| [0-9]' ~/.todo/TODO.md)

if [ "$LOG_LINES" -gt 20 ]; then
  OVERFLOW=$((LOG_LINES - 20))

  # Determine archive quarter
  QUARTER=$(date +%Y-Q)$(( ($(date +%-m)-1)/3+1 ))
  mkdir -p ~/.todo/archive
  ARCHIVE=~/.todo/archive/${QUARTER}.md

  # Append oldest N lines to archive
  grep '^| [0-9]' ~/.todo/TODO.md | tail -n "$OVERFLOW" >> "$ARCHIVE"

  # Remove oldest N lines from TODO.md (they are at the bottom of the table)
  tac ~/.todo/TODO.md | awk -v max="$OVERFLOW" '
    /^[|] [0-9]/ && count < max { count++; next }
    { print }
  ' | tac > ~/.todo/TODO.md.tmp && mv ~/.todo/TODO.md.tmp ~/.todo/TODO.md
fi
```

### Move old DONE items to archive (reorg)

Reads multi-line task blocks. The `**Done:**` date can appear on any indented
line (not just the first one after the `[x]` line).

```bash
CUTOFF=$(date -v-90d +%Y-%m-%d 2>/dev/null || date -d '90 days ago' +%Y-%m-%d)
mkdir -p ~/.todo/archive
QUARTER=$(date +%Y-Q)$(( ($(date +%-m)-1)/3+1 ))
ARCHIVE=~/.todo/archive/${QUARTER}.md

awk -v cutoff="$CUTOFF" -v archive="$ARCHIVE" '
  /^- \[x\]/ {
    block = $0
    done_date = ""
    while ((getline line) > 0 && line ~ /^  /) {
      block = block "\n" line
      if (line ~ /\*\*Done:\*\*/) {
        match(line, /[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]/)
        done_date = substr(line, RSTART, RLENGTH)
      }
    }
    if (done_date != "" && done_date < cutoff) {
      print block >> archive
    } else {
      print block
    }
    if (line != "" && line !~ /^  /) print line
    next
  }
  { print }
' ~/.todo/DONE.md > ~/.todo/DONE.md.tmp && mv ~/.todo/DONE.md.tmp ~/.todo/DONE.md
```

### Sort TODO.md by priority (reorg)

Sorting multi-line blocks in shell is error-prone. For this operation,
the agent reads the `## Tasks` section, parses task blocks into a list,
sorts by priority (P0 → P1 → P2), and rewrites only the Tasks section.
Use the Edit tool or programmatic rewrite for this — not `sort`.

The rest of TODO.md (header, Memory section) is untouched.

### General principle

Use `sed`, `awk`, `grep` to move and filter. Treat TODO.md as a stream —
filter lines in, filter lines out, append, prepend. Never reconstruct the
full file from the agent's memory. This prevents:
- Accidental content modification
- Dropped lines from context window limits
- Subtle formatting changes on rewrite

---

## Staleness Detection

A task is **stale** if:
- `Added` date is > 14 days ago, AND
- Status is still `[ ]` (not started) or `[-]` (in progress with no recent mention)

On **session start**: mention stale count in the brief (don't list each one).
On **reorg**: address each stale task individually with the user.

---

## Grep Patterns

The schema is designed for fast grep. Common queries:

```bash
# All open tasks
grep '\- \[ \]' ~/.todo/TODO.md

# All in-progress
grep '\- \[-\]' ~/.todo/TODO.md

# All blocked
grep '\- \[!\]' ~/.todo/TODO.md

# All P0 (any status)
grep '\[P0\]' ~/.todo/TODO.md

# Open P0 tasks
grep '\[P0\]' ~/.todo/TODO.md | grep '\- \[ \]'

# Everything with a deadline
grep 'Due:' ~/.todo/TODO.md

# Find a specific task across all files
grep 'T-042' ~/.todo/TODO.md ~/.todo/DONE.md ~/.todo/archive/*.md

# Overdue items (agent should parse dates, not rely on grep for this)

# Tasks added in a date range
grep 'Added: 2026-04' ~/.todo/TODO.md

# Stale detection (agent logic, not pure grep):
#   1. grep '\- \[ \]\|\- \[-\]' TODO.md  → get open/in-progress
#   2. Parse Added dates, compare to today
#   3. Flag if > 14 days old
```

---

## First Run (Initialization)

If `~/.todo/TODO.md` does not exist, the agent creates it from the template:

```markdown
# TODO

## Tasks

<!-- No tasks yet. Tell me what you're working on! -->

---
## Memory
<!-- Agent: read this FIRST on session start. Update on teardown. -->
**Sessions since reorg:** 0
**Last reorg:** YYYY-MM-DD
**Next ID:** T-001

| # | Date | Summary |
|---|------|---------|
```

Also create `~/.todo/DONE.md`:

```markdown
# Completed Tasks
```

And `~/.todo/archive/` directory.

---

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| First run, no TODO.md | Initialize from template |
| No [x] items on teardown | Skip archive step, still log session |
| Duplicate task titles | IDs disambiguate — always use ID for matching |
| User changes priority mid-task | Update tag in place, log in session summary |
| Crashed session (no teardown) | Next session start moves leftover [x] items |
| DONE.md doesn't exist | Create it on first archive operation |
| archive/ dir missing | Create it on first archive operation |
| User says "undo" on a mark-done | Move from DONE.md back to TODO.md, restore status |
| Task has no Added date (legacy) | Treat as today's date, add the field |
| Memory table has > 20 rows | FIFO oldest rows to archive on teardown |

---

## What This Skill Does NOT Do

- **Multi-user / collaboration** — this is a personal agent skill
- **Sync across machines** — use git or cloud storage for that
- **GUI / web UI** — pure markdown + agent instructions
- **Integration with external systems** (Jira, Linear, GitHub Issues) — future extension
- **Recurring/repeating tasks** — adds complexity, possible v2 feature
- **Time tracking** — estimates exist for planning, not for logging actual time spent
