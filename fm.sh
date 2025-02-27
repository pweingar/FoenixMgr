#!/bin/bash

DIR=$(realpath $(dirname "$0"))

# Create virtual environment and install requirments.
# This is used to avoid breaking host python environment.
if [ ! -d $DIR/.venv ]; then
  python -m venv $DIR/.venv
  source $DIR/.venv/bin/activate
  pip install -r $DIR/requirements.txt
  deactivate
fi

# Launch script in virtual environment.
source $DIR/.venv/bin/activate
python $DIR/FoenixMgr/fnxmgr.py $@
deactivate
