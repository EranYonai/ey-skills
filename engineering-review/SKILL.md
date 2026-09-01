---
name: engineering-review
description: Learn and apply the engineering judgment of real code reviewers from historical GitLab or GitHub reviews. Use when learning a reviewer or team, building or updating a reviewer model, reviewing a PR against learned judgment, comparing reviewers, or evolving review principles from new evidence.
---

# Engineering Review

Apply an evidence-backed model of how specific engineers judge software.

The model distinguishes objective defects, team conventions, reviewer
preferences, architectural principles, and uncertainty.

**Never present a learned preference as an objective defect.**

## Route

Default to `review`. Load another mode only when the request clearly asks for it.

| Request | Mode | Load |
|---|---|---|
| review this PR/MR/diff, would X approve this, what would X flag | **review** | continue below |
| learn how X reviews, build or initialize a reviewer model | learn | `modes/learn.md` |
| update the model with new reviews, re-learn | evolve | `modes/evolve.md` |
| compare reviewers, build a review panel | compare | `modes/compare.md` |
| what would X think of this, without a diff | predict | `modes/predict.md` |

Once learned, local knowledge lives in `knowledge/` as an OKF v0.1 bundle: one
concept per Markdown file with YAML frontmatter, linked together, with
`index.md` at each level for progressive disclosure. This bare skill does not
ship a knowledge bundle; run `learn` before making reviewer-specific claims.

# Review Mode

## 1. Load only what the diff needs

```text
knowledge/surfaces/index.md   -> match changed paths to a surface
        |
knowledge/surfaces/<slug>.md  -> names reviewers with evidence
        |
knowledge/reviewers/<CODE>.md -> open those, not every reviewer
```

Open only the principle concepts cited by the selected surface or reviewer.
Open `knowledge/conventions.md` when the change touches an area covered there.

Opening unrelated concepts wastes context and can fabricate judgment. If no
surface matches, say so and perform only the objective review.

Never read raw evidence unless provenance is needed for a specific finding.

## 2. Understand the change

Read the PR or MR description, linked issue, complete diff, surrounding
implementation, relevant tests, and callers. Do not review isolated snippets
when surrounding code determines correctness.

## 3. Objective correctness pass

Independently check, regardless of what the learned model says:

incorrect behavior, broken invariants, races, error-handling failures, data
loss, security, API and backward compatibility, resource leaks, and missing or
misleading tests.

**Do not let learned preferences suppress objective defects.**

## 4. Learned-judgment pass

Ask what these reviewers have historically challenged in comparable changes.
Apply only loaded principles backed by relevant evidence.

Write: "consistent with a pattern this reviewer has challenged repeatedly."

Do not write: "the reviewer would reject this."

## 5. Blind-spot pass

The learned model must improve the review, not replace it. Independently inspect
important areas with weak historical coverage, especially security,
reliability, and compatibility boundaries.

Automated findings are claims, not verdicts. Verify them against the code.

## 6. Verify before reporting

For each candidate finding, locate the exact code, understand the execution
path, establish concrete impact, check whether existing code already handles
it, inspect tests and callers, and consider whether the behavior is intentional.

Do not report hypothetical concerns merely because something could go wrong.

## Classification

| Class | Meaning |
|---|---|
| `DEFECT` | Likely objectively incorrect behavior. Explain the concrete failure. |
| `SECURITY` | Security-impacting defect or unsafe boundary. |
| `RELIABILITY` | Availability, recovery, concurrency, or durability risk. |
| `PERFORMANCE` | Meaningful resource problem supported by evidence. |
| `LEARNED_PRINCIPLE` | Conflicts with an established reviewer or team principle. Label it as learned judgment. |
| `CONVENTION` | Conflicts with an established project convention. |
| `QUESTION` | Important uncertainty needing clarification. |

Do not report formatting preferences, unsupported hypotheticals, issues handled
elsewhere, or generic requests for more tests. Prefer a few high-confidence
findings over many weak ones.

## Calibration

1. Accepted feedback does not prove a principle is a requirement. Weight the
   reasoning and repeated evidence, not only the outcome.
2. Preserve self-labeled severity such as "nit", "your call", or "non-blocking".
3. Preserve contested positions. Report disagreement instead of inventing team
   consensus.
4. Respect the coverage map. Never synthesize an opinion for a reviewer on a
   surface they have not reviewed. Say "limited historical evidence" instead.
5. For each finding, state whether the appropriate resolution is blocker,
   follow-up, or nit.

## Output

```markdown
## Summary

<short assessment>

## Findings

### [severity] [classification] - <title>

**Location:** `<file>:<lines>`

<problem and evidence>

**Why it matters:** <impact>

**Basis:** Defect / Learned principle (`<id>`) / Convention / Security
**Confidence:** High / Medium / Low
**Resolution:** blocker / follow-up / nit

## Learned Judgment
<reviewer-specific observations, if any>

## Blind Spots Checked
<areas checked independently because historical evidence is weak>
```

If there are no substantive findings, say so explicitly. Do not produce a long
review merely to demonstrate that the skill ran.

When a finding rests on learned judgment, include the principle ID, evidence
count or examples, confidence, any contradictory evidence, and resolution.

## Bundle Layout

```text
engineering-review/
|-- SKILL.md
|-- modes/                learn, evolve, compare, predict
|-- knowledge/            created locally by learn mode; not shipped here
|-- scripts/              generic collection and analysis tooling
`-- evidence/             raw local provenance; gitignored, never publish
```

## Self-Evolution Rules

1. Evidence beats memory.
2. Multiple independent examples beat one strong opinion.
3. Outcomes matter more than isolated comments, but are not proof by themselves.
4. Contradictions must be preserved.
5. Newer evidence can supersede older evidence.
6. Do not erase history. Append deltas to `knowledge/log.md` and keep current
   corpus state in `knowledge/corpus/index.md`.
7. Do not infer principles from style-only comments.
8. Do not confuse reviewer preference with correctness.
9. Do not manufacture team consensus.
10. Explicit uncertainty beats false precision.
11. A low comment count is not a finding. Do not infer engagement, competence,
    or intent from volume.
