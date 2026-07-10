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
