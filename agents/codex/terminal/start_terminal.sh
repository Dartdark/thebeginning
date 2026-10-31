#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [[ -n "${THEBEGINNING_PYTHON:-}" ]]; then
  exec "$THEBEGINNING_PYTHON" server.py --open
elif [[ -x /workspace/venvs/thebeginning/bin/python ]]; then
  exec /workspace/venvs/thebeginning/bin/python server.py --open
else
  exec python3 server.py --open
fi
