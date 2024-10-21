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

- Add 'Trino' Database connection
  - SQLAlchemy URI: `trino://admin@192.168.0.10:443/vast?verify=false`
  - Engine Parameters: `{"connect_args":{"http_scheme":"https"}}`
