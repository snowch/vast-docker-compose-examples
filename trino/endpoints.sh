#!/usr/bin/env bash

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local
source .env

echo "Trino Server:"
echo "https://${DOCKER_HOST_OR_IP}:8443"
echo ""
