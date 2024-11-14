#!/usr/bin/env bash

set -eau

for dir in $(ls -d */ | grep -v "^demos/" | grep -v "^scripts/"); do
  if [[ -f "$dir/endpoints.sh" ]]; then
    (cd "$dir" && ./endpoints.sh)
  fi
done

