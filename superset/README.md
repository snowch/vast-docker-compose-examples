# VastDB Superset Quickstart

**Caution**: Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases. 

## Overview

Docker compose quickstart environment to try Apache Superset with Vast Database.

## Dependency

- Run trino using the instructions here: [../vastdb-trino/README.md](../vastdb-trino/README.md)
- If you change the port exposed by ../vastdb-trino, update the 

## Instructions

- cd into this folder
- run `docker compose up`

- When superset is running, add a 'Trino' Database connection:
  - SQLAlchemy URI: `trino://admin@192.168.0.10:8443/vast?verify=false`
    - Ensure the `IP` matches the hostname or IP address where you are running docker.  Do NOT use `localhost` or `127.0.0.1`
    - The port must match the trino exposed (default is 8443)
  - Engine Parameters: `{"connect_args":{"http_scheme":"https"}}`
