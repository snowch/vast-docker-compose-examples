#!/usr/bin/env bash

for dir in $(ls -d */ | grep -v "^demos/" | grep -v "^scripts/"); do
  (cd $dir && docker compose up -d && docker compose up --wait)
done

./trino/setup_iceberg.sh
./superset/setup_db_connections.sh
