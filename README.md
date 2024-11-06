# Docker Compose examples for VAST Data.

This project aims to give you a quickstart way to try example integrations with VAST Data. The goal is to support functional testing of key technologies automated by docker compose. Most of the docker instance are single instance only and are therefore unlikely to be useful for performance testing.

> [!CAUTION]
> - Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases. 
> - Some of the images do NOT yet persist data when shutdown.  Ensure you regularly save any data that you need to keep.

# Prerequisites

- Docker Compose
- Mac OS or Linux Host

> [!NOTE]  
> This project has only been tested on Mac OS (Silicon) and Linux (AMD64)

# Setup

- Copy `.env-example` to `.env-local` and update to reflect your environment
- See the readme of each integration sub-project for usage instructions:
  - [hive3x](./hive3x)
  - [jupyter-pyspark](./jupyter-pyspark)
  - [kafka](./kafka)
  - [nifi](./nifi)
  - [superset](./superset)
  - [trino](./trino)
- Most sub-projects follow the pattern:
 
  ```bash
  cd trino # or other sub-project
  docker compose up -d && docker compose logs -f
  ```
- The [demos](./demos) folder contains demos using these integrations.
