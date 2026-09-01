# Mode: Compare

Compare reviewers or teams. Identify consensus, disagreement, reviewer-specific
preferences, differing risk tolerances, and areas without an established
position.

## Rules

Do not collapse disagreement into a single best practice. If two reviewers
genuinely disagree, that is the finding.

Identify shared principles, conflicting principles, different risk thresholds,
different areas of attention, and different interpretations of the same
historical examples. Reviewers may hold the same principle for different
reasons; preserve their distinct framing.

## Output

```markdown
## Shared
<principles both hold, with each reviewer's framing>

## Conflicting
| Principle | Reviewer A | Reviewer B | Evidence |
|---|---|---|---|

## Different Attention
<what each inspects that the other does not>

## Different Risk Thresholds
<where one is conservative and the other permissive>

## No Established Position
<where neither has evidence>
```

## Building a Review Panel

Prefer complementary coverage over the most vocal reviewers. Use the coverage
map in `knowledge/surfaces/index.md` to choose reviewers who have evidence on the
changed surface. Add independent correctness and security passes where learned
coverage is weak.
