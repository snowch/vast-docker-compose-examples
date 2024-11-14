#!/usr/bin/env bash

# Check if 'docker compose' is available; if not, use 'docker-compose'
DOCKER_COMPOSE_CMD="docker compose"
if ! command -v docker compose &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker-compose"
fi

for dir in $(ls -d */ | grep -v "^demos/" | grep -v "^scripts/"); do
  (cd $dir && $DOCKER_COMPOSE_CMD up -d && $DOCKER_COMPOSE_CMD up --wait)
done

echo "======================================"
echo "        Starting Trino Setup          "
echo "======================================"
./trino/setup_iceberg.sh

echo "======================================"
echo "       Starting Superset Setup        "
echo "======================================"
./superset/setup_db_connections.sh

echo "======================================"
echo "       All Setup Tasks Complete       "
echo "======================================"
