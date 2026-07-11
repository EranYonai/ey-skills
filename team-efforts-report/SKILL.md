---
name: team-efforts-report
description: Generate a beautiful, self-contained HTML report summarizing a team's efforts and achievements over a time window by pulling from JIRA (epics, initiatives, incidents, tasks, bugs — open + closed), GitLab (merge requests, reviews, commits), and optionally a Slack channel export. Use this skill when the user asks for a "team efforts report", "what did the team do", "summarize team achievements", "team contribution report for my boss", or a "6-month review of the team".
---

# team-efforts-report

Build a single self-contained `index.html` that tells the story of what a team shipped and
contributed over a chosen window. Pull the facts from JIRA + GitLab (+ optional Slack export),
**curate** what matters, then render a modern dashboard the user can hand to their manager.

> **Genericize the placeholders (`<JIRA_HOST>`, `<GITLAB_HOST>`, `<GROUP_ID>`, team usernames)
> for your environment before running.** See the *Example configuration* section below for the
> full list of values you need to fill in.

> **Ground everything in real data.** Every rendered number, epic key, MR title, and person
> must trace back to a source JSON. Never invent keys, counts, or quotes to fill a gap — omit
> or reframe instead.

> **Self-contained output.** The final `index.html` must open by double-click. Inline all data
> as JS consts (no `fetch` of local files). Chart.js via CDN by default; offer a fully-inlined
> variant for offline use.

---

## Example configuration

Before running, gather these values for your environment and substitute them wherever the
placeholders appear below:

| Placeholder | What it is | Example |
|---|---|---|
| `<JIRA_HOST>` | Your JIRA hostname | `jira.example.com` |
| JIRA browse base | Link base for tickets | `https://<JIRA_HOST>/browse/<KEY>` |
| `<GITLAB_HOST>` | Your GitLab hostname | `gitlab.example.com` |
| `<GROUP_ID>` | The team's GitLab group id | `12345` |
| Team members | Names + resolved usernames/emails | `<user1>`, `<user2>`, `<user3>` |
| Slack export path | Optional channel export text file | `slack.txt` |
| `<output-dir>` | Where to write the report + data | `output/team-report/` |

Authentication:

- **JIRA** — via an Atlassian JIRA MCP (the tool names below are examples; adapt to your MCP).
- **GitLab** — authenticate `glab` with your token before running.

---

## Workflow

### Phase 1 — Clarify (use the question tool)

Confirm before pulling anything:

- **Team members** — names (you will resolve to usernames/emails in discovery).
- **Time window** — start + end date.
- **Sources** — JIRA / GitLab / Slack (which of the three).
- **JIRA scope** — all projects they touched vs. a specific project set.
- **Output location** — default `<output-dir>/`.
- **Charts** — online (Chart.js CDN) vs. fully-offline (inline Chart.js).

### Phase 2 — Discovery (parallel subagents)

Probe each source and resolve identities. **Gate: stop and tell the user if a chosen source is
unreachable.**

- **JIRA** (Atlassian MCP): confirm tools respond. Resolve each member via a user-profile lookup
  (example for an Atlassian JIRA MCP: `atlassian_jira_get_user_profile`) using **email**
  (display-name lookup is unreliable). On a Data Center instance, use **short usernames** in JQL
  (e.g. `<user1>`), not accountId.
- **GitLab** (`glab`): confirm auth, resolve each member to username + id via
  `glab api "users?search=<name>"`, and locate the team's group.

### Phase 3 — Data pull (parallel, data-only)

Subagents write **JSON only** into `<output-dir>/data/` — no HTML in this phase. Paginate fully;
expect hundreds of MRs and ~hundreds–thousands of JIRA issues.

**Full data-file set produced under `<output-dir>/data/`:**

- **`jira_raw.json`** — run both JQLs below, dedupe by key, normalize assignee/reporter to short
  usernames, derive `status_category` (Done = closed).
- **`gitlab_raw.json`** — MRs authored, reviews given, issues authored, activity events, plus a
  `project_map` (id → name).
- **`review_impact.json`** — authors of reviewed MRs split external vs. internal to the team,
  the **full** top-external-authors list, `by_project_area`, and `reviewer_to_area` (which
  reviewer covered which area).
