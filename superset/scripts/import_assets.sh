#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Set script and parent directories
script_dir="$(cd "$(dirname "$0")" && pwd)"
parent_dir="$(dirname "$script_dir")"

cd "$script_dir"

# Load environment variables
source "$parent_dir/../.env-local"

# Container configuration
CONTAINER_NAME="hairyhenderson/gomplate:latest"
HOST_WORKDIR="$parent_dir"
INPUT_DIR="$HOST_WORKDIR/templates"
OUTPUT_DIR="$HOST_WORKDIR/generated"

# Clean up previous assets
cleanup_assets() {
  docker run --rm \
    -v "$OUTPUT_DIR:/workspace/output" \
    --name superset_generated_cleanup \
    python:3.10-slim \
    sh -c "find /workspace/output -mindepth 1 ! -name '.gitignore' -exec rm -rf {} +"
}

# Generate assets using gomplate
generate_assets() {
  docker run --rm \
    -v "$INPUT_DIR:/workspace/input" \
    -v "$OUTPUT_DIR:/workspace/output" \
    -e "DOCKER_HOST_OR_IP=$DOCKER_HOST_OR_IP" \
    -e "S3A_ACCESS_KEY=$S3A_ACCESS_KEY" \
    -e "S3A_SECRET_KEY=$S3A_SECRET_KEY" \
    -e "S3A_ENDPOINT=$S3A_ENDPOINT" \
    -e "S3A_SSL_ENABLED=$S3A_SSL_ENABLED" \
    -e "S3A_TIMEOUT=$S3A_TIMEOUT" \
    -e "S3A_BUCKET=$S3A_BUCKET" \
    -e "S3A_ICEBERG_URI=$S3A_ICEBERG_URI" \
    -e "VASTDB_ACCESS_KEY=$VASTDB_ACCESS_KEY" \
    -e "VASTDB_SECRET_KEY=$VASTDB_SECRET_KEY" \
    -e "VASTDB_ENDPOINT=$VASTDB_ENDPOINT" \
    -e "VASTDB_TWITTER_INGEST_BUCKET=$VASTDB_TWITTER_INGEST_BUCKET" \
    -e "VASTDB_TWITTER_INGEST_SCHEMA=$VASTDB_TWITTER_INGEST_SCHEMA" \
    -e "VASTDB_TWITTER_INGEST_TABLE=$VASTDB_TWITTER_INGEST_TABLE" \
    -e "VASTDB_BULK_IMPORT_BUCKET=$VASTDB_BULK_IMPORT_BUCKET" \
    -e "VASTDB_BULK_IMPORT_SCHEMA=$VASTDB_BULK_IMPORT_SCHEMA" \
    -e "VASTDB_BULK_IMPORT_TABLE=$VASTDB_BULK_IMPORT_TABLE" \
    -e "VASTDB_DATA_ENDPOINTS=$VASTDB_DATA_ENDPOINTS" \
    -w /workspace \
    "$CONTAINER_NAME" \
    --input-dir /workspace/input \
    --output-dir /workspace/output
}

# Compress directories into zip files
compress_directories() {
  cd "$script_dir/../generated"

  docker run --rm \
    -v "$(pwd):/data" debian:stable-slim \
    sh -c "\
      apt-get update && \
      apt-get install -y zip && \
      cd /data && \
      for dir in *; do \
        if [ -d \"\$dir\" ]; then \
          zip -r \"\$dir.zip\" \"\$dir\"; \
        fi; \
      done"
  
  cd "$script_dir"
}

# Import assets into Superset
import_assets() {
  IMAGE_NAME="python:3.10-slim"
  CONTAINER_NAME="import_superset_assets"

  OVERWRITE_FLAG=""
  if [[ "$1" == "--overwrite" ]]; then
    OVERWRITE_FLAG="--overwrite"
  fi

  docker run --rm \
    --name "$CONTAINER_NAME" \
    --network host \
    -e DOCKER_HOST_OR_IP="$DOCKER_HOST_OR_IP" \
    -v "$script_dir/../scripts/:/scripts" \
    -v "$script_dir/../generated/:/generated" \
    "$IMAGE_NAME" /bin/bash -c "\
      pip install --no-cache-dir --no-warn-script-location --disable-pip-version-check --quiet superset-api-client && \
      python /scripts/import_assets.py $OVERWRITE_FLAG"
}

# Execute tasks
cleanup_assets
generate_assets
compress_directories
import_assets "$1"
