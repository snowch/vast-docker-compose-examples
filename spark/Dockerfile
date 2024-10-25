# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

###### v add spark packages
ARG spark_jar_packages
###### ^ add spark packages

ARG REGISTRY=quay.io
ARG OWNER=jupyter
ARG BASE_CONTAINER=$REGISTRY/$OWNER/scipy-notebook
FROM $BASE_CONTAINER

LABEL maintainer="Jupyter Project <jupyter@googlegroups.com>"

# Fix: https://github.com/hadolint/hadolint/wiki/DL4006
# Fix: https://github.com/koalaman/shellcheck/wiki/SC3014
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

USER root

# Spark dependencies
# Default values can be overridden at build time
# (ARGS are in lowercase to distinguish them from ENV)
ARG openjdk_version="17"

RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    "openjdk-${openjdk_version}-jre-headless" \
    ca-certificates-java && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# If spark_version is not set, latest stable Spark will be installed
ARG spark_version
ARG hadoop_version="3"
# If scala_version is not set, Spark without Scala will be installed
ARG scala_version
# URL to use for Spark downloads
# You need to use https://archive.apache.org/dist/spark/ website if you want to download old Spark versions
# But it seems to be slower, that's why we use the recommended site for download
ARG spark_download_url="https://dlcdn.apache.org/spark/"

ENV SPARK_HOME=/usr/local/spark
ENV PATH="${PATH}:${SPARK_HOME}/bin"
ENV SPARK_OPTS="--driver-java-options=-Xms1024M --driver-java-options=-Xmx4096M --driver-java-options=-Dlog4j.logLevel=info"

#COPY setup_spark.py /opt/setup-scripts/
RUN wget -O  /opt/setup-scripts/setup_spark.py https://raw.githubusercontent.com/jupyter/docker-stacks/main/images/pyspark-notebook/setup_spark.py
RUN chmod a+x /opt/setup-scripts/setup_spark.py

# Setup Spark
RUN /opt/setup-scripts/setup_spark.py \
    --spark-version="${spark_version}" \
    --hadoop-version="${hadoop_version}" \
    --scala-version="${scala_version}" \
    --spark-download-url="${spark_download_url}" \
    --spark_jars_packages="${spark_jars_packages}"  ### add spark packages 

# Configure IPython system-wide
#COPY ipython_kernel_config.py "/etc/ipython/"
RUN mkdir /etc/ipython
RUN wget -O /etc/ipython/ipython_kernel_config.py https://raw.githubusercontent.com/jupyter/docker-stacks/main/images/pyspark-notebook/ipython_kernel_config.py
RUN fix-permissions "/etc/ipython/"

# \/ Vast Database configuration \/
#
COPY spark-defaults.conf /usr/local/spark/conf/
COPY spark-env.sh /usr/local/spark/conf/
COPY log4j2.properties /usr/local/spark/conf/

RUN wget https://github.com/vast-data/vast-db-connectors/releases/download/spark3-vast-3.4.1-f93839bfa38a/spark3-vast-3.4.1-f93839bfa38a.zip && \
    unzip spark3-vast-3.4.1-f93839bfa38a.zip && \
    mv spark3-vast-3.4.1-f93839bfa38a /usr/local/spark/jars/ && \
    rm spark3-vast-3.4.1-f93839bfa38a.zip

RUN rm -f .wget-hsts    
#
# /\ Vast Database configuration /\

USER ${NB_UID}

# Install pyarrow
# NOTE: It's important to ensure compatibility between Pandas versions.
# The pandas version in this Dockerfile should match the version
# on which the Pandas API for Spark is built.
# To find the right version:
# 1. Check out the Spark branch you are on: <https://github.com/apache/spark>
# 2. Find the pandas version in the file `dev/infra/Dockerfile`.
RUN mamba install --yes \
    'grpcio-status' \
    'grpcio' \
    'pandas=2.2.2' \
    'pyarrow' && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

WORKDIR "${HOME}"
EXPOSE 4040

