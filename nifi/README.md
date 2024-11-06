# Vast NiFi Quickstart

> [!CAUTION]
> - Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases.
> - Currently this image loses state when it is restarted.  Manually save any work that you need to keep.

## Overview

Docker compose quickstart environment to try Apache NiFi with Vast S3 and Vast Database.

## Instructions

### Running

Set `DOCKER_HOST_OR_IP` in `../.env-local` to the hostname or ip address where you are running NiFi.
This is the name you will enter in your browser.

> [!TIP]
> - If you will access NiFi by the URL https://my_nifi_host:some_port then `DOCKER_HOST_OR_IP=my_nifi_host`
> - If you don't set this correctly, NiFi will not work - you will received a TLS SNI Error.

Finally, run docker compose up to start up NiFi.

```bash
docker compose up -d && docker compose logs -f
```

## Stopping

- `docker compose stop` to stop the docker instances and maintain state when next running `compose up`
- `docker compose down -v` to stop the docker instances and remove any state and volumes

> [!CAUTION]
> - You may want to backup your data before running `docker compose down -v`.  
> - You can backup with a command *like* this:
> ```
> docker compose stop
> volumes=("database_repository" "nar_extensions" "state" "flowfile_repository" "content_repository" "provenance_repository")
> 
> timestamp=$(date +%Y-%m-%d_%H-%M-%S)
> for volume in "${volumes[@]}"; do
>   # Create a temporary container to access the volume
>   docker run --rm --volumes-from nifi -v $(pwd)/backup:/backup ubuntu tar -czvf /backup/${volume}_$timestamp.tar.gz /opt/nifi/nifi-current/$volume
> done
> ```
> - You are responsible for verifying your backup and restore process works.


## Using

Wait a few minutes, then open the URL: https://DOCKER_HOST_OR_IP:18443
  - username: admin
  - password: 123456123456
 
> [!TIP]
> - NiFi should be accessible when the logs (`docker compose logs`) output **org.apache.nifi.web.server.JettyServer Started Server on https://abcdefghi:18443/nifi**

> [!IMPORTANT]
> - If you receive a SNI error when accessing NiFi from your browser, verify the DOCKER_HOST_OR_IP variable is set to your NiFi hostname or ip address.
