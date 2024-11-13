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
./superset/setup_db_connections.sh
```

## View Endpoints

Run the following from the repo root folder:

```bash
./scripts/endpoints_all.sh
```

## Stop containers

> [!CAUTION]
> Manually backup any data that you need to keep in the event the containers do not restart.

Run the following from the repo root folder:

```bash
./scripts/stop_all.sh
```

> [!TIP]
> Start the environment again with:
> ```bash
> ./scripts/start_all.sh
> ```


## Teardown the environment

> [!CAUTION]
> All data will be deleted. Manually backup any data that you need to keep.

Run the following from the repo root folder:

```bash
./scripts/destroy_all.sh
```


