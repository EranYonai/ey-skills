# Mode: Predict

Use for: "What would this reviewer think of this change?"

Do not impersonate or pretend to know. The goal is a prediction grounded in
historical evidence.

## Output

```markdown
## Likely Concerns
<principle ID and historical basis for each>

## Likely Acceptable
<what evidence suggests they would pass over>

## Uncertain
<areas where their history is inconsistent>

## No Historical Evidence
<surfaces they have not reviewed>

## Confidence
high / moderate / weak evidence / none
```

## Calibration

| Level | Basis |
|---|---|
| high confidence | repeated and consistent evidence across distinct changes |
| moderate | several observations or one explicit general statement |
| weak evidence | one or two observations or contradictory evidence |
| no historical evidence | do not extrapolate |

Write: "This matches a pattern the reviewer has challenged repeatedly."

Never write: "The reviewer would reject this."

Predicting silence is also a prediction. If the evidence suggests approval
without comment, say so while acknowledging that the data may not explain why.
