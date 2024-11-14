#!/usr/bin/env bash

set -eau

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
echo "         Compose Up Finished          "
echo "======================================"
echo ""
echo "If this is the first time running compose
echo "up, run the following post-install scripts:"
echo ""
echo "./trino/setup_iceberg.sh"
echo "./superset/setup_db_connections.sh"
echo "./nifi/postinstall.sh"

