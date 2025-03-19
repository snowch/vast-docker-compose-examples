#!/usr/bin/env bash

# Ensure the script stops if any command fails
set -eua

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local

# Export all variables defined in the .env-local file
export DOCKER_HOST_OR_IP=$DOCKER_HOST_OR_IP
export VASTDB_ENDPOINT=$VASTDB_ENDPOINT
export VASTDB_ACCESS_KEY=$VASTDB_ACCESS_KEY
export VASTDB_SECRET_KEY=$VASTDB_SECRET_KEY
export VASTDB_TWITTER_INGEST_BUCKET=$VASTDB_TWITTER_INGEST_BUCKET
export VASTDB_TWITTER_INGEST_SCHEMA=$VASTDB_TWITTER_INGEST_SCHEMA
export VASTDB_TWITTER_INGEST_TABLE=$VASTDB_TWITTER_INGEST_TABLE
export VASTDB_BULK_IMPORT_BUCKET=$VASTDB_BULK_IMPORT_BUCKET
export VASTDB_BULK_IMPORT_SCHEMA=$VASTDB_BULK_IMPORT_SCHEMA
export VASTDB_BULK_IMPORT_TABLE=$VASTDB_BULK_IMPORT_TABLE
export VAST_KAFKA_BROKER=$VAST_KAFKA_BROKER
export S3_ENDPOINT=$S3A_ENDPOINT
export S3_ACCESS_KEY=$S3A_ACCESS_KEY
export S3_SECRET_KEY=$S3A_SECRET_KEY


# Docker image and container name (update with your image and container name)
IMAGE_NAME="python:3.10-slim"  # Replace with your Python image name
CONTAINER_NAME="setup_superset_dbs"

# Create a Docker container with the necessary setup to run the Python script
docker run --rm \
  --name $CONTAINER_NAME \
  --network host \
  -e DOCKER_HOST_OR_IP=$DOCKER_HOST_OR_IP \
  -e VASTDB_ENDPOINT=$VASTDB_ENDPOINT \
  -e VASTDB_ACCESS_KEY=$VASTDB_ACCESS_KEY \
  -e VASTDB_SECRET_KEY=$VASTDB_SECRET_KEY \
  -e VASTDB_TWITTER_INGEST_BUCKET=$VASTDB_TWITTER_INGEST_BUCKET \
  -e VASTDB_TWITTER_INGEST_SCHEMA=$VASTDB_TWITTER_INGEST_SCHEMA \
  -e VASTDB_TWITTER_INGEST_TABLE=$VASTDB_TWITTER_INGEST_TABLE \
  -e VASTDB_BULK_IMPORT_BUCKET=$VASTDB_BULK_IMPORT_BUCKET \
  -e VASTDB_BULK_IMPORT_SCHEMA=$VASTDB_BULK_IMPORT_SCHEMA \
  -e VASTDB_BULK_IMPORT_TABLE=$VASTDB_BULK_IMPORT_TABLE \
  -e VASTDB_WATERLEVEL_BUCKET=$VASTDB_WATERLEVEL_BUCKET \
  -e VASTDB_WATERLEVEL_SCHEMA=$VASTDB_WATERLEVEL_SCHEMA \
  -e VAST_KAFKA_BROKER=$VAST_KAFKA_BROKER \
  -e S3A_ENDPOINT=$S3A_ENDPOINT \
  -e S3A_ACCESS_KEY=$S3A_ACCESS_KEY \
  -e S3A_SECRET_KEY=$S3A_SECRET_KEY \
  -e S3A_BUCKET=$S3A_BUCKET \
  -v $(pwd)/assets:/app \
  $IMAGE_NAME /bin/bash -c "
    set -eua
    # Install necessary dependencies
    pip install --no-cache-dir --no-warn-script-location --disable-pip-version-check --quiet nipyapi && \

    # Run the Python script to set up the database connections with the optional --force-delete flag
    python3 /app/import_flow.py
    python3 /app/update_variables.py
  "
