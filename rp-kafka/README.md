# Basic Kafka

> [!CAUTION]
> - Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases.
> - Currently this image loses state when it is restarted.  Manually save any work that you need to keep.

## Overview

Docker compose quickstart environment to run Kafka for development purposes.

## Instructions

```bash
docker compose up
```

## Console

http://DOCKER_HOST_OR_IP:28080
