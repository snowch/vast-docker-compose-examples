#!/usr/bin/env bash

# Check if 'docker compose' is available; if not, use 'docker-compose'
DOCKER_COMPOSE_CMD="docker compose"
if ! command -v docker compose &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker-compose"
fi

for dir in $(ls -d */ | grep -v "^demos/" | grep -v "^scripts/"); do
  (cd $dir && $DOCKER_COMPOSE_CMD down)
done
