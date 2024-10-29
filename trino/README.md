# VastDB Trino Quickstart

**Caution**: Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases. 

## Overview

Docker compose quickstart environment to try Trino with Vast Database.

## Instructions

 - Change `vast.properties` to match your environment.
 - Change `docker-compose.yml` to use the correct container image:
  - Vast 4.7 - use `vastdataorg/trino-vast:375`
  - Vast 5.0 - use `vastdataorg/trino-vast:420`
  - Vast 5.1 - use `vastdataorg/trino-vast:429`
- Run `docker-compose up`

### Hive Setup

**NOTE:** If you wish to access Hive S3 datasets, change `hive.properties` to match your environment.

## Test with the Trino client

Start the client from within the trino container:

```bash
export DOCKER_HOST_OR_IP=##CHANGE_ME##
docker exec -it trino trino --server https://${DOCKER_HOST_OR_IP}:8443 --insecure
```

Note:
- replace `192.168.0.10` with the hostname or ip of your docker compose host
- replace `8443` if you have changed the port exposed in docker-compose.yml

### Vast DB

Now you can execute queries against the server – you must start with the use command to set the context:

```sql
use vast."vast-db-bucket|vast_db_schema";

show columns from vast_db_table;
select * from vast_db_table limit 1;
```

### Hive

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