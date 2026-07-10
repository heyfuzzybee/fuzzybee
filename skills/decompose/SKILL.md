---
name: execute-decompose
description: Classify problem type and break into verifiable units
---

## When to invoke

The agent should reach for this skill when:
- A new task arrives and needs breakdown
- The problem type is unknown (bug/feature/audit/deploy/design)
- Pass criteria need to be defined for each unit

## Workflow

1. **Classify** — Detect problem type from keywords:
   - BUG: crash, error, fail, broken, exception, traceback
   - FEATURE: add, implement, build, create, new, support
   - AUDIT: audit, review, scan, assess, compliance, gap
   - DEPLOY: deploy, release, ship, publish, push
   - DESIGN: design, architecture, refactor, restructure

2. **Decompose** — Break into 2-4 verifiable Unit objects:
   - Bug: reproduce → root-cause → fix+verify (3 units)
   - Feature: spec → architecture → implementation → verification (4 units)
   - Audit: scan → analyze → fix (3 units)
   - Generic: analyze → act (2 units)

3. **Define pass criteria** — Each unit gets a backtick command:
   - `bats tests/api/test_sentinel.bats`
   - `pytest tests/ -x`
   - `bash scripts/self-audit.sh`

## Output Format

Return a list of Unit objects with:
- task_id: unique identifier
- subject: human-readable description
- unit_type: decomposition/build/verify/integration/fix/audit
- pass_criteria: backtick command or natural language gate
- parent_task: optional parent reference
