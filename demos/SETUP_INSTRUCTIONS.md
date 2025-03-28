# Setup Instructions

> [!NOTE]
> The approximate setup time for this demo is 30 mins.

## Clone repo and configure

- Clone this git repository, e.g. `git clone https://github.com/snowch/vast-docker-compose-examples.git`
- Change to this new folder: `cd vast-docker-compose-examples`
- Copy `.env-example` to `.env-local` in the repo root folder
- Update `.env-local` to reflect your environment

## Setup environment

```bash
 sudo apt install python3-pip
 sudo apt install python3-full
```

Change to examples folder:

```bash
cd /path/to/vast-docker-compose-examples
```

Create python venv

```bash
 python3 -m venv .pyvenv
 source .pyvenv/bin/activate
```

Add vastdb module

```bash
pip3 install vastdb
```

## Start the containers

Run the following scripts from the repo root folder:

```bash
./scripts/start_all.sh
```

## View Endpoints

Run the following from the repo root folder:

```bash
./scripts/endpoints_all.sh
```

# Stopping containers

You can stop the running containers without removing them with these instructions.

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


# Teardown Instructions

Follow these instructions to stop and removes containers, networks, volumes, and images created by the setup scripts.

> [!CAUTION]
> All data will be deleted. Manually backup any data that you need to keep.

Run the following from the repo root folder:

```bash
./scripts/destroy_all.sh
```