- **`slack_summary.json`** — channel stats (approx messages, distinct participants, distinct
  **external** people helped, per-member counts) + ranked **common topics/issues**.
  **No quote highlights by default** — aggregated common issues are preferred over quote cards.
- **`shipped.json`** — the "What We Shipped" TLDR: `themes` + `top_shipped` (see Phase 5).
- **`narrative.md`** — the executive-summary source (see Phase 5).
- **`insights.json`** — the advanced insights (see Phase 6).
- **`stats.json`** — the aggregate (see Phase 4).

**Cache & reuse raw pulls.** Per-endpoint raw responses may be cached under `data/raw/` and
reused so you don't re-hit the APIs. Recompute derived files (e.g. the full external-author list)
from `data/raw/` instead of re-pulling — a full author list can be regenerated from cache with
**zero API calls**.

**JIRA — working JQL** (both open + closed, all types, all projects):

```
(assignee in (u1,u2,...) OR reporter in (u1,u2,...)) AND updated >= "<start>" ORDER BY updated DESC
```

Also run an **`assignee was in (...)`** variant and dedupe by key — this catches people who did
the work but no longer own the issue.

- Tool (example for an Atlassian JIRA MCP): `atlassian_jira_search`. Params: `jql`, `fields`
  (CSV), `limit` (max 50), `start_at` offset for pagination. **On Data Center do NOT use
  `page_token`** (Cloud-only).
- Fields to request: `summary,status,issuetype,project,created,updated,resolutiondate,resolution,assignee,reporter,priority,labels,customfield_10016` (Epic Link — the custom field id varies per instance).
- Issue types seen in the wild: Task, Bug, Epic, Initiative, Incident, and others — don't assume a fixed set.

**GitLab — `glab` recipes** (append `2>/dev/null` to suppress the harmless `.config.yml` warning;
always `--paginate` with `per_page=100`):

```bash
# MRs authored
glab api --paginate "merge_requests?author_username=<u>&created_after=<startISO>&scope=all&state=all&per_page=100" 2>/dev/null
# Reviews given (capture author.username/name per MR to measure impact on OTHER devs)
glab api --paginate "merge_requests?reviewer_username=<u>&created_after=<startISO>&scope=all&state=all&per_page=100" 2>/dev/null
# Issues authored (often ~0 for teams that track work in JIRA)
glab api --paginate "issues?author_username=<u>&created_after=<startISO>&scope=all&state=all&per_page=100" 2>/dev/null
# Activity → estimated commit count (sum push_data.commit_count; do NOT fetch per-commit)
glab api --paginate "users/<id>/events?after=<day-before-start>&per_page=100" 2>/dev/null
# Project id → name
glab api --paginate "groups/<GROUP_ID>/projects?include_subgroups=true&per_page=100" 2>/dev/null
# Resolve straggler project ids
glab api "projects/<id>" 2>/dev/null
```

Do **not** fetch per-MR diffs or per-commit detail — too slow/expensive.

**Slack** — the user provides a channel export as a text file (e.g. `slack.txt`). It's messy
(alternating name / timestamp / body lines). Parse into support-impact stats and **aggregated
common topics/issues** (ranked categories). Default to common-issues aggregation; add quote
highlights only if the user asks.

### Phase 4 — Aggregate → `stats.json`

Keep arrays **chart-ready** (aligned `labels[]` / `values[]`).

- Totals; `by_type` (include Tasks & Bugs with open/closed split); `by_project` (open/closed);
  `by_priority`.
- `per_person` — attribute by **assignee, falling back to reporter** when unassigned.
  **Disclose this rule in the report.**
- `epics_initiatives` list; `incidents` list; `monthly_timeline` (created vs. closed).
- GitLab: totals + `per_person` + `top_projects_by_mr` + `mr_monthly_timeline`.

### Phase 5 — Synthesize

- **`narrative.md`** — the exec-summary source. **Not one flat paragraph** — it must contain the
  pieces the rendered exec summary is composed from (see Phase 7 Build HTML → *Executive summary
  composition*): an intro paragraph with the scale numbers, a **Key Accomplishments** bullet list
  (each bullet a marquee deliverable + the relevant epic/initiative keys), a short **Research
  Insights** group (3 bullets from `insights.json`), and a closing "backbone" line. Also capture
  by-the-numbers, key initiatives/themes, delivery & quality, per-person highlights, looking ahead.
