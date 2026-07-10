# Fuzzybee — Domain Glossary

## Core Concepts

| Term | Definition |
|------|-----------|
| **Cycle** | One complete run: Reason → Act → Verify → gate. Produces a CycleReport. |
| **Unit** | A single verifiable task within a cycle. Has type, pass_criteria, evidence list. |
| **Gate** | A verification check (command run + expected output). Produces PASS/FAIL/BLOCKED. |
| **Evidence** | Structured record of a gate execution: command, expected, actual, status, timestamp. |
| **SLA** | Time and resource limits per cycle: 8 tool calls, 10 min wall clock, 3 gate failures. |
| **STOP GATE** | Irreversible halt condition. S1–S4. |
| **Decomposition** | Breaking a problem into verifiable units. 7 problem types, each with specific strategies. |
| **mem0** | Universal memory layer (60K⭐). pgvector RAG for cross-session semantic recall. |
| **Fallback chain** | mem0 → SQLite (WAL) → JSONL. Each tier degrades gracefully. |

## Gate Status

| Status | Meaning |
|--------|---------|
| PASS | Command exited 0, output matched expected |
| FAIL | Command exited non-0 or output didn't match |
| BLOCKED | SLA exceeded or 3-strike escalation |
| SKIPPED | Not yet executed |
| ERROR | Subprocess crashed, timeout, or unexpected error |

## Problem Types

| Type | Units | Strategy |
|------|-------|----------|
| BUG | 3 | Reproduce → Root cause → Fix + verify |
| FEATURE | 4 | Spec → Architecture → Implementation → Verification |
| AUDIT | 3 | Scan → Analyze → Fix |
| MEMORY | 2 | Check → Store |
| DEPLOY | 3 | Pre-check → Deploy → Verify |
| DESIGN | 3 | Review → Implement → Polish |
| GENERIC | 2 | Research → Implement |
