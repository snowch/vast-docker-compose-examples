#!/usr/bin/env bash

read -p "This will delete all data. Continue [y|N]? " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Aborted."
  exit 1
fi

for dir in $(ls -d */ | grep -v "^demos/" | grep -v "^scripts/"); do
  (cd $dir && docker compose down -v)
done
