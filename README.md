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

## Philosophy

These skills follow a few principles:

1. **Zero friction** — if the user has to remember to do something, the system has failed
2. **Flat files** — markdown that works with grep, git, and any editor
3. **Agent-maintained** — the AI does the bookkeeping, the human does the thinking
4. **Bounded growth** — every file has a cap, archives are automatic
5. **Grep-friendly** — consistent tokens (`[P0]`, `T-042`, `[x]`) that tools can find

## License

MIT
