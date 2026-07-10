# Integration: fuzzybee + secure-code-review

## Use Case
Run OWASP security audit as a gated verification step.

## Setup
```bash
# Install both skills
npm install -g @charles-liuson/fuzzybee
# secure-code-review is a Kimi built-in skill
```

## Workflow

### Step 1: Decompose security audit
```bash
fuzzybee-execute decompose "audit auth module for SQL injection and XSS"
```
Output:
```
  [audit] sec-01-scan: Scan auth module for vulnerabilities
      pass: `/skill:code-vuln-audit scan src/auth.py`
  [audit] sec-02-analyze: Analyze findings
      pass: `bash -c 'python3 -c "import json; data=json.load(open("findings.json")); assert not any(f["severity"]=="CRITICAL" for f in data)"'`
  [fix] sec-03-fix: Fix critical issues
      pass: `bash scripts/check-14-skill-compliance.sh --gate`
```

### Step 2: Execute with skill-as-gate
```python
from lib.engine import ExecutionEngine
engine = ExecutionEngine()

unit = engine.decompose("audit auth module for SQL injection")[0]
# The pass_criteria references the skill directly
cycle = engine.execute(unit)
# EvidenceRecord captures the skill output
```

### Step 3: Chain with repo-audit for context
```
/skill:repo-audit
# → identifies auth.py as hotspot

fuzzybee-execute decompose "refactor auth.py based on repo-audit findings"
# → decomposition includes hotspot context
```

## Gate Mapping

| Fuzzybee Gate | Skill Input | Skill Output |
|-------------------|-------------|--------------|
| S3 (Evidence != PASS) | `/skill:secure-code-review scan` | Vulnerability report |
| S2 (3-strike) | `/skill:cross-examine` "why did this fail?" | Root cause analysis |
| S1 (Tool limit) | `/skill:test-suite-architect` | Optimized test plan |
