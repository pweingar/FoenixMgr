#!/bin/bash

DIR=$(realpath $(dirname "$0"))

# Prefer uv when available. fnxmgr.py carries its lightweight runtime
# dependency declaration, so uv can provision and launch it directly.
if command -v uv >/dev/null 2>&1; then
  exec uv run "$DIR/FoenixMgr/fnxmgr.py" "$@"
fi

# Detect if python3 or python installed
if command -v python3 >/dev/null 2>&1; then
  PYTHON_EXEC=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON_EXEC=python
else
  echo "Python is not installed."
  exit 1
fi

# Create virtual environment and install requirments.
# This is used to avoid breaking host python environment.
if [ ! -d $DIR/.venv ]; then
  $PYTHON_EXEC -m venv $DIR/.venv
  source $DIR/.venv/bin/activate
  pip install -r $DIR/requirements.txt
  deactivate
fi

# Launch script in virtual environment.
source $DIR/.venv/bin/activate
$PYTHON_EXEC "$DIR/FoenixMgr/fnxmgr.py" "$@"
deactivate
