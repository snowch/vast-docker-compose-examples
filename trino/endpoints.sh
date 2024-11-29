#!/usr/bin/env bash

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local
source .env

echo "Trino Server:"
echo "https://${DOCKER_HOST_OR_IP}:8443"
echo ""

echo "Trino Server UI:"
echo "https://${DOCKER_HOST_OR_IP}:8443/ui"
echo ""

echo "Note: 404 error with trino queries happens when"
echo "      trino is unavailable, e.g. if it has crashed"
echo "      and is restarting"
