#!/usr/bin/env bash
set -euo pipefail

echo "=== Fuzzybee Self-Audit ==="

# Check all lib modules are importable
for mod in engine gate decompose sla learn memory report session telemetry dashboard; do
    python3 -c "import lib.$mod" || { echo "FAIL: cannot import lib.$mod"; exit 1; }
    echo "OK: lib.$mod"
done

# Check bin scripts are executable
for script in bin/fuzzybee-*; do
    if [ ! -x "$script" ]; then
        echo "FAIL: $script not executable"
        exit 1
    fi
    echo "OK: $script"
done

# Check evidence dir exists (engine creates it on first cycle)
if [ -d "docs/status/execution-gates" ]; then
  echo "OK: evidence dir exists"
else
  echo "INFO: evidence dir will be created on first cycle"
fi

echo "=== Audit PASSED ==="
