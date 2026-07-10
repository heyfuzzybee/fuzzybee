---
name: execute-sla
description: Enforce execution boundaries per unit
---

## When to invoke

The agent should reach for this skill after EVERY gate execution.

## Boundaries

| Limit | Value | Action |
|-------|-------|--------|
| MAX_TOOL_CALLS | 8 | BLOCKED, file remaining as new task |
| MAX_WALL_CLOCK_S | 600 (10 min) | BLOCKED |
| MAX_GATE_FAILURES | 3 (strike 3) | BLOCKED, write memory, report |

## Check Method

```python
violation = sla.check(
    tool_calls=unit.tool_calls,
    elapsed_s=unit.wall_clock_s,
    gate_failures=unit.gate_failures,
)
# Returns: str (violation message) or None
```

## Escalation

If violation contains "STOP" → status = BLOCKED
If tool_calls >= limit → status = BLOCKED
If gate_failures >= 3 → status = BLOCKED