- **`shipped.json`** — a "What We Shipped" TLDR: 6–9 themes, each with `one_liner`, real epic
  `keys`, `highlights`, and a `shipped_count_hint`; plus a `top_shipped` flat list. Ground every
  entry in real keys / MR titles.

**Accuracy / honesty rule (applies to every bullet & claim).** Claims must reflect the **true
status** of the work. Do **not** say something is "done / migrated / completed" when the backing
epics are in-progress or partial — check `status_category` before wording a bullet. If an
initiative is in flight, word it as "drove / in progress / already shipped X", not "migrated
everything". *Example:* if a platform migration is in progress, word the bullet as "drove the
migration (in progress) — already shipped the new pipeline as blocking and moved core packages
over", **not** "migrated everything onto a single modern platform".

### Phase 6 — Data Curation (decide what to present) — **IMPORTANT**

**Think before you build. Don't dump everything.**

- **Inventory first.** List what data you actually have and how rich each dimension is
  (volume, variety, story value).
- **Serve the audience.** This is usually a manager showing *their* boss — favor outcomes and
  impact over raw activity.
- **Value over completeness.** Highlight what's impressive and true: shipped outcomes,
  cross-team impact (reviews for others, support-hotline reach), delivery health (close rates),
  themes/initiatives. De-emphasize or omit low-signal metrics (e.g. issues authored = 0, or any
  metric too sparse to chart).
- **Right chart for the shape.** Donut = part-of-whole; bar = category comparison; horizontal
  bar = many/long labels (e.g. top-N people); line = time trend; stacked bar = composition per
  entity. Prefer a stat callout or short list when a chart adds nothing. **Drop any chart with
  <3 meaningful data points.**
- **Turn counts into impact.** e.g. "~50% of our reviews served developers outside the team;
  N distinct devs unblocked."
- **Frame gaps honestly and positively.** e.g. incidents are newly tracked — a low count
  reflects stability + a new process. Never fabricate to fill a gap.
- **You own section ordering and inclusion.** The section list in Phase 7 is a **template, not a
  mandate** — include what's strong for *this* team and window.
- **Decide what the Overview tab features.** Decide which KPIs, outcomes, and ~5 highest-impact
  charts to feature on the Overview tab (Phase 7 View 1) — this curation is authoritative there;
  don't promote everything.

#### Advanced insights → `insights.json`

Derived from the raw JIRA + GitLab MR data already collected (source field in parens). Compute
the ones that tell a strong, true story for this team/window; skip the rest. A useful concrete
set (and **where each can land** in the report):

- **`weekly_merge_throughput`** — MRs merged per week: avg/week + peak week (MR `merged_at`).
  → **Drill-down** chart. Sustained momentum.
- **`release_branch_support`** — mainline vs release vs other, plus the specific release branches
  (MR `target_branch`). → **Drill-down**. **Frame by ABSOLUTE COUNT** — lead
  with "N fixes to live release branches"; do **not** lead with the small %.
- **`ticket_traceability`** — MR titles referencing a JIRA key regex `[A-Z]{2,10}-\d+` (MR
  `title`). → **Drill-down**. **Lead with the absolute count + project linkage** ("N MRs linked
  to JIRA epics, mostly PROJ"); show the percentage only as a **muted secondary** (the % is often
  unflattering).
- **`roadmap_status`** — epics bucketed Done / In-Progress / Planned + the initiatives with their
  statuses (`epics_initiatives` by `status_category`). → **Drill-down roadmap view**: initiative
  cards + an epic progress bar + a featured-epics list. "N delivered, M in flight."
- **`engineers_enabled` (combined reach)** — union of distinct external MR authors reviewed
  (`review_impact`) + distinct people helped in Slack (`slack_summary`). **Computed but OPTIONAL /
  ASK-FIRST.** Default to showing the component facts separately (e.g. N external review devs;
  ~M hotline people) rather than a combined hero number — only surface the combined headline if
  the user asks. Slack↔GitLab identity matching is approximate — label it an estimate and disclose
  the method.

**Curation & framing (reinforces Phase 6):**

