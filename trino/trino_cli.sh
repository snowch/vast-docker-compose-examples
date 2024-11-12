#!/usr/bin/env bash

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local

docker exec -it trino trino --server https://${DOCKER_HOST_OR_IP}:8443 --insecure
