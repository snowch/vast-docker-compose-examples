#!/usr/bin/env bash

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local

# Check if 'docker compose' is available; if not, use 'docker-compose'
DOCKER_COMPOSE_CMD="docker compose"
if ! command -v docker compose &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker-compose"
fi

TOKEN=$($DOCKER_COMPOSE_CMD logs | grep 'jupyter-pyspark-1 *| *http://127.0.0.1:8888/lab?token=' | awk -F'token=' '{print $2}')

echo "Jupyter-Spark:"
echo "http://${DOCKER_HOST_OR_IP}:8888/lab?token=${TOKEN}"
echo ""
