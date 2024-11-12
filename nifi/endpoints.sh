#!/usr/bin/env bash

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local
source .env

echo "NiFi:"
echo "https://${DOCKER_HOST_OR_IP}:${EXT_NIFI_PORT}"
echo ""
