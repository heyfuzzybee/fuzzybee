---
name: fuzzybee
description: Recursive verify skill — Reason → Act → Verify → Prove → Recurse with evidence gates
metadata:
  version: 0.1.0
  source: Charles Liuson
  preamble-tier: full
---

## When to invoke

Use when the user asks to: "execute a plan", "verify a change", "run a cycle",
"decompose this task", "prove it works", "show evidence", or any multi-step task
that needs gated verification. Proactively suggest when the user says
"I think it works" without evidence.

## STOP GATES

| Gate | Condition | Action |
|------|-----------|--------|
| S1 | 8 tool calls OR 10 min wall clock | BLOCKED, file remaining as new task |
| S2 | 3 consecutive gate failures on same unit | BLOCKED, write memory, report |
| S3 | EvidenceRecord status != PASS | STOP, DO NOT report success |
| S4 | DATABASE_URL contains "localhost" in deploy | BLOCKED, never deploy |

## Workflow

1. **Decompose** — Classify problem type, break into verifiable units
2. **Execute** — Run each unit: Reason → Act → Verify → gate
3. **Report** — Structured markdown with evidence, SLA status
4. **Learn** — Log cycle outcome to JSONL for pattern detection

## CLI

```bash
fuzzybee-execute health          # Check system health
fuzzybee-execute decompose "..." # Break problem into units
fuzzybee-dashboard               # Start localhost:3333 dashboard
fuzzybee-config get telemetry    # Read config value
fuzzybee-config set telemetry anonymous  # Set config value
```

## Dashboard

Zero-dependency dashboard at http://localhost:3333:
- `/` — Overview (cycles, pass rate, active)
- `/burn` — Burn report (token usage, duration, pass rate)
- `/cycles` — Cycle history with filters
- `/cycles/{id}` — Single cycle detail with evidence
- `/cycles/{id}/evidence` — Raw evidence JSON
- `/agents` — Agent monitor
- `/analytics` — Pattern clusters
- `/api/cycles/stream` — SSE live updates


## Skill Integrations

Execute-skill is designed to work with the broader agent skill ecosystem.
See [references/skill-integration.md](references/skill-integration.md) for:
- Recommended skill stack (14 skills mapped)
- 4 integration patterns (pre-flight, gate, chaining, enrichment)
- Usage examples with `/skill:` and `/flow:` commands

## Flow Skill Variant

For automated multi-turn execution, use the flow skill:
```
/flow:fuzzybee
```
This runs the full Reason → Act → Verify → Recurse cycle automatically.

## Files

- `lib/engine.py` — Core execution engine
- `lib/gate.py` — Gate runner + evidence records
- `lib/decompose.py` — Problem classifier + strategies
- `lib/sla.py` — SLA enforcement (3-strike, wall clock, tool limits)
- `lib/learn.py` — Instinct logger + confidence decay
- `lib/memory.py` — File/SQLite/mem0 adapters
- `lib/report.py` — Markdown report generation
- `lib/session.py` — Session detection
- `lib/telemetry.py` — 3-tier privacy logger
- `lib/dashboard.py` — Pure Python http.server + HTMX dashboard
- `lib/security.py` — Injection sanitizer + secret redactor
