#!/usr/bin/env bash

# Validate the metastore schema; set IS_RESUME based on success or failure.
if $HIVE_HOME/bin/schematool -dbType postgres -validate \
    -url jdbc:postgresql://postgres:5432/metastore_db \
    -userName hive -passWord password; then
  export IS_RESUME=true
else
  export IS_RESUME=false
fi

echo "IS_RESUME=$IS_RESUME"

# Call the original entrypoint script with any additional arguments.
exec /entrypoint.sh "$@"