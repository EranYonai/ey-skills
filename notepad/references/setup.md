# Notepad — First Run Setup

> Read this file **only** when the config file
> `${XDG_CONFIG_HOME:-$HOME/.config}/ai-notepad/config` does not exist, or when
> the user asks to `notepad: setup` / `move notepad` / `change notepad location`.
> Once the config is written, you never need this file again.

The notepad has **no hardcoded path**. Before saving anything on first use, set
up the location and persist it. Do NOT pick a location silently — ask the user.

## Step 1 — Ask where notes should live

Present three options conversationally:

```
Agent: Looks like this is your first note. Where should I keep your notepad?

       1. An existing Obsidian vault — I'll use wikilinks, callouts, and a
          Notes.base view. Just give me the vault path.
       2. A custom folder — any directory you like (I'll create it if needed).
       3. Default — ~/Documents/notepad-ai (plain markdown, no Obsidian).

       Which one? (1/2/3, or paste a path)
```

Resolve the answer to two values:

| User choice | `NP` | `NP_BACKEND` |
|-------------|------|--------------|
| Obsidian vault (path given) | the vault path | `obsidian` |
| Custom folder (path given) | that path | `plain` (or `obsidian` if it has a `.obsidian/` dir) |
| Default | `$HOME/Documents/notepad-ai` | `plain` |

Detection helper — if the chosen directory contains a `.obsidian/` folder,
treat it as an Obsidian vault regardless of how it was selected:

```bash
if [ -d "$NP/.obsidian" ]; then NP_BACKEND=obsidian; fi
```

## Step 2 — Create the directory and INDEX

```bash
mkdir -p "$NP/archive"
# Create INDEX.md from templates/INDEX.md if absent.
```

There is no `notes/` subfolder — notes are written directly to `$NP`.

## Step 3 — (Obsidian only) optional Notes.base

If `NP_BACKEND=obsidian`, you MAY create `$NP/Notes.base` — see
[`obsidian.md`](./obsidian.md). This is optional; only `INDEX.md` is required.
Skip entirely for `plain` backends.

## Step 4 — Persist the choice

Write the config so future sessions skip setup entirely:

```bash
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ai-notepad"
mkdir -p "$CONFIG_DIR"
cat > "$CONFIG_DIR/config" <<EOF
# AI Notepad configuration — edit NP to move your notepad.
NP="$NP"
NP_BACKEND="$NP_BACKEND"
EOF
```

## Step 5 — Brief the user

```
Notepad initialized at <NP> (<backend>). Ready — paste your notes.
To move it later, edit ~/.config/ai-notepad/config or say "move notepad".
```

## Relocating an existing notepad

When the user asks to move the notepad, re-run this flow. Before rewriting the
config, offer to copy or move the existing `$NP` contents (all `*.md`,
`*.transcript.txt`, `INDEX.md`, `archive/`) to the new location.
