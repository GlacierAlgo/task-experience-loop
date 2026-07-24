#!/usr/bin/env bash
# Install TEL skills into both Codex and Claude Code skill directories.
#
# Symlink strategy: each skill in ./skills/ (plus _shared) is linked into
# ~/.codex/skills/ and ~/.claude/skills/. Edit the repo once; both tools see
# it immediately. The repo is the single source of truth.
#
# Only skill directories that contain a SKILL.md are installed. Unrelated
# skills already present in the target directories are left untouched.

set -euo pipefail

REPO_SKILLS="$(cd "$(dirname "$0")/skills" && pwd)"
TARGETS=("$HOME/.codex/skills" "$HOME/.claude/skills")

link_into() {
  local target="$1"

  # A dangling symlink target (points nowhere) is replaced with a real dir.
  if [ -L "$target" ] && [ ! -e "$target" ]; then
    echo "warn: $target is a dangling symlink -> $(readlink "$target"); replacing with a real directory"
    rm "$target"
  fi
  mkdir -p "$target"

  # Prune only stale symlinks previously managed by this repository.
  local existing existing_src
  for existing in "$target"/*; do
    [ -L "$existing" ] || continue
    existing_src="$(readlink "$existing")"
    case "$existing_src" in
      "$REPO_SKILLS"/*)
        if [ ! -e "$existing_src" ]; then
          rm "$existing"
          echo "  pruned stale $(basename "$existing") -> $existing"
        fi
        ;;
    esac
  done

  local src name link
  for src in "$REPO_SKILLS"/*/; do
    src="${src%/}"
    name="$(basename "$src")"
    # Install _shared (norms) and any directory with a SKILL.md.
    if [ "$name" != "_shared" ] && [ ! -f "$src/SKILL.md" ]; then
      continue
    fi
    link="$target/$name"
    if [ -L "$link" ] || [ -e "$link" ]; then
      rm -rf "$link"
    fi
    ln -s "$src" "$link"
    echo "  linked $name -> $link"
  done
}

for target in "${TARGETS[@]}"; do
  echo "Installing TEL skills into $target"
  link_into "$target"
done

echo "Done. Skills are symlinked from $REPO_SKILLS into Codex and Claude Code."
