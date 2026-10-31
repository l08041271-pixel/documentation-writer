#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BASELINE="d797acfbf7d329c35070d0b1e0234f5e45bf1a1c"

echo "=== RELEASE READINESS CHECK ==="

BRANCH="$(git branch --show-current)"
if [[ "$BRANCH" != "develop" ]]; then
    echo "ERROR: Release preparation must run on develop."
    exit 1
fi

echo "PASS: Current branch is develop."

if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERROR: Working tree must be clean."
    git status --short
    exit 1
fi

echo "PASS: Working tree is clean."

if ! git rev-parse -q --verify 'v1.0.0^{commit}' >/dev/null; then
    echo "ERROR: v1.0.0 tag is missing."
    exit 1
fi

TAG_COMMIT="$(git rev-parse 'v1.0.0^{commit}')"

if [[ "$TAG_COMMIT" != "$BASELINE" ]]; then
    echo "ERROR: v1.0.0 does not match the protected baseline."
    exit 1
fi

echo "PASS: v1.0.0 baseline is unchanged."

if ! git merge-base --is-ancestor v1.0.0 HEAD; then
    echo "ERROR: develop does not descend from v1.0.0."
    exit 1
fi

echo "PASS: Development history preserves v1.0.0."

python3 scripts/validate_skill.py
python3 -m unittest discover -s tests -v

echo "=== RELEASE CHECKS PASSED ==="
echo "This script does not create tags, publish releases, or push changes."
