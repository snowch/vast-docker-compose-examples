# Spark Iceberg Quickstart

**Caution**: Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases. 

## Prerequisites

- Vast S3 Credentials
- Vast S3 Endpoint

## Instructions

Copy `.env` file to `.env-local` and add your details:

```bash
cp .env .env-local
```

Start the environment:

```bash
docker compose up -d && docker compose logs -f
```

## Using

