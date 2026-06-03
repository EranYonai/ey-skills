# Notepad — Obsidian Backend

> Read this file **only** when `NP_BACKEND=obsidian`. For a `plain` backend,
> ignore everything here — none of it applies.

When `$NP` is an Obsidian vault, notes use Obsidian conventions. The core flow
(capture, enhance, query) is identical to the plain backend; only the link
format and the optional `Notes.base` view differ.

## Link format in INDEX.md

The `File` column uses Obsidian **wikilinks** (note name without extension):

```markdown
| N-017 | 2026-05-27 | Intro call — AllFound | sales, discovery | [[2026-05-27 - Intro call - AllFound]] |
```

(Plain backend uses `[title](./name.md)` instead — see SKILL.md.)

### Prepend an INDEX row (Obsidian)

```bash
sed -i '' "/^|----|------|-------|------|------|$/a\\
| N-017 | 2026-05-27 | Intro call — AllFound | sales, discovery | [[2026-05-27 - Intro call - AllFound]] |
" "$NP/INDEX.md"
```

## Callouts

TL;DR / decisions / warnings render as native Obsidian callouts:

```markdown
> [!abstract] TL;DR
> ...
> [!check] Decisions
> - ...
> [!warning] ...
```

These are plain blockquotes in non-Obsidian viewers, so they're safe either
way — but in a vault they get the nicer styling.

## Notes.base (queryable table view)

`Notes.base` is an Obsidian **Bases** file: a static definition of a queryable
table/board view over all `notepad-ai`-tagged notes. It is **optional** — the
notepad works with `INDEX.md` alone.

- The agent does **not** edit `Notes.base` during normal note operations.
- Only create or modify it when the user explicitly asks to change views or
  filters.
- For Base file syntax, consult the separate `obsidian` skill.

A minimal `Notes.base` filters on the mandatory `notepad-ai` tag and surfaces
the key frontmatter fields (id, date, title, tags, attendees, transcript).
Defer to the `obsidian` skill for the exact `.base` schema rather than guessing.

## Vault hygiene

- Notes still live in the **vault root**, not a subfolder.
- `INDEX.md` and `Notes.base` also live in the root.
- The mandatory `notepad-ai` first tag is what every Base view / search filters
  on — never drop it.
