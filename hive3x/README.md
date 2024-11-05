# Vast Hive Quickstart


> [!CAUTION]
> - Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases.
> - Currently this image loses state when it is restarted.  Manually save any work that you need to keep.

> [!WARNING]
> This image is currently broken.  When starting up for the first time, you need to comment out the following:
> `      - ./pg_hba.conf:/var/lib/postgresql/data/pgdata/pg_hba.conf`
> Then start the image, stop it uncomment the above live and restart it.

## Prerequisites

- Vast S3 Credentials
- Vast S3 Endpoint

## Instructions

- Ensure `../.env-local` is created and populated with your environment.  See `../.env-example` for an example.
- Start the hive environment:

```bash
docker compose up -d && docker compose logs -f
```

## Using

### Beeline

You can test by accessing the environment with beeline:

```bash
docker exec -it hive3-hiveserver2 beeline -u 'jdbc:hive2://localhost:10000/'
```

> [!TIP]
> If beeline is unable to connect verify with logs `docker compose logs -f` to ensure you see output similar to `hive3-hiveserver2  | Hive Session ID = xxxxxxxx`.


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


#### Iceberg from Trino

From Trino:

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

- Access the web ui at http://your_host_name_or_ip:10002

## Changing the ports

- You can change the ports exposed by docker in the `.env` file in this project folder.
