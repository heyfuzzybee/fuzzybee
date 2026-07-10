# Fuzzybee

Recursive verify skill for Claude Code. Reason → Act → Verify → Prove → Recurse with evidence gates.

## Quick Start

```bash
# Install
bash scripts/install.sh

# Health check
bash scripts/execute.sh health

# Decompose a problem
bash scripts/execute.sh decompose "bug: login crash on empty email"

# Run a full cycle
bash scripts/execute.sh run "bug: login crash on empty email"
```

### npm

```bash
npm install -g @heyfuzzybee/fuzzybee
fuzzybee health
fuzzybee decompose "bug: login crash on empty email"
```

## Architecture

See `sections/` for contract, workflow, gates, and integration docs.

## Tests

```bash
pytest tests/ --cov=lib/ --cov-fail-under=64
bats tests/test_health.bats
```

## License

MIT
