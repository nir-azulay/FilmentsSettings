#!/usr/bin/env bash
# Point this clone's git at the repo-managed hooks in .githooks/.
#
# Idempotent. Re-run any time after a clone or after pulling new hooks. Does
# not touch your global git config.
#
# After running, `git commit` will execute .githooks/pre-commit (et al.).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -d .githooks ]]; then
    echo "install-git-hooks: no .githooks/ directory in repo root" >&2
    exit 1
fi

chmod +x .githooks/*

git config core.hooksPath .githooks
echo "install-git-hooks: core.hooksPath set to .githooks (this repo only)"
ls .githooks/ | sed 's/^/  - /'
