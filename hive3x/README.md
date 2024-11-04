# Vast Hive Quickstart


> [!CAUTION]
> - Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases.
> - Currently this image loses state when it is restarted.  Manually save any work that you need to keep.

## Prerequisites

- Vast S3 Credentials
- Vast S3 Endpoint

## Instructions

Ensure `../.env-local` is created and populated with your environment.  See `../.env-example` for an example.

Start the hive environment:

```bash
docker compose up -d && docker compose logs -f
```

## Using

### Beeline

You can test by accessing the environment with beeline:

```bash
docker exec -it hive3-hiveserver2 beeline -u 'jdbc:hive2://localhost:10000/'
```

Let's test S3a configuration works by trying to create a HIVE SCHEMA.

```sql
-- CHANGE the s3a URI to reflect your environment
CREATE SCHEMA csnow 
LOCATION 's3a://csnow-bucket/hive_location';
```

Verify the shema exists (note the terms SCHEMA and DATABASE are interchangeable with Hive):


```sql
DESCRIBE SCHEMA csnow;
```

Which shows:

```
+----------+----------+--------------------------------------+----------------------------------------------+-------------+-------------+-----------------+----------------+
| db_name  | comment  |               location               |               managedlocation                | owner_name  | owner_type  | connector_name  | remote_dbname  |
+----------+----------+--------------------------------------+----------------------------------------------+-------------+-------------+-----------------+----------------+
| csnow    |          | s3a://datastore/csnow_hive_location  | s3a://datastore/csnow_hive_managed_location  | hive        | USER        |                 |                |
+----------+----------+--------------------------------------+----------------------------------------------+-------------+-------------+-----------------+----------------+
```

```sql
USE csnow;
```

#### Iceberg tables

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
