# Docker Compose examples for VAST Data.

This project aims to give you a quickstart way to try example integrations with VAST Data. The goal is to support functional testing of key technologies automated by docker compose. Most of the docker instance are single instance only and are therefore unlikely to be useful for performance testing.

> [!CAUTION]
> - Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases. 
> - Some of the images do NOT yet persist data when shutdown.  Ensure you regularly save any data that you need to keep.
> - These demos have NOT been secured, do not use them for sensitive data and do NOT host them on publicly accessible hosts.

# Prerequisites

- Docker Compose
- Mac OS or Linux Host

> [!NOTE]  
> - This project has been tested on Mac OS (Silicon) and Linux (AMD64)
> - [Colima](https://github.com/abiosoft/colima) is used on Mac OS to provide docker compose. `docker compose` can be invoked with `docker-compose`.

# End-to-end demo setup

- The [demos](./demos) folder contains end-to-end demos.

# Individual integrations setup

You don't have to use the end-to-end demos.  

Alternatively, you can use the components individually, e.g. for example "I would like to just demonstrate how to connect Trino to VastDB.

- Clone this repo.
- Copy `.env-example` to `.env-local` and update to reflect your environment
- See the README of each integration sub-project for usage instructions:
  - [hive3x](./hive3x)
  - [jupyter-pyspark](./jupyter-pyspark)
  - [kafka](./kafka)
  - [nifi](./nifi)
  - [superset](./superset)
  - [trino](./trino)
- Most sub-projects follow the pattern:
 
  ```bash
  cd trino # or other sub-project
  docker compose up -d
  ```

> [!TIP]
> Your environment may use `docker-compose` instead of `docker compose`.
