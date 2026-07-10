# Workflow

1. **Detect** — Session kind, telemetry tier, health check
2. **Decompose** — Classify → break into units with pass_criteria
3. **Execute** — For each unit: run gate → record evidence → SLA check
4. **Verify** — Re-run gate on demand
5. **Report** — Markdown with evidence summary
6. **Learn** — Log pattern to JSONL
