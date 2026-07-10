# Fuzzybee — Recursive Verify Skill

> Reason → Act → Verify → Prove → Recurse with evidence gates.

## Architecture

- **User-invoked skills**: `bin/fuzzybee-*` CLI tools (health, decompose, run, verify, report, dashboard, config)
- **Model-invoked skills**: `skills/*/SKILL.md` — compose automatically in Claude Code
- **Setup skill**: `/setup-fuzzybee-skill` — run once per repo
- **Evidence gates**: Every action produces `EvidenceRecord` with PASS/FAIL/BLOCKED status
- **SLA enforcement**: 8 tool calls max, 600s wall clock, 3-strike escalation

## Key files

| Path | Purpose |
|------|---------|
| `SKILL.md` | Orchestrator — entry point for Claude Code |
| `sections/contract.md` | Rules, SLA, enforcement |
| `sections/gates.md` | All 4 STOP GATES |
| `sections/CONTEXT.md` | Domain glossary |
| `lib/engine.py` | Core ExecutionEngine |
| `lib/memory.py` | mem0 → SQLite → JSONL fallback |
| `lib/gate.py` | GateRunner, EvidenceRecord |
| `scripts/execute.sh` | Bash wrapper |
| `scripts/install.sh` | Platform-aware installer |
| `skills/askme/SKILL.md` | Pre-decomposition interview |
| `skills/setup/SKILL.md` | One-time environment config |
| `skills/dashboard/SKILL.md` | Localhost :3333 dashboard |

## Dependencies

- Python 3.12+
- mem0 (60K⭐) — pgvector RAG for persistent memory
- PostgreSQL 16+ with pgvector for mem0 backend
- `http.server` + HTMX for dashboard (zero framework deps)
- Expo (optional, for web dashboard mode)

## Quick start

```bash
bash scripts/install.sh
bash scripts/execute.sh health
bash scripts/execute.sh decompose "bug: login crash on empty email"
```

## Distribution

- GitHub: `github.com/heyfuzzybee/fuzzybee`
- npm: `@heyfuzzybee/fuzzybee`
- Skills hubs: SkillsMP, SkillsLLM, LobeHub
