# Streaming Lakehouse

The primary purpose of this example is to demonstrate how streaming data into the Vast Database using NiFi.  This is highlighted in the streaming flow, below.  

> [!TIP]
> See this [blog](https://www.vastdata.com/blog/the-data-lake-dilemma) for more information on issues with streaming into data lakehouse technologies like Iceberg, Delta and Hudi.

## Streaming Flow

This example uses a NiFi flow generate the creation of random tweets in realtime (using a NiFi ScriptProcessor).  The Tweets are published to a Kafka topic.

A separate NiFi flow consumes from the Kafka topic and saves the tweets to the Vast DB.  Spark and Trino can be used to query from Iceberg tables that are stored on Vast S3 or from data in the Vast Database.  Queries can join data from both sources.  In addition Superset is configured to use Trino to provide a UI for data visualization and exploration.

Finally, a Spark Kafka notebook demonstrates how spark can be used to write to Kafka.

![Streaming Flow](./assets/StreamingFlow.png)

## Bulk Import

Bulk Import uses a NiFi ListS3 processor to monitor a S3 folder for new parquet files.  It then calls a Vast DB processor, ImportVastDB to bulk load the files into a Database table.

You can find out more bulk importing with NiFi [here](https://vast-data.github.io/data-platform-field-docs/vast_database/nifi/bulk_import.html).

![Bulk Import](./assets/BulkImport.png)

## Prerequisites

- Docker Compose
- Host with:
  - approx. 24GB Memory
  - approx. 8 cores
- Vast S3 Bucket
- Vast Database

## Getting Started

- Clone this git repository.
- Copy `.env-example` to `.env-local` in the repo root folder and update it to reflect your environment
- Run the following projects:
  - [hive3x](../../hive3x)
  - [kafka](../../kafka)
  - [nifi](../../nifi)
    - Upload the [NiFi Flow File](./assets/NiFi_Flow.json) 
  - [jupyter-pyspark](../../jupyter-pyspark)
  - [trino](../../trino)
  - [superset](../../superset)
  
## Detailed Setup Instructions

### Clone repo and configure

- Clone this git repository.
- Copy `.env-example` to `.env-local` in the repo root folder and update it to reflect your environment:
  - DOCKER_HOST_OR_IP
  - S3A_ACCESS_KEY
  - S3A_SECRET_KEY
  - S3A_ENDPOINT
  - VASTDB_ACCESS_KEY
  - VASTDB_SECRET_KEY
  - VASTDB_ENDPOINT

### Hive3x 

Start metastore and hiveserver2:

```bash
cd hive3x
docker compose up -d
```

Run beeline:

```bash
docker exec -it hive3-hiveserver2 beeline -u 'jdbc:hive2://localhost:10000/'
```

Create your hive iceberg database:

```sql
SET iceberg.catalog.vast_iceberg.type=hive;
SET iceberg.catalog.vast_iceberg.uri=thrift://localhost:9083;
SET iceberg.catalog.vast_iceberg.clients=10;

### Change the s3a location to a bucket on your S3A_ENDPOINT ###
CREATE DATABASE vast_iceberg
LOCATION 's3a://csnow-bucket/iceberg';

CREATE TABLE vast_iceberg.twitter_data (
  created_at BIGINT,
  id BIGINT,
  id_str STRING,
  text STRING
)
STORED BY 'org.apache.iceberg.mr.hive.HiveIcebergStorageHandler';

DESCRIBE EXTENDED vast_iceberg.twitter_data;
```

### Install and Configure s3cmd

- Install: https://github.com/s3tools/s3cmd/blob/master/INSTALL.md
- Configure: `s3cmd --configure`

### Verify Iceberg on S3

```bash
### Change the s3a location to a bucket on your S3A_ENDPOINT ###
s3cmd ls s3://csnow-bucket/iceberg/ -r
```

Example output:

```bash
$ s3cmd ls s3://csnow-bucket/iceberg/ -r
2024-11-06 22:00         1599  s3://csnow-bucket/iceberg/twitter_data/metadata/00000-d098452f-a8ac-4b8d-bfd4-2d25fa5c17bd.metadata.json
```

### Trino

Start trino:

```bash
cd trino
docker compose up -d
```

Connect to trino:

```bash
if [ -f .env-local ]; then
  source .env-local
elif [ -f ../.env-local ]; then
  source ../.env-local
fi

echo "Connecting to: $DOCKER_HOST_OR_IP"
docker exec -it trino trino --server https://${DOCKER_HOST_OR_IP}:8443 --insecure
```

Verify iceberg table exists:

```bash
trino> show tables in iceberg.vast_iceberg;
```

This should output:

```bash
    Table
--------------
 twitter_data
(1 row)
```

### Superset

```bash
cd superset
docker compose up -d
```

Open Superset URL:

```bash
if [ -f .env-local ]; then
  source .env-local
elif [ -f ../.env-local ]; then
  source ../.env-local
fi

echo "Superset URL: $DOCKER_HOST_OR_IP:8088"
```

Navigate to:

- Settings -> Database Connections
  - +Database -> Trino
    - Display Name: `Trino Vast DB`
    - SQLAlchemy URI: `trino://admin@DOCKER_HOST_OR_IP:8443/vast?verify=false`
      - replace DOCKER_HOST_OR_IP with your host or ip
    - Advanced -> Other -> Engine Parameters: `{"connect_args":{"http_scheme":"https"}}`
  - +Database -> Trino
    - Display Name: `Trino Vast Iceberg`
    - SQLAlchemy URI: `trino://admin@DOCKER_HOST_OR_IP:8443/iceberg?verify=false`
      - replace DOCKER_HOST_OR_IP with your host or ip
    - Advanced -> Other -> Engine Parameters: `{"connect_args":{"http_scheme":"https"}}`
   
Verify in SQL Lab that you are able to naviate the Iceberg and Vast DB databases.

### Kafka

Run the kafka container:

```bash
cd kafka
docker compose up -d
```

Navigate to the Redpanda console:

http://DOCKER_HOST_OR_IP:28080

### NiFi

Run the NiFi container:

```bash
cd nifi
docker compose up -d
docker compose up --wait # wait for nifi to be healthy
```

Wait a few minutes, then open the URL: https://DOCKER_HOST_OR_IP:18443

- username: admin
- password: 123456123456


### More coming soon ...


