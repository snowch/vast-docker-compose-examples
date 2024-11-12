#!/usr/bin/env bash

for dir in $(ls -d */ | grep -v "^demos/"); do
  (cd $dir && docker compose up -d)
done
