# Vast Hive Quickstart


> [!CAUTION]
> - Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases.
> - Currently this image loses state when it is restarted.  Manually save any work that you need to keep.


## Prerequisites

- Vast S3 Credentials
- Vast S3 Endpoint

## Instructions

- Ensure `../.env-local` is created and populated with your environment.  See `../.env-example` for an example.
- Start the hive environment:

```bash
docker compose up -d && docker compose logs -f
```

## Stopping

- `docker compose stop` to stop the docker instances and maintain state when next running `compose up`
- `docker compose down -v` to stop the docker instances and remove any state and volumes

> [!CAUTION]
> You may want to backup your data before running `docker compose down -v`.  You can backup with this command:
> `docker exec -i hive3-postgres /usr/bin/pg_dump  -U hive metastore_db >  postgres-backup.sql`

## Using

### Hive Beeline

You can run Hive Commands by connecting to the Hive beeline CLI:

```bash
docker exec -it hive3-hiveserver2 beeline -u 'jdbc:hive2://localhost:10000/'
```

### Hive Beeline SQL Commands

These example SQL commands can be run from the Hive beeline CLI.

```sql
SET iceberg.catalog.vast_iceberg.type=hive;
SET iceberg.catalog.vast_iceberg.uri=thrift://localhost:9083;
SET iceberg.catalog.vast_iceberg.clients=10;

-- Mofify the S3 URI to reflect your environment
CREATE DATABASE vast_iceberg
LOCATION 's3a://csnow-bucket/iceberg';

CREATE EXTERNAL TABLE vast_iceberg.x (i int)
STORED BY 'org.apache.iceberg.mr.hive.HiveIcebergStorageHandler';

DESCRIBE EXTENDED vast_iceberg.x;
```

### Web UI

- Access the web ui at http://DOCKER_HOST_OR_IP:10002

## Changing the ports

- You can change the ports exposed by docker in the `.env` file in this project folder.
