# Basic Kafka

> [!CAUTION]
> - Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases.
> - Currently this image loses state when it is restarted.  Manually save any work that you need to keep.

## Overview

Docker compose quickstart environment to run Kafka for development purposes.

## Instructions

Ensure `../.env-local` is created and populated with your environment.  See `../.env-example` for an example.  The key variable is `DOCKER_HOST_OR_IP`.

```bash
docker compose up
```

> [!NOTE]
> The KAFKA endpoint is: `DOCKER_HOST_OR_IP:19092`

## Console

The console application can be access at:

`http://DOCKER_HOST_OR_IP:28080`
