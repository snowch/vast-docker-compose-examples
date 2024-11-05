#!/usr/bin/env bash

function __check_port() {
  local host="localhost"
  local port="$1"

  if [ -z "$port" ]; then
    echo "Usage: $0 PORT_NUMBER"
    exit 1
  fi

  exec 3<>/dev/tcp/$host/$port
  exit $?
}