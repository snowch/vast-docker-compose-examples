#!/bin/bash

set -x

export AWS_ACCESS_KEY_ID=${S3A_ACCESS_KEY}
export AWS_SECRET_ACCESS_KEY=${S3A_SECRET_KEY}
export AWS_ENDPOINT_URL=${S3A_ENDPOINT}

mkdir -p ${HOME}/s3-read-only

# read-only until more info on
# https://github.com/awslabs/mountpoint-s3/issues/1133

mount-s3 \
    --region VAST \
    --endpoint-url $AWS_ENDPOINT_URL \
    --read-only \
    --uid $(id -u jovyan) \
    --gid $(id -g jovyan) \
    --file-mode 0664 \
    --dir-mode 0775 \
    "$S3A_BUCKET" ${HOME}/s3-read-only
