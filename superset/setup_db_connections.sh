#!/usr/bin/env bash

# Ensure the script stops if any command fails
set -e

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local

# Docker image and container name (update with your image and container name)
IMAGE_NAME="python:3.10-slim"  # Replace with your Python image name
CONTAINER_NAME="setup_superset_dbs"

# Create a Docker container with the necessary setup to run the Python script
docker run --rm \
  --name $CONTAINER_NAME \
  --network host \
  -e DOCKER_HOST_OR_IP=$DOCKER_HOST_OR_IP \
  -v $(pwd):/app \
  $IMAGE_NAME /bin/bash -c "
    # Install necessary dependencies
    pip install --no-cache-dir --quiet superset-api-client && \

    # Run the Python script to set up the database connections
    python /app/setup_db_connections.py
  "

