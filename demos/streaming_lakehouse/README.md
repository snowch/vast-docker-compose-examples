# Streaming Lakehouse

The primary purpose of this example is to demonstrate how streaming data into the Vast Database using NiFi.  This is highlighted in the streaming flow, below.  

> [!TIP]
> See this [blog](https://www.vastdata.com/blog/the-data-lake-dilemma) for more information on issues with streaming into data lakehouse technologies like Iceberg, Delta and Hudi.

## Streaming Flow

![Streaming Flow](./assets/StreamingFlow.png)

## Bulk Import

Bulk Import uses a NiFi ListS3 processor to monitor a S3 folder for new parquet files.  It then calls a Vast DB processor, ImportVastDB to bulk load the files into a Database table.

You can find out more bulk importing with NiFi [here](https://vast-data.github.io/data-platform-field-docs/vast_database/nifi/bulk_import.html).

![Bulk Import](./assets/BulkImport.png)

## Prerequisites

- Docker Compose
- Host with:
  - approx. 24GB Memory
  - TBC cores
- Vast S3 Bucket
- Vast Database

## Getting Started

- Clone the parent project
- Copy `.env-example` to `.env-local` and update to reflect your environment
- Run the following projects:
  - [nifi](../../nifi)
  - [kafka](../../kafka)
  - [superset](../../superset)
  - [trino](../../trino)
  - [hive3x](../../hive3x)
  - [jupyter-pyspark](../../jupyter-pyspark)


