# Notepad — Obsidian Vault Backend (no-database RAG)

> Read this file **only** when `NP_BACKEND=obsidian`. For a `plain` backend,
> ignore everything here — none of it applies and the flat `INDEX.md` model in
> `SKILL.md` is the whole story.

When `$NP` is an Obsidian vault, the notepad is more than a flat note pile: it
is the capture front-end of a **file-system knowledge base** modelled on
Andrej Karpathy's no-database Obsidian RAG. There is no vector store and no
embeddings — the *folder structure is the index* and the agent does the
retrieval by reading at most three files.

The core capture + enhancement flow (anchors are sacred, `## Raw` is sacred,
the Granola rules) is **identical** to the plain backend. What changes is
*where notes land* and that a manual **`compile`** step promotes them into a
queryable wiki.

For the canonical description of this vault convention — and for `.base`,
wikilink, callout, and Canvas syntax — defer to the separate **`obsidian`
skill** ("Karpathy no-database RAG vault" section). Do not guess Obsidian
syntax; consult that skill.

---

## Vault layout

```
$NP/                              <- the Obsidian vault root
  AGENTS.md                       <- vault navigation rules (the "CLAUDE.md")
  raw/                            <- staging area (input zone)
    notepad-ai/                   <- notepad writes captures HERE
      INDEX.md                    <- catalog of staged notepad notes (flat, newest-first)
      Notes.base                  <- optional Obsidian view over staged notes
      2026-05-27 - Intro call - AllFound.md
      ...
    <other raw material>          <- web clippings, pasted research, etc.
  wiki/                           <- compiled knowledge base (output zone)
    _master-index.md             <- table of contents: every topic, one line each
    <topic>/
      _index.md                   <- lists every article in this topic
      <Article Title>.md          <- compiled wiki article with [[wikilinks]]
  archive/                        <- INDEX overflow rows only (see SKILL.md)
```

Two zones, two jobs:

- **`raw/notepad-ai/`** — fast capture. Every notepad note is written here as a
  staging file using the standard note schema from `SKILL.md` (frontmatter,
  body sections, the sacred `## Raw` block, the mandatory `notepad-ai` first
  tag). This folder keeps its own flat `INDEX.md` exactly like the plain
  backend — it is the staging catalog.
- **`wiki/`** — the compiled, navigable knowledge base. Nothing lands here
  automatically. The **`compile`** command promotes raw material into topic
  articles.

> **Key difference from the plain backend:** notes do NOT live in the vault
> root. They live in `raw/notepad-ai/`. The "no `notes/` subfolder" rule in
> `SKILL.md` applies to the *plain* backend only; in a vault, the staging
> subfolder IS the model.

---

## Capture (vault mode)

Identical to `SKILL.md` capture, with two differences:

1. **Destination is `$NP/raw/notepad-ai/`**, not `$NP`. Substitute
   `RAW="$NP/raw/notepad-ai"` everywhere `SKILL.md` uses `$NP` for note files,
   INDEX.md, archive, and transcripts.
2. **Links use wikilinks** (see below).

```bash
[ -f "$CONFIG" ] && . "$CONFIG"      # defines NP, NP_BACKEND
RAW="$NP/raw/notepad-ai"
mkdir -p "$RAW"
# write note file, INDEX row, transcript, etc. into $RAW exactly as SKILL.md
```

A freshly captured note is **not** yet in the wiki. It sits in
`raw/notepad-ai/` until the next `compile`. This is deliberate — capture is
cheap and frequent; compilation is a considered, batch operation.

### Link format in the staging INDEX.md

The `File` column in `raw/notepad-ai/INDEX.md` uses Obsidian **wikilinks**
(note name without extension):

```markdown
| N-017 | 2026-05-27 | Intro call — AllFound | sales, discovery | [[2026-05-27 - Intro call - AllFound]] |
```

(Plain backend uses `[title](./name.md)` — see `SKILL.md`.)

#### Prepend an INDEX row (Obsidian)

```bash
sed -i '' "/^|----|------|-------|------|------|$/a\\
| N-017 | 2026-05-27 | Intro call — AllFound | sales, discovery | [[2026-05-27 - Intro call - AllFound]] |
" "$RAW/INDEX.md"
```

### Callouts

TL;DR / decisions / warnings render as native Obsidian callouts and are plain
blockquotes everywhere else, so they are safe in both:

```markdown
> [!abstract] TL;DR
> ...
> [!check] Decisions
> - ...
> [!warning] ...
```

---

## Compile — promote `raw/` into `wiki/`

**Trigger:** the user says `compile`, `notepad: compile`, `compile notes`, or
"build the wiki".

This is the heart of the RAG. The agent reads everything pending in `raw/`,
decides which topic each piece belongs to, and writes or updates wiki articles.

### Compile algorithm

1. **List pending raw material.** Read `raw/notepad-ai/INDEX.md` for staged
   notepad notes; also list any other files under `raw/` (web clippings,
   pasted research). Skip files already marked compiled (see step 6).
2. **Read the current map.** Read `wiki/_master-index.md` to learn existing
   topics and their one-line descriptions. Read the relevant
   `wiki/<topic>/_index.md` files only for topics a raw item plausibly fits.
3. **Categorize each raw item by topic.**
   - If it fits an existing topic, target that `wiki/<topic>/`.
   - If it is genuinely new, create a new topic folder and add it to the
     master index. Topic folder names are short, lowercase, hyphenated
     (e.g. `wiki/hiring/`, `wiki/agent-infra/`).
   - Prefer **few, broad topics** over many tiny ones. A topic should hold
     several related articles.
