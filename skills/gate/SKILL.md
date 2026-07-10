---
name: execute-gate
description: Run pass/fail commands and record structured evidence
---

## When to invoke

The agent should reach for this skill when:
- A unit needs verification
- Evidence must be persisted for audit
- A gate command needs to run with timeout

## Workflow

1. **Parse command** — Backtick expression or shell command
2. **Execute** — Run with subprocess, capture stdout/stderr
3. **Compare** — Match actual vs expected outcome
4. **Record** — Produce EvidenceRecord with:
   - gate_name, command, expected, actual
   - status (PASS/FAIL/BLOCKED/SKIPPED/ERROR)
   - timestamp, duration_ms
   - evidence_file (JSON path)

## Evidence Directory

`docs/status/execution-gates/` — auto-created, committed as build artifact

## Stop Conditions

- Timeout: default 30s, configurable per gate
- Exit code mismatch → FAIL
- Exception → ERROR
- Timeout → FAIL with "TIMEOUT" in actual
