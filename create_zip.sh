#!/usr/bin/env bash
# create_zip.sh — ejecuta desde la raíz del proyecto
set -e
TMPDIR=$(mktemp -d)
ROOT="$TMPDIR/cog5_scaffold"
mkdir -p "$ROOT"


# create files from this script's embedded heredocs
writefile() {
  local path="$1"; shift
  mkdir -p "$(dirname "$ROOT/$path")"
  cat > "$ROOT/$path"
}

# Note: paste the full content blocks below. If running locally, better copy the tree manually.
echo "Script created. Recommended: copy the file blocks above into actual files, then run:"
echo "cd <repo-root> && zip -r cog5_scaffold.zip src tests .github pyproject.toml README.md"