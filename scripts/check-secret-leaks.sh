#!/usr/bin/env bash
set -euo pipefail

echo "Scanning for secret patterns..."

PATTERNS=(
    "shpat_"
    "shpss_"
    "shpca_"
    "atkn_"
    "sk_live_"
    "AKIA"
    "sk-proj-"
)

FOUND=0
for pattern in "${PATTERNS[@]}"; do
    if grep -r "$pattern" lib/ tests/ scripts/ bin/ 2>/dev/null; then
        echo "SECRET PATTERN FOUND: $pattern" >&2
        FOUND=1
    fi
done

if [ "$FOUND" -eq 1 ]; then
    exit 1
fi

echo "No secret patterns found."
