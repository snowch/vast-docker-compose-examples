# Basic Kafka

> [!CAUTION]
> - Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases.
> - Currently this image loses state when it is restarted.  Manually save any work that you need to keep.

## Overview

Docker compose quickstart environment to run Apache Kafka for development purposes.

## Instructions

```bash
# Change to the IP address of your DOCKER HOST, but not to localhost or 127.0.0.1
export DOCKER_HOST_IP=192.168.0.10
```

```bash
docker compose up
```

## Testing

```bash
docker run --tty \
    confluentinc/cp-kafkacat \
    kafkacat -b ${DOCKER_HOST_IP}:9093 -C -K: \
            -f '\nKey (%K bytes): %k\t\nValue (%S bytes): %s\n\Partition: %p\tOffset: %o\n--\n' \
            -t YOUR_TOPIC
```
