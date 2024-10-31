# VAST Data - Docker Compose examples

Example integrations with Vast Data

> [!CAUTION]
> - Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases. 
> - Some of the images do NOT yet persist data when shutdown.  Ensure you regularly save any data that you need to keep.

# Setup

- Copy `.env-example` to `.env-local` and update to reflect your environment
- See the readme of each sub-project for usage instructions.  For example:
 
  ```bash
  cd trino
  docker compose up -d && docker compose logs -f
  ```
