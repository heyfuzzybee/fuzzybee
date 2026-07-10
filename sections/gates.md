# Gate Definitions

## GateStatus
- PASS: Command succeeded as expected
- FAIL: Command failed or output mismatch
- BLOCKED: SLA violation or escalation
- SKIPPED: Gate not run
- ERROR: Exception during execution

## EvidenceRecord Schema
```json
{
  "gate_name": "string",
  "command": "string",
  "expected": "string",
  "actual": "string",
  "status": "PASS|FAIL|BLOCKED|SKIPPED|ERROR",
  "timestamp": "ISO8601",
  "duration_ms": 0.0
}
```

## STOP GATES (SKILL.md)

| Gate | Condition | Action |
|------|-----------|--------|
| S1 | 8 tool calls OR 10 min wall clock | BLOCKED, file remaining as new task |
| S2 | 3 consecutive gate failures on same unit | BLOCKED, write memory, report |
| S3 | EvidenceRecord status != PASS | STOP, DO NOT report success |
| S4 | DATABASE_URL contains "localhost" in deploy | BLOCKED, never deploy |
