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
docker exec -it hive4-hiveserver2 beeline -u 'jdbc:hive2://localhost:10000/'
```

Let's test S3a configuration works by trying to create a HIVE SCHEMA.

```sql
-- CHANGE the s3a URI to reflect your environment
CREATE SCHEMA csnow 
LOCATION 's3a://datastore/csnow_hive_location' 
MANAGEDLOCATION 's3a://datastore/csnow_hive_managed_location';
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

```sql
CREATE TABLE twitter_data (
    id BIGINT,
    id_str STRING,
    text STRING
)
PARTITIONED BY (ts string) STORED BY ICEBERG;
```

```sql
DESCRIBE FORMATTED twitter_data
```

```
+------------------------------------+----------------------------------------------------+----------------------------------------------------+
|              col_name              |                     data_type                      |                      comment                       |
+------------------------------------+----------------------------------------------------+----------------------------------------------------+
...
| Location:                          | s3a://datastore/csnow_hive_location/twitter_data   | NULL                                               |
| Table Type:                        | EXTERNAL_TABLE                                     | NULL                                               |
| Table Parameters:                  | NULL                                               | NULL                                               |
|                                    | EXTERNAL                                           | TRUE                                               |
|                                    | TRANSLATED_TO_EXTERNAL                             | TRUE                                               |
...
|                                    | metadata_location                                  | s3a://datastore/csnow_hive_location/twitter_data/metadata/00000-ca548db6-6846-4dc3-aae2-8b55cad1f8c6.metadata.json |
...
|                                    | storage_handler                                    | org.apache.iceberg.mr.hive.HiveIcebergStorageHandler |
+------------------------------------+----------------------------------------------------+----------------------------------------------------+
```

Note: 
  - The table type is `EXTERNAL_TABLE` even though we didn't specify this.
  - The parameter `TRANSLATED_TO_EXTERNAL=TRUE` - what does this mean?


#### Iceberg external tables

```sql
CREATE EXTERNAL TABLE twitter_data_external (
    id BIGINT,
    id_str STRING,
    text STRING
)
PARTITIONED BY (ts string) STORED BY ICEBERG;
```

### Web UI

- Access the web ui at http://your_host_name_or_ip:10002

## Changing the ports

- You can change the ports exposed by docker in the `.env` file in this project folder.
