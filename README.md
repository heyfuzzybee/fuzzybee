# Fuzzybee

Reason → Act → Verify → Prove → Recurse with evidence gates.

## Install

```bash
# Option A: npm (primary)
npm install -g @heyfuzzybee/fuzzybee
fuzzybee health

# Option B: curl (zero dependencies)
curl -sf https://raw.githubusercontent.com/heyfuzzybee/fuzzybee/main/scripts/install.sh | sh
fuzzybee health
```

## Use

```bash
fuzzybee health                          # Check everything works
fuzzybee decompose "bug: login crash"    # Plan the work
fuzzybee verify --task-id 1              # Gate a claim
fuzzybee dashboard                       # Localhost :3333
fuzzybee-config set telemetry community  # Opt in
```

## Tests

```bash
pytest tests/ --cov=lib/ --cov-fail-under=64
bats tests/test_health.bats
```

## License

MIT
