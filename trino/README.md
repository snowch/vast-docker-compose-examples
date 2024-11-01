# Vast Trino Quickstart

> [!CAUTION]
> - Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases.
> - Currently this image loses state when it is restarted.  Manually save any work that you need to keep.

## Overview

Docker compose quickstart environment to try Trino with:

- Vast Database
- Hive on Vast S3
- Iceberg on Vast S3

## Instructions

- Change `.env` to use the correct container image
- Run `docker compose up`

## Hive Configuration

Hive is configured using `S3A_` settings in `../.env-local`.

## Vast DB Configuration

Vast DB is configured using `VASTDB_` settings in `../.env-local`.

## Using the Trino client

Start the client from within the trino container:

```bash
# Check if .env-local exists in the current or parent directory
if [ -f .env-local ]; then
  source .env-local
elif [ -f ../.env-local ]; then
  source ../.env-local
fi

echo "Connecting to: $DOCKER_HOST_OR_IP"
docker exec -it trino trino --server https://${DOCKER_HOST_OR_IP}:8443 --insecure
```

### Vast DB

Let's check we can access the schemas in Vast.

```sql
SHOW SCHEMAS FROM vast;
```

Then you can select a schema:

```sql
use vast."vast-db-bucket|vast_db_schema";

show columns from vast_db_table;
select * from vast_db_table limit 1;
```

### Hive

```sql
SHOW SCHEMAS FROM hive;
```

Iceberg example:

```sql
CREATE SCHEMA IF NOT EXISTS hive.iceberg WITH (location = 's3a://datastore/csnow_iceberg');

CREATE TABLE hive.iceberg.twitter_data (
    ts VARCHAR,
    id BIGINT,
    id_str VARCHAR,
    text VARCHAR
)
WITH (
    format = 'TEXTFILE',
    external_location = 's3a://datastore/csnow_iceberg/twitter_data'
);
```

### Hive + Vast DB

```sql
SELECT 
  *
FROM
  vast."vastdb|twitter_import".twitter_data vtd 
  FULL OUTER JOIN hive.iceberg.twitter_data htd 
    ON vtd.created_at = htd.ts;
```
