#!/usr/bin/env bash

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local

echo "Superset:"
echo "http://${DOCKER_HOST_OR_IP}:8088"
echo "Username: admin"
echo "Password: admin"
echo ""
