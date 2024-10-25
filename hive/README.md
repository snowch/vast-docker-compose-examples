# Vast Hive Quickstart

**Caution**: Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases. 

## Prerequisites

- Vast S3 Credentials
- Vast S3 Endpoint

## Instructions

Modify hdfs-site.xml with your Vast S3 endpoint and credentials:

```bash
cp custom_conf/hdfs-site.xml-template custom_conf/hdfs-site.xml
```

```bash
touch .env-local
```

Start the hive environment:

```bash
docker compose up
```

## Overview

You can test by accessing the environment with beeline:

```bash
docker exec -it hiveserver2 beeline -u 'jdbc:hive2://localhost:10000/'
```

From beeline you can run SQL commands, e.g.

```sql
CREATE EXTERNAL TABLE TEST_S3 (name string, age int) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' 
STORED AS TextFile 
LOCATION 's3a://datastore/test_table';
```

- Ensure you update the s3a url to reflect your environment.

create database csnow_iceberg_demo_db;
use csnow_iceberg_demo_db;

CREATE EXTERNAL TABLE twitter_data (
    id BIGINT,
    id_str STRING,
    text STRING
)
PARTITIONED BY (ts string) STORED BY ICEBERG
LOCATION 's3a://datastore/csnow_iceberg_demo.db/twitter_data/';


select * from twitter_data;
