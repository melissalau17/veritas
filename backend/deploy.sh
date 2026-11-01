#!/bin/bash

set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAGE_DIR="$(mktemp -d "$BACKEND_DIR/.worker-deploy.XXXXXX")"
SOURCE_DIR="$STAGE_DIR/source"

cleanup() {
    rm -rf "$STAGE_DIR"
}
trap cleanup EXIT

cd "$BACKEND_DIR"
uv run --project "$BACKEND_DIR" pywrangler sync

mkdir -p "$SOURCE_DIR"

cp -R \
    "$BACKEND_DIR/api" \
    "$BACKEND_DIR/assets" \
    "$BACKEND_DIR/data" \
    "$BACKEND_DIR/evaluation" \
    "$BACKEND_DIR/services" \
    "$BACKEND_DIR/src" \
    "$BACKEND_DIR/tools" \
    "$SOURCE_DIR/"
cp \
    "$BACKEND_DIR/__init__.py" \
    "$BACKEND_DIR/app.py" \
    "$BACKEND_DIR/config.py" \
    "$BACKEND_DIR/main.py" \
    "$BACKEND_DIR/schemas.py" \
    "$BACKEND_DIR/worker.py" \
    "$SOURCE_DIR/"
cp -R \
    "$BACKEND_DIR/python_modules" \
    "$STAGE_DIR/"

cat > "$STAGE_DIR/wrangler.jsonc" <<'EOF'
{
  "name": "veritas-api",
  "main": "source/worker.py",
  "base_dir": "source",
  "compatibility_date": "2026-10-30",
  "compatibility_flags": [
    "python_workers"
  ],
  "python_modules": {
    "exclude": [
      "**/*.pyc",
      "**/__pycache__/**",
      "**/tests/**",
      "**/test/**"
    ]
  }
}
EOF

cd "$STAGE_DIR"
npx wrangler deploy "$@"
