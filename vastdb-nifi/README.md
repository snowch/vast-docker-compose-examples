# VastDB NiFi Quickstart

**Caution**: Since docker compose is primarily designed to run a set of containers on a single host and can't support requirements for high availability, we do not support nor recommend using our docker compose constructs to support production-type use-cases. 

## Overview

Docker compose quickstart environment to try Apache NiFi with Vast Database.

## Instructions

Run the following script to create folders for nifi to store its state and to download extension NAR files that we need.  

```bash
./setup_env.sh
```

Set NIFI_HOST to the hostname or ip address where you are running NiFi.
This is the name you will enter in your browser.

E.g. If you will access NiFi by the URL https://my_nifi_host:some_port then `NIFI_HOST=my_nifi_host`

**IMPORTANT**: If you don't set this correctly, NiFi will not work.

```bash
export NIFI_HOST=hostname_or_ipaddress
```

Finally, run docker compose up to start up NiFi.

```bash
docker compose up
```

## Using

Wait a few minutes, then:

- Open the URL: https://hostname_or_ipaddress:8443
  - username: admin
  - password: 123456123456

**Note**:

- If you receive a SNI error when accessing NiFi from your browser, verify the NIFI_HOST variable is set to your NiFi hostname or ip address.
- NiFi should be accessible when the logs output org.apache.nifi.web.server.JettyServer Started Server on https://abcdefghi:8443/nifi
