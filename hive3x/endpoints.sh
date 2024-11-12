#!/usr/bin/env bash

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local
source .env

echo "Hive Thift Server:"
echo "thrift://${DOCKER_HOST_OR_IP}:${EXT_HIVE_SERVER2_THRIFT_PORT}"
echo ""
echo "Hive Web UI:"
echo "http://${DOCKER_HOST_OR_IP}:${EXT_HIVE_SERVER2_WEB_UI_PORT}"
