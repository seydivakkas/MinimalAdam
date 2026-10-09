#!/usr/bin/env sh
set -eu
HERE="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
python3 "$HERE/start_studio.py" "$@"