4. **Write / update the wiki article.**
   - One article per coherent subject (an article may synthesize several raw
     notes; a single raw note may contribute to several articles).
   - Use the **wiki article schema** below: frontmatter, synthesized prose +
     bullets, `[[wikilinks]]` to related articles, and a **Sources** section
     listing the raw notes it was built from (as wikilinks).
   - Synthesize — do not copy. The raw note's verbatim `## Raw` block stays in
     `raw/`; the wiki article is the clean, cross-linked compilation.
   - When updating an existing article, merge new material in; never silently
     drop existing content.
5. **Update the indexes** (see "Index files" below): add new articles to the
   topic `_index.md`, add new topics to `_master-index.md`.
6. **Mark raw items compiled.** Add `compiled: 2026-06-03` to the raw note's
   frontmatter (and/or note it in `raw/notepad-ai/INDEX.md`) so the next
   compile skips it. Never delete raw files — `raw/` is the permanent verbatim
   record.
7. **Report.** Summarize: which articles were created/updated, which topics are
   new, how many raw items were promoted.

> The standalone "loose" notes that may already exist in the vault root are NOT
> touched by compile unless the user explicitly asks to fold them in.

### Wiki article schema

```markdown
---
title: AllFound Account
topic: sales
tags:
  - notepad-ai
  - wiki
  - sales
updated: 2026-06-03
---

# AllFound Account

> [!abstract] Summary
> Discovery-stage prospect (100 employees). Replacing Tuesday.ai is a Q2
> priority; price and manual workflow are the pain points.

## Background
- 100 employees, +20 next quarter.
- Currently on [[Tuesday.ai]] at $180/employee/year.

## Open Threads
- HIPAA requirements — see [[Compliance Requirements]].

## Sources
- [[2026-05-27 - Intro call - AllFound]]
```

Rules:
- **Always** keep `notepad-ai` and `wiki` in `tags`.
- Cross-link liberally with `[[wikilinks]]` — this is the graph that lets the
  agent traverse related concepts for free.
- The **Sources** section links back to the originating `raw/notepad-ai/` notes
  so provenance is always one hop away.

---

## Index files (the file-system "database")

Three reads locate any fact, regardless of vault size:
`_master-index.md` → `<topic>/_index.md` → the article.

### `wiki/_master-index.md`

Root table of contents — every topic with a one-line description and a link to
its `_index.md`:

```markdown
---
title: Wiki Master Index
tags:
  - notepad-ai
  - wiki
  - index
---

# Wiki — Master Index

Three-read navigation: this file → a topic's `_index` → the article.

| Topic | What's in it |
|-------|--------------|
| [[wiki/sales/_index\|sales]] | Prospects, deals, discovery calls. |
| [[wiki/hiring/_index\|hiring]] | Candidates, interview notes, pipeline. |
| [[wiki/agent-infra/_index\|agent-infra]] | Infra roadmap, downtimes, CI. |
```

### `wiki/<topic>/_index.md`

Per-topic catalog — every article in that topic, one line each:

```markdown
---
title: "Sales — Index"
topic: sales
tags:
  - notepad-ai
  - wiki
  - index
---

# Sales

| Article | Summary |
|---------|---------|
| [[AllFound Account]] | 100-emp prospect; replacing Tuesday.ai (Q2). |
| [[Tuesday.ai]] | Incumbent tool being displaced. |
```

Keep these as plain markdown wikilink tables — they are what the agent reads to
navigate, and they work without Obsidian. (See the `obsidian` skill for the
exact wikilink-to-subfolder syntax, e.g. `[[wiki/sales/_index|sales]]`.)

### Optional `.base` views

A `.base` is a *live, human-browsable* table — a convenience for you in
Obsidian, never the agent's retrieval path.

- `raw/notepad-ai/Notes.base` — table over staged notepad notes (the existing
  one). Defer to the `obsidian` skill for `.base` schema.
- `wiki/Wiki.base` (optional) — table over all `tags: wiki` articles grouped by
  `topic`.

The agent does **not** edit `.base` files during capture or compile. Only
create/modify them when the user explicitly asks. The markdown indexes remain
the source of truth for traversal.

---

## Query — three-read traversal

When the user asks a question against the knowledge base:

1. Read `wiki/_master-index.md` → pick the relevant topic(s).
2. Read that topic's `wiki/<topic>/_index.md` → pick the article(s).
3. Read the article. Follow its `[[wikilinks]]` to pull in related articles for
   free (no new search).
4. If the answer is not yet compiled, fall back to grepping `raw/` (the staged
   notes still contain everything) and offer to `compile`.

Prefer this 3-read path over broad globbing — that is the whole point of the
structure.

```bash
# Fallback grep over staged-but-not-yet-compiled material
grep -ril --include='*.md' 'allfound' "$NP/raw"
```

---

## Direct research into the wiki

The user may skip the raw step entirely: "research X and write it into the
wiki." In that case the agent does the full pipeline — gather, synthesize,
write the article + indexes directly under `wiki/` — and adds a Sources note
indicating it was direct research rather than a captured raw note.

---

## Vault hygiene

- Captures live in `raw/notepad-ai/`; the staging `INDEX.md` and `Notes.base`
  live there too.
- Compiled knowledge lives in `wiki/`; never put articles in the vault root.
- `raw/` files are the permanent verbatim record — never delete on compile,
  only mark `compiled:`.
- The mandatory `notepad-ai` first tag rides through from raw note → wiki
  article so every Base view and search can filter on it. Never drop it.
- All navigation/compile rules are also encoded in the vault's `AGENTS.md` so
  any agent opening the vault knows the conventions without loading this skill.
