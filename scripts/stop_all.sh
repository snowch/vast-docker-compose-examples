#!/usr/bin/env bash

# Check if 'docker compose' (Docker v2) or 'docker-compose' (Docker v1) is available
if command -v docker compose &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker-compose"
else
  echo "Neither 'docker compose' nor 'docker-compose' command found. Please install Docker Compose."
  exit 1
fi

for dir in $(ls -d */ | grep -v "^demos/" | grep -v "^scripts/"); do
  if [ -f "$dir/docker-compose.yml" ] || [ -f "$dir/docker-compose.yaml" ]; then
    (cd "$dir" && $DOCKER_COMPOSE_CMD down)
  else
    echo "No docker-compose.yml or docker-compose.yaml found in $dir, skipping."
  fi
done