- Pick only the insights that are **strong and true** for this team/window.
- **Reframe weak-looking metrics honestly and positively** — prefer absolute counts over
  unflattering percentages; never fabricate (see the accuracy/honesty rule in Phase 5).
- **Don't promote a combined "engineers enabled" hero.** Keep insights in Drill-down; show
  component impact facts (external review devs, hotline reach) separately unless the user asks for
  a combined number.
- **Drop any insight with too little data** to be meaningful.

### Phase 7 — Build HTML

One self-contained `index.html`. Inline all data as JS consts (no local `fetch`). Chart.js via
CDN by default (offer inlined for fully-offline). Modern dashboard aesthetic (deep blue / teal /
amber). Include a `<!-- FILL ME -->` placeholder for manual Slack additions.

**Structure the report as TWO TABBED VIEWS**, shown one at a time on screen (not a long scroll,
not just PDF page breaks). A sticky top **tab nav** has two tabs — **"Overview"** (default/active)
and **"Drill-down"**. Vanilla JS toggles an `.active` class; the inactive view is `display:none`.
Put a prominent **"View full drill-down ↓"** button on the Overview and a **"← Back to overview"**
link on the Drill-down. Scroll to top on every switch. Print-to-PDF can be mentioned as a
nice-to-have, but the on-screen tabs are the primary model.

**Executive summary composition (do this exactly — it is NOT one flat paragraph):**

Compose the exec summary from `narrative.md` as:

1. **Intro paragraph** with the scale numbers.
2. **Key Accomplishments** — a **bullet list**; each bullet is a marquee deliverable followed by
   **clickable JIRA links** to the relevant epic/initiative keys.
3. **Research Insights** — a short group of **3 bullets** pulling computed values from
   `insights.json` (e.g. sustained velocity = avg/week + peak week; cross-team reach = reviews +
   external devs + hotline people; roadmap progress = epics delivered vs in flight).
4. A closing **"backbone"** line.

**JIRA links** use the instance browse URL — for Jira **DC**: `https://<JIRA_HOST>/browse/<KEY>`
— and open in a new tab (`target="_blank" rel="noopener"`).

The two tabs show different depths of the **same** exec summary:

- **Overview** → a **tight** version: intro paragraph + top ~6 accomplishment bullets + the 3
  Research Insights.
- **Drill-down** → the **fuller** version: all accomplishment bullets + insights + the closing
  backbone line.

**⚠️ Chart.js + `display:none` (real bug — follow exactly):** a canvas inside a hidden container
can render at 0 size (blank chart). So:

- Give **every** chart container an explicit CSS **height**.
- **Initialize ALL charts on load** (both views), even the hidden one.
- On each tab switch, **`resize()` the now-visible view's charts** — iterate its canvases and call
  `Chart.getChart(canvas).resize()` inside a `requestAnimationFrame`.
- **Every canvas id must be UNIQUE across the whole document.** The Overview charts need **NEW**
  canvas ids and their **own** Chart instances even when they visualize the same data as
  drill-down charts (Chart.js can't bind two charts to one canvas). Use distinct namespaces:
  Overview charts `c-ov-*`, insight charts `c-ins-*`.

Section template (curate per Phase 6):

**View 1 — Overview** (default tab; the executive one-pager; fills the screen; first thing the
boss sees; uncluttered, stands on its own):

- Dark hero — a **two-column** layout:
  - **LEFT:** eyebrow + h1 + subtitle (reporting window + generated date + team name),
    vertically centered against the org chart. **Do NOT add per-member name "chips"** — the org
    chart on the right already lists everyone, so chips would duplicate it.
  - **RIGHT:** the small pure-CSS **org chart** (see the Team / Org structure note below).
  - Stacks responsively on narrow screens.
- **Tight executive summary** (intro paragraph + top ~6 accomplishment bullets + 3 Research
  Insights) — see *Executive summary composition* above
- Headline KPI cards — only the highest-value numbers (e.g. issues closed, MRs merged, reviews
  given, commits, cross-team devs helped), **not** every metric (see Phase 6)
- Headline outcomes — the 3-5 biggest wins, one line each (distilled from shipped themes)
- A small curated set of the **HIGHEST-IMPACT charts** (typically ~5) chosen for wow/outcome
  value — e.g. delivery donut (closed vs open), cross-team review impact (top external devs
  helped), per-person contribution (stacked), monthly delivery timeline, MR-merged timeline.
  Keep it uncluttered. (These use their own unique canvas ids / Chart instances — see above.)
- Prominent **"View full drill-down ↓"** button

#### Team / Org structure (hero org chart)

If the team has a known reporting structure, render a small CSS org chart in the hero (right
side): manager on top, reports below, connected with simple CSS connector lines / borders (no
external libs/images). New/very-recent members should be visually de-emphasized (greyed/muted,
dashed border, a "(new)" tag) but still shown. Make it responsive — stack below the title text on
narrow screens.

**Prefer the org chart alone — do not also render the members as name "chips".** If the org chart
shows everyone, chips are redundant duplication and were removed.

Org tree template (fill in real names/structure at runtime):

```
<Manager> (Manager)
├─ <Team Member 1>
├─ <Team Member 2>
└─ <New Member> (new — grey out)
```

The org chart is **presentational only** — it doesn't affect the data pulls (which are
per-configured-team-member). New members with little/no history in the window may legitimately
have low or zero metrics; that's expected — present them accordingly (or note they just joined).

