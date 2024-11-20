#!/usr/bin/env bash

# Ensure the script stops if any command fails
set -e

# Change to the script's directory
script_dir="$(cd "$(dirname "$0")" && pwd)"
parent_dir="$(dirname "$script_dir")"

cd $script_dir

source ../../.env-local

# Define container name 
CONTAINER_NAME="hairyhenderson/gomplate:latest"

# Set working directory on host
HOST_WORKDIR=${parent_dir}

# Define input and output directories
INPUT_DIR="${HOST_WORKDIR}/templates"
OUTPUT_DIR="${HOST_WORKDIR}/generated"

# Run the container
docker run --rm \
  -v "${INPUT_DIR}:/workspace/input" \
  -v "${OUTPUT_DIR}:/workspace/output" \
  -e "DOCKER_HOST_OR_IP=${DOCKER_HOST_OR_IP}" \
  -e "S3A_ACCESS_KEY=${S3A_ACCESS_KEY}" \
  -e "S3A_SECRET_KEY=${S3A_SECRET_KEY}" \
  -e "S3A_ENDPOINT=${S3A_ENDPOINT}" \
  -e "S3A_SSL_ENABLED=${S3A_SSL_ENABLED}" \
  -e "S3A_TIMEOUT=${S3A_TIMEOUT}" \
  -e "S3A_BUCKET=${S3A_BUCKET}" \
  -e "S3A_ICEBERG_URI=${S3A_ICEBERG_URI}" \
  -e "VASTDB_ACCESS_KEY=${VASTDB_ACCESS_KEY}" \
  -e "VASTDB_SECRET_KEY=${VASTDB_SECRET_KEY}" \
  -e "VASTDB_ENDPOINT=${VASTDB_ENDPOINT}" \
  -e "VASTDB_TWITTER_INGEST_BUCKET=${VASTDB_TWITTER_INGEST_BUCKET}" \
  -e "VASTDB_TWITTER_INGEST_SCHEMA=${VASTDB_TWITTER_INGEST_SCHEMA}" \
  -e "VASTDB_TWITTER_INGEST_TABLE=${VASTDB_TWITTER_INGEST_TABLE}" \
  -e "VASTDB_BULK_IMPORT_BUCKET=${VASTDB_BULK_IMPORT_BUCKET}" \
  -e "VASTDB_BULK_IMPORT_SCHEMA=${VASTDB_BULK_IMPORT_SCHEMA}" \
  -e "VASTDB_BULK_IMPORT_TABLE=${VASTDB_BULK_IMPORT_TABLE}" \
  -e "VASTDB_DATA_ENDPOINTS=${VASTDB_DATA_ENDPOINTS}" \
  -w /workspace \
  ${CONTAINER_NAME} \
  --input-dir /workspace/input \
  --output-dir /workspace/output


cd $script_dir/../generated
# Loop through each directory in the current directory
for dir in *; do
    if [[ -d "$dir" ]]; then
        # Create a zip file with the same name as the directory using Docker
        docker run --rm \
          -v "$(pwd):/data" debian:stable-slim \
          sh -c "apt-get update && apt-get install -y zip && cd /data && zip -r \"${dir}.zip\" \"${dir}\""
    fi
done
cd $script_dir

IMAGE_NAME="python:3.10-slim"  # Replace with your Python image name
CONTAINER_NAME="import_superset_assets"

# Check if the --overwrite option is provided
OVERWRITE_FLAG=""
if [[ "$1" == "--overwrite" ]]; then
  OVERWRITE_FLAG="--overwrite"
fi

# Create a Docker container with the necessary setup to run the Python script
docker run --rm \
  --name $CONTAINER_NAME \
  --network host \
  -e DOCKER_HOST_OR_IP=$DOCKER_HOST_OR_IP \
  -v $script_dir/../scripts/:/scripts \
  -v $script_dir/../generated/:/generated \
  $IMAGE_NAME /bin/bash -c "
    # Install necessary dependencies
    pip install --no-cache-dir --no-warn-script-location --disable-pip-version-check --quiet superset-api-client && \

    # Run the Python script to import the assets
    python /scripts/import_assets.py $OVERWRITE_FLAG
  "

