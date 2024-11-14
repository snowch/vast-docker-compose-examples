#!/usr/bin/env bash

set -x

python3 -c "import nipyapi" 2>/dev/null || pip3 install nipyapi

python3 /healthcheck.py


