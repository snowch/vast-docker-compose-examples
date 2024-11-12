#!/usr/bin/env bash

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local

echo "Kafka Broker:"
echo "${DOCKER_HOST_OR_IP}:19092"
echo ""
echo "Kafka Console:"
echo "http://${DOCKER_HOST_OR_IP}:28080"
echo ""
