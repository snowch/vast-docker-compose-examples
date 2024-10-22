## Trino

- Run: `../vastdb-trino/`

## Superset

- Based on: https://superset.apache.org/docs/installation/docker-compose/

- Clone Superset: `git clone --depth=1  https://github.com/apache/superset.git`

- Edit `docker-compose-image-tag.yml`, modify:

```yml
    container_name: superset_app
   # command: ["/app/docker/docker-bootstrap.sh", "app-gunicorn"]
    command: bash -c "pip3 install trino[sqlalchemy] && /app/docker/docker-bootstrap.sh app-gunicorn"
```

- `export TAG=4.0.2`

- Add 'Trino' Database connection
  - SQLAlchemy URI: `trino://admin@192.168.0.10:8443/vast?verify=false`
    - Ensure the `IP` matches the hostname or IP address where you are running docker.  Do NOT use `localhost` or `127.0.0.1`
    - The port must match the trino exposed
  - Engine Parameters: `{"connect_args":{"http_scheme":"https"}}`
