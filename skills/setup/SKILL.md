# Setup — /setup-fuzzybee-skill

> User-invoked skill. Run once per repository to configure fuzzybee.

## When to invoke

- First time using fuzzybee in a repository
- After upgrading fuzzybee version
- To reconfigure evidence dir, telemetry tier, or dependencies

## What it does

### 1. Evidence directory

```bash
mkdir -p docs/status/execution-gates/
```

### 2. Telemetry prompt

Ask user for telemetry tier: `off` (default), `anonymous`, or `community`.

```bash
fuzzybee-config set telemetry community
```

### 3. Dashboard dependencies (optional)

If user wants the dashboard:

```bash
# Expo is a HARD requirement for the dashboard
npx create-expo-app fuzzybee-dashboard --template blank --no-install 2>/dev/null || true
touch ~/.fuzzybee/.dashboard-configured
```

Without Expo, dashboard mode is unavailable. User can run setup again later.

### 4. Memory backend

Check for PostgreSQL + pgvector (for mem0). If unavailable:

```bash
fuzzybee-config set memory_backend jsonl
# Fallback: file-based JSONL memory, no semantic search
```

### 5. Multi-platform detection

```bash
detect_platforms() {
    local platforms=()
    [ -d "$HOME/.claude/skills" ] && platforms+=("claude-code")
    [ -d "$HOME/.codex/skills" ] && platforms+=("codex-cli")
    [ -d "$HOME/.cursor/skills" ] && platforms+=("cursor")
    echo "${platforms[@]}"
}
```

### 6. Write config

```bash
fuzzybee-config set evidence_dir docs/status/execution-gates/
fuzzybee-config set skill_prefix false
fuzzybee-config set explain_level default
```

## Post-setup verification

```bash
fuzzybee-health
# Should print: ALL CHECKS PASS
```
