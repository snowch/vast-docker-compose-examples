# VastDB Trino Quickstart

**Caution**: Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases. 

## Overview

Docker compose quickstart environment to try Trino with Vast Database.

## Instructions

- Change `vast.properties` to match your environment.
- Change `docker-compose.yml` to use the correct container image:
 - Vast 4.7 - use `vastdataorg/trino-vast:375`
 - Vast 5.0 - use `vastdataorg/trino-vast:420`
 - Vast 5.1 - use `vastdataorg/trino-vast:429``
- Run `docker-compose up`

## Test with the Trino client

Start the client from within the trino container:

```bash
docker exec -it trino trino --server https://192.168.0.10:8443 --insecure
```

Note:
- replace `192.168.0.10` with the hostname or ip of your docker compose host
- replace `8443` if you have changed the port exposed in docker-compose.yml

Now you can execute queries against the server – you must start with the use command to set the context:

```sql
use vast."vast-db-bucket|vast_db_schema";

show columns from vast_db_table;
select * from vast_db_table limit 1;
```




