#!/usr/bin/env bash
set -euo pipefail

echo "[postStart] Starting post-start tasks..."

echo "[postStart] Re-installing pre-commit hooks to ensure environment is ready..."
python3 -m pre_commit install -f

echo "[postStart] Running pre-commit across all files (non-blocking, show diffs on failure)..."
python3 -m pre_commit run --all-files --show-diff-on-failure || true

echo "[postStart] Completed."
