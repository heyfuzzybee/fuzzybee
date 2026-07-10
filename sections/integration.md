# Integration

## Memory
- File adapter: `~/.execute/memory/*.json`
- SQLite adapter: `~/.execute/cycles.db` (WAL mode)
- mem0 adapter: fallback to SQLite

## Telemetry
- OFF (default): nothing logged
- ANONYMOUS: skill, duration, pass/fail counts
- COMMUNITY: + cycle type, problem type, gate outcomes

## Git
- Branch detection in health check
- Evidence dir committed as build artifact
