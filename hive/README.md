# VastDB Hive Quickstart

**Caution**: Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases. 

## Instructions

```
wget -c -O jars/hadoop-aws.jar https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.6/hadoop-aws-3.3.6.jar
wget -c -O jars/aws-java-sdk-bundle.jar https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.777/aws-java-sdk-bundle-1.12.777.jar
wget -c -O jars/postgresql.jar https://repo1.maven.org/maven2/org/postgresql/postgresql/42.5.6/postgresql-42.5.6.jar
```

```bash
docker compose up
```

## Overview

Accessing with Beeline:

```bash
docker exec -it hiveserver2 beeline -u 'jdbc:hive2://localhost:10000/'
```

Accessing the web interface:

- http://your_docker_host:10002/

```sql
CREATE EXTERNAL TABLE NAME_TEST_S3(name string, age int) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TextFile LOCATION 's3a://datastore/mytable';
```