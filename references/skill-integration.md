# Skill Integration Guide

This document maps external Kimi/Claude/Codex skills to fuzzybee capabilities.
Install these skills alongside fuzzybee for enhanced workflows.

## Recommended Skill Stack

| Skill | Source | Users | Maps to Fuzzybee |
|-------|--------|-------|----------------------|
| **test-suite-architect** | Daymade | 28.2K | Decompose → Test Strategy + Gate Verification |
| **secure-code-review** | Kimi | 38.5K | Security Audit Gate (S4) + OWASP Testing |
| **code-vuln-audit** | Kimi | 15.4K | Dependency Scan Gate + Secret Detection |
| **repo-audit** | Kimi | 49.2K | Health Check + Git History Analysis |
| **conventional-commit-gen** | Kimi | 12.2K | Evidence Commit Messages |
| **test-driven-dev** | Matt Pocock | 15.7K | Red-Green-Refactor Cycle |
| **cross-examine** | Matt Pocock | 7.6K | Skeptic Audit Gate |
| **deep-module-refactor** | Matt Pocock | 22.3K | Decompose → Refactor Strategy |
| **domain-glossary** | Matt Pocock | 6.2K | Problem Classification Context |
| **pipeline-blueprint** | Chenyingjiang | 12.6K | CI/CD Gate Templates |
| **log-error-digest** | Kimi | 26.3K | Evidence Analysis + Pattern Clustering |
| **dataset-quality-audit** | Kimi | 45.2K | Data Validation Gate |
| **data-viz-renderer** | Kimi | 30.4K | Dashboard Visualization |
| **browse** | Browserbase | 37.4K | External Verification Gate |

## Integration Patterns

### Pattern 1: Pre-Flight Skill Load
Before executing a cycle, load domain-specific skills:
```
/skill:secure-code-review
/skill:test-suite-architect
fuzzybee-execute decompose "audit auth module for OWASP compliance"
```

### Pattern 2: Skill-as-Gate
Use skill output as pass criteria for a gate:
```python
unit = Unit(
    task_id="security-01",
    subject="OWASP Top 10 scan",
    unit_type=UnitType.AUDIT,
    pass_criteria="`/skill:code-vuln-audit scan src/auth.py`",
)
```

### Pattern 3: Skill Chaining
Chain multiple skills through fuzzybee's decomposition:
1. `/skill:repo-audit` → identify hotspots
2. `/skill:deep-module-refactor` → plan refactor
3. `fuzzybee-execute` → verify each refactoring unit

### Pattern 4: Evidence Enrichment
Use skills to enrich evidence records:
- `/skill:log-error-digest` → analyze failure logs
- `/skill:data-viz-renderer` → generate failure charts
- Store in evidence JSON for dashboard display
