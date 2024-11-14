#!/usr/bin/env bash

set -x

curl --fail -k https://${NIFI_WEB_PROXY_HOST}:8443
