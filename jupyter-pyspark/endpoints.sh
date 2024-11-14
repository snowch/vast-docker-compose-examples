#!/usr/bin/env bash

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local

# Check if 'docker compose' (Docker v2) or 'docker-compose' (Docker v1) is available
if docker compose version &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker compose"
elif docker-compose version &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker-compose"
else
  echo "Neither 'docker compose' nor 'docker-compose' command found. Please install Docker Compose."
  exit 1
fi

TOKEN=$($DOCKER_COMPOSE_CMD logs | grep 'jupyter-pyspark-1 *| *http://127.0.0.1:8888/lab?token=' | awk -F'token=' '{print $2}')

echo "Jupyter-Spark:"
echo "http://${DOCKER_HOST_OR_IP}:8888/lab?token=${TOKEN}"
echo ""
