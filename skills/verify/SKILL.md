---
name: execute-verify
description: Re-run gates to confirm pass/fail status
---

## When to invoke

The agent should reach for this skill when:
- A previous gate result is questioned
- Evidence needs independent confirmation
- A fix needs re-verification after changes

## Workflow

1. Retrieve original pass_criteria from unit
2. Re-run gate with same command
3. Compare new result vs original
4. Flag discrepancies

## Re-verification Gate

```python
record = gate_runner.run(
    gate_name=f"{unit.task_id}-verify",
    command=unit.pass_criteria,
)
```
