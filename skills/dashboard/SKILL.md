---
name: execute-dashboard
description: Local observability dashboard (Expo required for web mode)
---

## When to invoke

The agent should reach for this skill when:
- User asks for "status", "overview", "burn report"
- Evidence needs visual inspection
- Real-time cycle monitoring is needed

## Hard requirement: Expo (web mode)

The web dashboard requires Expo. Without it, only terminal mode is available.

```bash
# Check if configured for Expo mode
if [ -f ~/.fuzzybee/.dashboard-configured ]; then
  echo "Dashboard configured — Expo available"
else
  echo "Dashboard not configured. Run: /setup-fuzzybee-skill"
  echo "Falling back to terminal mode"
fi
```

## Endpoints (Expo mode)

| Path | Content |
|------|---------|
| / | Overview: cycles, pass rate, active, blocked |
| /burn | Burn report: tokens, duration, pass rate |
| /cycles | Cycle history with status filters |
| /cycles/{id} | Single cycle detail with evidence |
| /cycles/{id}/evidence | Raw evidence JSON |
| /agents | Agent monitor |
| /analytics | Pattern clusters |
| /api/cycles/stream | SSE live updates |

## Technology

- Terminal mode: Python rich or tabulate (lightweight)
- Expo web mode: React Native + Expo Router (full dashboard)
- SQLite WAL — concurrent-safe storage
