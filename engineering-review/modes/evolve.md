# Mode: Evolve

Update an existing model with new evidence. This is evidence-driven knowledge
maintenance, not free-form rewriting.

## Workflow

1. Collect evidence beginning at the previous model's cutoff date.
2. Build review events and compare them with existing principles.
3. Find supporting and contradicting evidence for each relevant principle.
4. Record changed opinions with dates and both old and new positions.
5. Update confidence, first observed, and last observed dates.
6. Promote a principle only when the evidence supports it.
7. Mark abandoned principles `deprecated` instead of deleting them.

## Never Silently Rewrite

When a statement changes, preserve the superseded statement and explain which
evidence changed the model. Historical principles remain useful because they
show what the team previously enforced and prevent stale evidence from being
relearned as current judgment.

## Persist

Append one newest-first delta entry to `knowledge/log.md` containing the evidence
window, corpus delta, new principles, changed principles with old text,
deprecated principles, and reconfirmed principles.

Update `knowledge/corpus/index.md` in place with current scale, outcome
distribution, limitations, and backlog. Then update only affected reviewer,
principle, surface, and convention concepts.

Do not create a complete model snapshot for every run. The log carries history;
the concepts and corpus index carry current state.

Validate with:

```sh
python3 scripts/validate_okf.py .
```
