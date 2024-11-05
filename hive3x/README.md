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

- `compose stop` to stop the docker instances and maintain state when next running `compose up`
- `comopse down -v` to stop the docker instances and remove any state and volumes

## Using

### Hive Beeline

You can run Hive Commands by connecting to the Hive beeline CLI:

```bash
docker exec -it hive3-hiveserver2 beeline -u 'jdbc:hive2://localhost:10000/'
```

> [!TIP]
> If beeline is unable to connect:
>  - You may need to wait a minutes or two for the environment to start.
>  - You should be able to connect when the hiveserver2 logs (`docker compose logs -f hiveserver2`) have this output: `hive3-hiveserver2  | Hive Session ID = xxxxxxxx`

### Hive Beeline SQL Commands

These example SQL commands can be run from the Hive beeline CLI.  Mofify to reflect your environment:

```sql
SET iceberg.catalog.vast_iceberg.type=hive;
SET iceberg.catalog.vast_iceberg.uri=thrift://localhost:9083;
SET iceberg.catalog.vast_iceberg.clients=10;

-- NOTE: The following doesn't seem to be needed
-- SET iceberg.catalog.vast_iceberg.warehouse=s3://csnow-bucket/iceberg;

CREATE DATABASE vast_iceberg
LOCATION 's3a://csnow-bucket/iceberg';

CREATE EXTERNAL TABLE vast_iceberg.x (i int)
STORED BY 'org.apache.iceberg.mr.hive.HiveIcebergStorageHandler';

DESCRIBE EXTENDED vast_iceberg.x;
```


### Trino SQL

These SQL commands can be run from the Trino [quickstart](../trino). Mofify to reflect your environment:

```sql
-- TRINO ICEBERG CONNECTION

CREATE SCHEMA iceberg.social_media
WITH (location = 's3a://csnow-bucket/iceberg/');

CREATE TABLE iceberg.social_media.twitter_data (
    created_at VARCHAR,
    id INT,
    id_str VARCHAR,
    text VARCHAR
);
-- STORED BY ICEBERG;

show create table iceberg.social_media.twitter_data;

INSERT INTO iceberg.social_media.twitter_data
(created_at, id, id_str, text)
VALUES('1', 1, '1', 'Yay!');

SELECT * FROM iceberg.social_media.twitter_data;
```

### Web UI

- Access the web ui at http://DOCKER_HOST_OR_IP:10002

## Changing the ports

- You can change the ports exposed by docker in the `.env` file in this project folder.
