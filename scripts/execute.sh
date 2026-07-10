#!/usr/bin/env bash
# Backward-compat wrapper — delegates to bin/fuzzybee-execute
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
exec "$SCRIPT_DIR/bin/fuzzybee-execute" "$@"
