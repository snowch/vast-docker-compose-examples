#!/usr/bin/env bash

# Check if 'docker compose' (Docker v2) or 'docker-compose' (Docker v1) is available
if docker compose version &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker compose"
elif docker-compose version &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker-compose"
else
  echo "Neither 'docker compose' nor 'docker-compose' command found. Please install Docker Compose."
  exit 1
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
