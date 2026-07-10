---
name: execute-learn
description: Log cycle outcomes to JSONL for pattern detection
---

## When to invoke

The agent should reach for this skill after EVERY cycle completion.

## Log Format

```json
{
  "pattern": "bug:PASS",
  "confidence": 1.0,
  "problem_type": "bug",
  "gate_outcome": "PASS",
  "tool_count": 4,
  "duration_ms": 45000,
  "timestamp": "2026-07-09T16:00:00"
}
```

## Confidence Decay

Weekly: confidence -= 0.1 per week old
Purpose: prevent stale patterns from dominating

## Clustering

Group by pattern → identify reusable strategies
Example: "bug:PASS" cluster → "this bug type usually passes in 3 units"
