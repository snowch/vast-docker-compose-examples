# VastDB Hive Quickstart

**Caution**: Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases. 

## Instructions

```
wget -c -P volumes/warehouse/ https://repo1.maven.org/maven2/org/postgresql/postgresql/42.5.6/postgresql-42.5.6.jar
export POSTGRES_LOCAL_PATH=volumes/warehouse/postgresql-42.5.1.jar 
```

```bash
docker compose up
```

## Overview

Accessing Beeline:

```bash
docker exec -it hiveserver2 beeline -u 'jdbc:hive2://localhost:10000/'
```