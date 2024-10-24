# vast-docker-compose-examples
Example integrations with Vast Data

```yaml
version: "3"

services:
  setup:
    image: alpine:latest
    volumes:
      - ./:/mnt/setup
    command: >
      ash -c "mkdir -p /mnt/setup/.local/solr/data &&
               cp -R /mnt/setup/sites/all/modules/search_api_solr/solr-conf/3.x /mnt/setup/.local/solr/conf"
  solr:
    image: geerlingguy/solr:3.6.2
    depends_on:
      - setup
    ports:
      - "8900:8983"
    restart: always
    volumes:
      - ./.local/solr:/opt/solr/example/solr:cached
    command: >
      bash -c "cd /opt/solr/example &&
               java -jar start.jar"
```
