#!/usr/bin/env  bash

s3cmd --access_key=${S3A_ACCESS_KEY} \
    --secret_key=${S3A_SECRET_KEY} \
    --host=$(echo $S3A_ENDPOINT | sed -s 's@http://@@' | sed -s 's@:.*@@g') \
    --host-bucket=${S3A_BUCKET} \
    --no-check-certificate --dump-config 2>&1 > ${HOME}/.s3cfg