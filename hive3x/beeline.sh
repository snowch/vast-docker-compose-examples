#!/usr/bin/env bash

docker exec -it hive3-hiveserver2 beeline -u 'jdbc:hive2://localhost:10000/'
