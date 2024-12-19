# Demonstrating

Follow these steps to run the demo.

## Start the data generator

- Ensure your `./.env-local` file contains settings for:
  - VASTDB_ENDPOINT
  - VASTDB_ACCESS_KEY
  - VASTDB_SECRET_KEY
  - VASTDB_NETFLOW_BUCKET
  - VASTDB_NETFLOW_SCHEMA
  - VASTDB_NETFLOW_TABLE
- From your CLI, cd `./netflow-datagen/`
    - run `pip install vastdb`
    - run `./start.sh`

## Discussion points

- run `./scripts/endpoints_all.sh` and open the Superset URL
- navigate to the dashboard **Netflow Data**
- set dashboard auto refresh to 10 seconds (click **&#x22EF;** next to **EDIT DASHBOARD**, top right)

More content coming soon...
