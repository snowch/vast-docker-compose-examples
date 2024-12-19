#!/usr/bin/env bash

source ../.env-local
export VASTDB_ENDPOINT
export VASTDB_ACCESS_KEY
export VASTDB_SECRET_KEY

export VASTDB_NETFLOW_BUCKET
export VASTDB_NETFLOW_SCHEMA
export VASTDB_NETFLOW_TABLE

MODULE_NAME="vastdb"

if ! python3 -c "import $MODULE_NAME" 2>/dev/null; then
    echo "Error: Python module '$MODULE_NAME' is not installed. Please install it using 'pip install $MODULE_NAME'." >&2
    exit 1
fi

while :
do
        python3 netflow_load_batch.py
        echo -n "."
        sleep 9
done






