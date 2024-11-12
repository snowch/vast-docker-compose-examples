#!/usr/bin/env bash

for dir in $(ls -d */ | grep -v "^demos/" | grep -v "^scripts/"); do
  (cd $dir && docker compose down)
done
