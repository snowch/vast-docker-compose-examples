# Spark Quickstart

> [!CAUTION]
> - Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases.
> - Currently this image loses state when it is restarted.  Manually save any work that you need to keep.

## Prerequisites

- Vast S3 and Vast DB Credentials
- Vast S3 and Vast DB Endpoint

## Instructions

Ensure `../.env-local` is created and populated with your environment.  See `../.env` for an example.

Build the image (use the same command to rebuild the image if you make any changes):

```bash
docker compose build --no-cache
```

Start the spark container:

```bash
docker compose up -d && docker compose logs -f
```

## Persistence

Any changes you make in the notebook to the examples folder are saved to the examples folder locally.

## Using

When the image has started, navigate to: `http://DOCKER_HOST_OR_IP:8888`

## Details

The image is built with jars ([Dockerfile](./docker/Dockerfile)) for:

- S3A support
- Iceberg Support

The environment variables in `../.env-local` are passed to the container.