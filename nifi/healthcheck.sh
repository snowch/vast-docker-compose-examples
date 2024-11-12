#!/usr/bin/env bash

set -x

curl --fail -k https://${NIFI_WEB_PROXY_HOST}:8443

LOCK_FILE="/tmp/import_flow_done.lock"

if [ -f "$LOCK_FILE" ]; then
  echo "The import flow has already been executed. Exiting."
  exit 0
fi

pip3 install --quiet requests nipyapi
python3 /assets/import_flow.py
python3 /assets/update_variables.py

# Create a lock file to prevent re-running
touch "$LOCK_FILE"