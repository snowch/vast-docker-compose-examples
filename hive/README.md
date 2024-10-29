# Vast Hive Quickstart

**Caution**: Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases.

**Caution**: Currently this image loses state when it is restarted.  Manually save any work that you need to keep.

## Prerequisites

- Vast S3 Credentials
- Vast S3 Endpoint

## Instructions

Ensure `../.env-local` is created and populated with your environment.  See `../.env` for an example.

Start the hive environment:

```bash
docker compose up -d && docker compose logs -f
```

## Using

### Beeline

You can test by accessing the environment with beeline:

```bash
docker exec -it hiveserver2 beeline -u 'jdbc:hive2://localhost:10000/'
```

Let's test S3a configuration works by trying to create a HIVE SCHEMA.

```sql
-- CHANGE the s3a URI to reflect your environment
CREATE SCHEMA csnow MANAGEDLOCATION 's3a://datastore/csnow';
```

Verify the shema exists (note SCHEMA and DATABASE are interchangeable):

```sql
SHOW SCHEMAS;
```

I see:

```
+----------------+
| database_name  |
+----------------+
| csnow          |
| default        |
+----------------+
```

Now, 

```sql
DESCRIBE csnow;
```

Which shows:

```
+----------+----------+-----------------------------------------+-----------------------------------------+-------------+-------------+-----------------+----------------+
| db_name  | comment  |                location                 |             managedlocation             | owner_name  | owner_type  | connector_name  | remote_dbname  |
+----------+----------+-----------------------------------------+-----------------------------------------+-------------+-------------+-----------------+----------------+
| csnow    |          | file:/opt/hive/data/warehouse/csnow.db  | file:/opt/hive/data/warehouse/csnow.db  | hive        | USER        |                 |                |
+----------+----------+-----------------------------------------+-----------------------------------------+-------------+-------------+-----------------+----------------+
```

```sql
USE csnow;
```

```sql
CREATE EXTERNAL TABLE twitter_data (
    id BIGINT,
    id_str STRING,
    text STRING
)
PARTITIONED BY (ts string) STORED BY ICEBERG
LOCATION 's3a://datastore/csnow/twitter_data/';
```

- Ensure you update the s3a url to reflect your environment.

### Web UI

- Access the web ui at http://your_host_name_or_ip:10002

