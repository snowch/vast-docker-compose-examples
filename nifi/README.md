# Vast NiFi Quickstart

> [!CAUTION]
> - Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases.
> - Currently this image loses state when it is restarted.  Manually save any work that you need to keep.

## Overview

Docker compose quickstart environment to try Apache NiFi with Vast S3 and Vast Database.

## Instructions

Set `DOCKER_HOST_OR_IP` in `../.env-local` to the hostname or ip address where you are running NiFi.
This is the name you will enter in your browser.

> [!TIP]
> - If you will access NiFi by the URL https://my_nifi_host:some_port then `DOCKER_HOST_OR_IP=my_nifi_host`
> - If you don't set this correctly, NiFi will not work - you will received a TLS SNI Error.

Finally, run docker compose up to start up NiFi.

```bash
docker compose up
```

## Using

Wait a few minutes, then:

- Open the URL: https://DOCKER_HOST_OR_IP:18443
  - username: admin
  - password: 123456123456
 
> [!TIP]
> - NiFi should be accessible when the logs (`docker compose logs`) output org.apache.nifi.web.server.JettyServer Started Server on https://abcdefghi:18443/nifi

> [!IMPORTANT]
> - If you receive a SNI error when accessing NiFi from your browser, verify the DOCKER_HOST_OR_IP variable is set to your NiFi hostname or ip address.
