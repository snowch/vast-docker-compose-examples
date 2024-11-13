# Setup Instructions

> [!NOTE]
> The approximate setup time for this demo is 30 mins.

## Clone repo and configure

- Clone this git repository.
- Copy `.env-example` to `.env-local` in the repo root folder and update it to reflect your environment

## Start the containers

Run the following scripts from the repo root folder:

```bash
./scripts/start_all.sh
./trino/setup_iceberg.sh
```

## Configure Superset

Open Superset URL:

```bash
if [ -f .env-local ]; then
  source .env-local
elif [ -f ../.env-local ]; then
  source ../.env-local
fi

echo "Superset URL: $DOCKER_HOST_OR_IP:8088"
```

Navigate to:

- Settings -> Database Connections
  - +Database -> Trino
    - Display Name: `Trino Vast DB`
    - SQLAlchemy URI: `trino://admin@DOCKER_HOST_OR_IP:8443/vast?verify=false`
      - replace DOCKER_HOST_OR_IP with your host or ip as set in `..\.env-local`
    - Advanced -> Other -> Engine Parameters: `{"connect_args":{"http_scheme":"https"}}`
  - +Database -> Trino
    - Display Name: `Trino Vast Iceberg`
    - SQLAlchemy URI: `trino://admin@DOCKER_HOST_OR_IP:8443/iceberg?verify=false`
      - replace DOCKER_HOST_OR_IP with your host or ip as set in `..\.env-local`
    - Advanced -> Other -> Engine Parameters: `{"connect_args":{"http_scheme":"https"}}`
   
Verify in SQL Lab that you are able to naviate the Iceberg and Vast DB databases.

## View Endpoints

Run the following from the repo root folder:

```bash
./scripts/endpoints_all.sh
```

## Stop containers

Run the following from the repo root folder:

```bash
./scripts/stop_all.sh
```

> [!CAUTION]
> Manually backup any data you need persisted.

## Teardown the environment

Run the following from the repo root folder:

```bash
./scripts/destroy_all.sh
```

> [!CAUTION]
> Manually backup any data you need persisted.
