# Setup Instructions

> [!NOTE]
> The approximate setup time for this demo is 30 mins.

## Clone repo and configure

- Clone this git repository.
- Copy `.env-example` to `.env-local` in the repo root folder and update it to reflect your environment:
  - DOCKER_HOST_OR_IP
  - S3A_ACCESS_KEY
  - S3A_SECRET_KEY
  - S3A_ENDPOINT
  - VASTDB_ACCESS_KEY
  - VASTDB_SECRET_KEY
  - VASTDB_ENDPOINT

## Hive3x 

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

-- ## Change the s3a location to a bucket on your S3A_ENDPOINT ##
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

## Install and Configure s3cmd

- Install: https://github.com/s3tools/s3cmd/blob/master/INSTALL.md
- Configure: `s3cmd --configure`

## Verify Iceberg on S3

```bash
## Change the s3a location to a bucket on your S3A_ENDPOINT ###
s3cmd ls s3://csnow-bucket/iceberg/ -r
```

Example output:

```bash
$ s3cmd ls s3://csnow-bucket/iceberg/ -r
2024-11-06 22:00         1599  s3://csnow-bucket/iceberg/twitter_data/metadata/00000-d098452f-a8ac-4b8d-bfd4-2d25fa5c17bd.metadata.json
```

## Trino

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

## Superset

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

## Kafka

Run the kafka container:

```bash
cd kafka
docker compose up -d
```

Navigate to the Redpanda console:

http://DOCKER_HOST_OR_IP:28080

## NiFi

Run the NiFi container:

```bash
cd nifi
docker compose up -d
docker compose up --wait # wait for nifi to be healthy
```

Wait a few minutes, then open the URL: https://DOCKER_HOST_OR_IP:18443

- username: admin
- password: 123456123456

After logging in to NiFi, create a new Process Group ![Process Group](./assets/drag_process_group.png)

Download the Nifi [Demo Flow Definition](./assets/NiFi_Flow.json)

Click on the icon to import the Flow Definition: 

<img src="./assets/import_flow_definition.png" width=500px style="float: left"/>

Double click on the imported Process Group Header and you will see two subflows:

 - Streaming
 - Bulk Import

Right click the Canvas and choose Controller Services.

<img src="./assets/configure_services.png" width=500px style="float: left"/>

Edit these controller services:

- S3A - AWSCredentialsProviderControllerService
  - Access Key ID: `${S3A_ACCESS_KEY}`
  - Secret Access Key : `${S3A_SECRET_KEY`
- VastDB - AWSCredentialsProviderControllerService
  - Access Key ID: `${VASTDB_ACCESS_KEY}`
  - Secret Access Key : `${VASTDB_SECRET_KEY`
 
> [!NOTE]
> These environment variables are passed to the NiFi service by docker compose and will be resolved at runtime.

Enable the services.

## More coming soon ...
