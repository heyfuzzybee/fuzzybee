#!/usr/bin/env bash
# Platform-aware installer
set -euo pipefail

detect_platforms() {
    local platforms=()
    [ -d "$HOME/.claude/skills" ] && platforms+=("claude-code")
    [ -d "$HOME/.codex/skills" ] && platforms+=("codex-cli")
    [ -d "$HOME/.cursor/skills" ] || [ -f ".cursor/rules" ] && platforms+=("cursor")
    [ -d "$HOME/.gemini/skills" ] && platforms+=("gemini-cli")
    [ -d "$HOME/.agent/skills" ] && platforms+=("opencode")
    echo "${platforms[@]}"
}

PLATFORMS=$(detect_platforms)
echo "Detected platforms: $PLATFORMS"

SKILL_DIR="$HOME/.claude/skills/fuzzybee"
mkdir -p "$SKILL_DIR"

# Copy files
cp -r bin lib scripts sections SKILL.md VERSION CHANGELOG.md README.md "$SKILL_DIR/" 2>/dev/null || true

echo "Installed to $SKILL_DIR"
echo "Add to PATH: export PATH="$SKILL_DIR/bin:\$PATH""