**View 2 — Drill-down** (second tab; everything else):

- **"← Back to overview"** link
- What We Built / Shipped (theme grid + scrollable `top_shipped`) + notable shipped items
- KPI cards (full detail)
- Charts grid (all detailed charts)
- Review-impact charts (top external authors; external/internal per person; by area)
- Per-person cards
- Epics & Initiatives table (scrollable, status color-coded, initiatives badged)
- Incidents table (open highlighted + a note that formal incident tracking may be new, so low
  counts are expected)
- Support Hotline (Slack) — stats + common-topics chart
- Footer — sources / window / generation timestamp

### Phase 8 — Verify

- Cross-check **every rendered number** against `stats.json` / the source JSONs.
- Confirm self-contained: no local `fetch`; Chart.js is the only external dependency.
- Confirm each chart's label/value arrays are length-matched.
- Confirm **every canvas id is unique** and both tabs' charts render (no blank charts on the
  initially-hidden view after switching — the `resize()` on tab switch handles this).
- Confirm the `<!-- FILL ME -->` placeholder exists.

### Phase 9 — Iterate with the user until satisfied — **IMPORTANT**

Present the finished report: the **path** plus a concise summary of sections and headline
numbers. Then **enter a review loop**:

1. Ask the user what to change.
2. Apply edits as **surgical patches to the existing `index.html`** (not a rebuild). Preserve
   style, keep it self-contained.
3. **Re-verify after each change** — numbers still trace to the data, and the report still opens
   by double-click.
4. Repeat until the user says they're satisfied.

Example requests: "bump the top-N chart from 12 to 25", "remove Slack quote
highlights and keep the aggregated common topics."

---

## Orchestration tips

- Run **discovery** and **data pulls** as **parallel subagents**.
- Keep raw pulls **data-only** — write JSON into `<output-dir>/data/`, no HTML.
- Expect large datasets (hundreds of MRs, ~hundreds–thousands of JIRA issues) — **paginate fully**.

## Pitfalls

- **JIRA DC vs Cloud pagination** — use `start_at` offset on Data Center; `page_token` is Cloud-only.
- **Resolve users by email**, not display name.
- **Dedupe across JQLs** (`assignee/reporter in` + `assignee was in`) by issue key.
- **Don't fetch per-MR diffs or per-commit** — estimate commits from `push_data.commit_count`.
- **Slack export is messy** — label all derived numbers as approximate.
- **Disclose the `per_person` attribution rule** (assignee → reporter fallback) in the report.
- **Keep the HTML self-contained** — inline data, no local `fetch`.
- **Accuracy / honesty** — never claim in-progress work is "done/migrated/completed"; check
  `status_category` and word in-flight items as "drove / in progress / already shipped X".
- **Don't duplicate names as chips** when the hero org chart already lists everyone.
- **No combined "engineers enabled" hero** by default — show component facts (external review
  devs, hotline reach) separately; only combine if the user asks.
- **No Slack quote cards** by default — aggregated common topics/issues only (keep a
  `<!-- FILL ME -->` for manual additions).
- **Cache raw pulls** under `data/raw/` and recompute derived files from cache instead of
  re-hitting the APIs.
