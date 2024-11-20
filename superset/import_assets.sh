#!/usr/bin/env bash

# Ensure the script stops if any command fails
set -e

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local

# Define container name (optional)
CONTAINER_NAME="hairyhenderson/gomplate:latest"

# Set working directory on host (optional)
HOST_WORKDIR=${PWD}

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

cd generated

# Loop through each directory in the current directory
for dir in *; do
    if [[ -d "$dir" ]]; then
        # Create a zip file with the same name as the directory
        zip -r "${dir}.zip" "$dir"
    fi
done


