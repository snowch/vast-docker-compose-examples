#!/usr/bin/env bash

# Ensure the script stops if any command fails
set -e

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local

./setup_db_connections.sh "$@"
./scripts/import_assets.sh "$@"
