#!/usr/bin/env bash
# Install fuzzybee — one-shot, zero questions, auto-detect platform
set -euo pipefail

FUZZYBEE_HOME="${FUZZYBEE_HOME:-$HOME/.fuzzybee}"
REPO="heyfuzzybee/fuzzybee"
VERSION="${VERSION:-latest}"

echo "==> Installing fuzzybee..."

# 1. Create home directory
mkdir -p "$FUZZYBEE_HOME/bin" "$FUZZYBEE_HOME/skills"

# 2. If running from a local repo copy, use it. Otherwise download from GitHub.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/../VERSION" ]; then
  # Local install (npm postinstall or git clone)
  REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
  cp -r "$REPO_ROOT/bin" "$REPO_ROOT/lib" "$REPO_ROOT/scripts" "$REPO_ROOT/sections" \
       "$REPO_ROOT/SKILL.md" "$REPO_ROOT/VERSION" "$REPO_ROOT/CHANGELOG.md" "$REPO_ROOT/README.md" \
       "$FUZZYBEE_HOME/" 2>/dev/null || true
  cp -r "$REPO_ROOT/skills"/* "$FUZZYBEE_HOME/skills/" 2>/dev/null || true
else
  # Remote install (curl | sh)
  TMPDIR="$(mktemp -d)"
  if [ "$VERSION" = "latest" ]; then
    DOWNLOAD_URL="https://github.com/$REPO/archive/refs/heads/main.tar.gz"
  else
    DOWNLOAD_URL="https://github.com/$REPO/archive/refs/tags/v$VERSION.tar.gz"
  fi
  curl -sfL "$DOWNLOAD_URL" | tar xz -C "$TMPDIR" --strip-components=1
  cp -r "$TMPDIR/bin" "$TMPDIR/lib" "$TMPDIR/scripts" "$TMPDIR/sections" \
       "$TMPDIR/SKILL.md" "$TMPDIR/VERSION" "$TMPDIR/CHANGELOG.md" "$TMPDIR/README.md" \
       "$FUZZYBEE_HOME/" 2>/dev/null || true
  cp -r "$TMPDIR/skills"/* "$FUZZYBEE_HOME/skills/" 2>/dev/null || true
  rm -rf "$TMPDIR"
fi

# 3. Symlink bin scripts to PATH
mkdir -p "$HOME/.local/bin"
for f in "$FUZZYBEE_HOME/bin/fuzzybee-"*; do
  ln -sf "$f" "$HOME/.local/bin/$(basename "$f")"
done

# 4. Detect platform and copy SKILL.md
for platform_dir in "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.cursor/skills"; do
  if [ -d "$platform_dir" ]; then
    mkdir -p "$platform_dir/fuzzybee"
    cp "$FUZZYBEE_HOME/SKILL.md" "$platform_dir/fuzzybee/" 2>/dev/null || true
    [ -d "$FUZZYBEE_HOME/skills" ] && cp -r "$FUZZYBEE_HOME/skills"/* "$platform_dir/fuzzybee/skills/" 2>/dev/null || true
  fi
done

# 5. Verify
if [ -f "$FUZZYBEE_HOME/bin/fuzzybee-health" ]; then
  echo "==> Installed at: $FUZZYBEE_HOME"
  echo "==> Run: $FUZZYBEE_HOME/bin/fuzzybee-health"

  # Add to current PATH hint
  case ":$PATH:" in
    *:"$HOME/.local/bin":*) ;;  # already in PATH
    *) echo "==> Add to PATH: export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
  esac
else
  echo "ERROR: Install failed — fuzzybee-health not found" >&2
  exit 1
fi
