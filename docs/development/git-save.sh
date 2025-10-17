#!/usr/bin/env bash
set -euo pipefail
MSG="${*:-chore: save work}"
git add -A
git commit -m "$MSG" || echo "Nothing to commit."
git push -u origin main
