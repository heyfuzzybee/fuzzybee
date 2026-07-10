# Execution Contract

## SLA
- MAX_TOOL_CALLS: 8
- MAX_WALL_CLOCK_S: 600 (10 min)
- MAX_GATE_FAILURES: 3 (strike 3 = BLOCKED)

## Evidence Requirements
Every gate produces an EvidenceRecord with: gate_name, command, expected, actual, status, timestamp, duration_ms.

## Stop Conditions
1. 3-strike escalation → BLOCKED
2. Wall clock exceeded → BLOCKED
3. Tool call limit → BLOCKED
4. Unverified claim → STOP, no success report
