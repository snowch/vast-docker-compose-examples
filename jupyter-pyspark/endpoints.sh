#!/usr/bin/env bash

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local

TOKEN=$(docker compose logs | grep 'jupyter-pyspark-1 *| *http://127.0.0.1:8888/lab?token=' | awk -F'token=' '{print $2}')

echo "Jupyter-Spark:"
echo "http://${DOCKER_HOST_OR_IP}:8888"
echo "Token: ${TOKEN}"
echo ""
