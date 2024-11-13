#!/usr/bin/env bash

# Change to the script's directory
cd "$(dirname "$0")"

source ../.env-local

docker exec -i trino trino --server https://${DOCKER_HOST_OR_IP}:8443 --insecure <<EOF
-- TRINO ICEBERG CONNECTION
CREATE SCHEMA IF NOT EXISTS iceberg.social_media
WITH (location = '${S3A_ICEBERG_URI}');

CREATE TABLE IF NOT EXISTS iceberg.social_media.twitter_data (
    created_at VARCHAR,
    id BIGINT,
    id_str VARCHAR,
    text VARCHAR
);

-- Show table structure
SHOW CREATE TABLE iceberg.social_media.twitter_data;

-- Insert data into the table
INSERT INTO iceberg.social_media.twitter_data (created_at, id, id_str, text)
VALUES('1', 1, '1', 'Test tweet');

-- Select data from the table
SELECT * FROM iceberg.social_media.twitter_data;

DELETE FROM iceberg.social_media.twitter_data
WHERE text = 'Test tweet';
EOF

