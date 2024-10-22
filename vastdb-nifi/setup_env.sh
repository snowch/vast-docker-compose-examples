#!/usr/bin/env bash

set -x
source .env

mkdir -p nifi_extensions nifi_state nifi_db nifi_flowfile nifi_profile nifi_content nifi_provenance
chmod -R 755 nifi_extensions nifi_state nifi_db nifi_flowfile nifi_profile nifi_content nifi_provenance

LATEST_VAST_NAR_RELEASE=$(python3 -c "import requests; print(requests.get('https://api.github.com/repos/vast-data/vastdb_nifi/releases/latest').json()['tag_name'].lstrip('v'))")

wget -c -P ./nifi_extensions https://github.com/vast-data/vastdb_nifi/releases/download/v${LATEST_VAST_NAR_RELEASE}/vastdb_nifi-${LATEST_VAST_NAR_RELEASE}-linux-x86_64-py39.nar && \
wget -c -P ./nifi_extensions https://repo1.maven.org/maven2/org/apache/nifi/nifi-parquet-nar/${NIFI_VERSION}/nifi-parquet-nar-${NIFI_VERSION}.nar && \
wget -c -P ./nifi_extensions https://repo1.maven.org/maven2/org/apache/nifi/nifi-hadoop-libraries-nar/${NIFI_VERSION}/nifi-hadoop-libraries-nar-${NIFI_VERSION}.nar && \
wget -c -P ./nifi_extensions https://repo1.maven.org/maven2/org/apache/nifi/nifi-iceberg-processors-nar/${NIFI_VERSION}/nifi-iceberg-processors-nar-${NIFI_VERSION}.nar && \
wget -c -P ./nifi_extensions https://repo1.maven.org/maven2/org/apache/nifi/nifi-iceberg-services-api-nar/${NIFI_VERSION}/nifi-iceberg-services-api-nar-${NIFI_VERSION}.nar && \
wget -c -P ./nifi_extensions https://repo1.maven.org/maven2/org/apache/nifi/nifi-iceberg-services-nar/${NIFI_VERSION}/nifi-iceberg-services-nar-${NIFI_VERSION}.nar
