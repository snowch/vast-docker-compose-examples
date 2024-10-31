#!/bin/bash
set -eaux

# Install necessary packages
apt-get update && apt-get install -y --no-install-recommends curl jq ca-certificates wget && rm -rf /var/lib/apt/lists/*

# Get the latest VAST NAR release version
CURL_OUTPUT=$(curl -sSL https://api.github.com/repos/vast-data/vastdb_nifi/releases/latest)
echo "Curl output: $CURL_OUTPUT"  # Print raw curl output for debugging

LATEST_VAST_NAR_RELEASE=$(echo "$CURL_OUTPUT" | jq -r ".tag_name" | cut -d "v" -f2)

echo "LATEST_VAST_NAR_RELEASE: $LATEST_VAST_NAR_RELEASE"  # Debug output for the release version

# Check if the variable is empty
if [ -z "$LATEST_VAST_NAR_RELEASE" ]; then 
  echo "Error: LATEST_VAST_NAR_RELEASE is not set or empty"; 
  exit 1; 
fi

# Download VAST NAR using the retrieved version
wget --continue --no-check-certificate -O /mnt/jars/vastdb_nifi-${LATEST_VAST_NAR_RELEASE}-linux-x86_64-py39.nar https://github.com/vast-data/vastdb_nifi/releases/download/v${LATEST_VAST_NAR_RELEASE}/vastdb_nifi-${LATEST_VAST_NAR_RELEASE}-linux-x86_64-py39.nar

# Download remaining NIFI NARS using environment variables (assuming set)
wget --continue --no-check-certificate -O /mnt/jars/nifi-parquet-nar-${NIFI_VERSION}.nar https://repo1.maven.org/maven2/org/apache/nifi/nifi-parquet-nar/${NIFI_VERSION}/nifi-parquet-nar-${NIFI_VERSION}.nar
wget --continue --no-check-certificate -O /mnt/jars/nifi-hadoop-libraries-nar-${NIFI_VERSION}.nar https://repo1.maven.org/maven2/org/apache/nifi/nifi-hadoop-libraries-nar/${NIFI_VERSION}/nifi-hadoop-libraries-nar-${NIFI_VERSION}.nar
wget --continue --no-check-certificate -O /mnt/jars/nifi-iceberg-processors-nar-${NIFI_VERSION}.nar https://repo1.maven.org/maven2/org/apache/nifi/nifi-iceberg-processors-nar/${NIFI_VERSION}/nifi-iceberg-processors-nar-${NIFI_VERSION}.nar
wget --continue --no-check-certificate -O /mnt/jars/nifi-iceberg-services-api-nar-${NIFI_VERSION}.nar https://repo1.maven.org/maven2/org/apache/nifi/nifi-iceberg-services-api-nar/${NIFI_VERSION}/nifi-iceberg-services-api-nar-${NIFI_VERSION}.nar
wget --continue --no-check-certificate -O /mnt/jars/nifi-iceberg-services-nar-${NIFI_VERSION}.nar https://repo1.maven.org/maven2/org/apache/nifi/nifi-iceberg-services-nar/${NIFI_VERSION}/nifi-iceberg-services-nar-${NIFI_VERSION}.nar
