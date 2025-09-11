# Base Jupyter image setup
ARG REGISTRY=quay.io
ARG OWNER=jupyter
ARG BASE_CONTAINER=$REGISTRY/$OWNER/scipy-notebook:b74418220768
FROM $BASE_CONTAINER

LABEL maintainer="Jupyter Project <jupyter@googlegroups.com>"

# Configure shell for script compatibility
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

USER root

# Enable repositories and install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    sudo fuse libfuse2 nfs-common && \
    rm -rf /var/lib/apt/lists/*

# Set up sudo for jovyan user
RUN echo "jovyan ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Download and install mount-s3
RUN wget https://s3.amazonaws.com/mountpoint-s3-release/latest/x86_64/mount-s3.deb && \
    apt-get install -y ./mount-s3.deb && \
    rm ./mount-s3.deb

# Java installation for Spark dependencies
ARG openjdk_version="17"

RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    "openjdk-${openjdk_version}-jre-headless" \
    ca-certificates-java && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends  python3-graphviz && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# If spark_version is not set, latest stable Spark will be installed
ARG spark_version
ARG hadoop_version="3"
# If scala_version is not set, Spark without Scala will be installed
ARG scala_version
# URL to use for Spark downloads
# You need to use https://archive.apache.org/dist/spark/ website if you want to download old Spark versions
# But it seems to be slower, that's why we use the recommended site for download
ARG spark_download_url="https://archive.apache.org/dist/spark/"

ENV SPARK_HOME=/usr/local/spark
ENV PATH="${PATH}:${SPARK_HOME}/bin"
ENV SPARK_OPTS="--driver-java-options=-Xms1024M --driver-java-options=-Xmx4096M --driver-java-options=-Dlog4j.logLevel=info"

# Install Spark and dependencies
COPY setup_spark.py /opt/setup-scripts/
RUN chmod a+x /opt/setup-scripts/setup_spark.py
RUN /opt/setup-scripts/setup_spark.py \
    --spark-version="${spark_version}" \
    --hadoop-version="${hadoop_version}" \
    --scala-version="${scala_version}" \
    --spark-download-url="${spark_download_url}"

# Download necessary JARs for S3 and Spark compatibility
RUN wget -c -O ${SPARK_HOME}/jars/aws-java-sdk.jar https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk/1.12.742/aws-java-sdk-1.12.742.jar && \
    wget -c -O ${SPARK_HOME}/jars/hadoop-aws.jar https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    wget -c -O ${SPARK_HOME}/jars/hadoop-client.jar https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client/3.3.4/hadoop-client-3.3.4.jar && \
    wget -c -O ${SPARK_HOME}/jars/aws-java-sdk-dynamodb.jar https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-dynamodb/1.12.742/aws-java-sdk-dynamodb-1.12.742.jar && \
    wget -c -O ${SPARK_HOME}/jars/iceberg-spark-runtime.jar https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.4_2.13/1.6.1/iceberg-spark-runtime-3.4_2.13-1.6.1.jar

# Configure IPython
RUN mkdir /etc/ipython && \
    wget -O /etc/ipython/ipython_kernel_config.py https://raw.githubusercontent.com/jupyter/docker-stacks/main/images/pyspark-notebook/ipython_kernel_config.py
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

# Create the mount script
COPY mount_s3.sh /usr/local/bin/mount_s3.sh
RUN chmod +x /usr/local/bin/mount_s3.sh

COPY s3cmd_configure.sh /usr/local/bin/s3cmd_configure.sh
RUN chmod +x /usr/local/bin/s3cmd_configure.sh

USER ${NB_UID}

#RUN curl https://sh.rustup.rs -sSf | sh -s -- -y && \
#    . "$HOME/.cargo/env" && \
#    cargo install datafusion-cli

# Install pyarrow and pandas
RUN mamba install --yes \
    'grpcio-status' \
    'grpcio' \
    'pandas=2.2.2' \
    'pyarrow' && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

RUN pip3 install \
    s3cmd==2.4.0 \
    urllib3 \
    findspark \
    boto3 \
    jupysql \
    trino \
    sqlalchemy-trino

# Copy configuration files for Spark
COPY spark-defaults.conf /usr/local/spark/conf/
COPY spark-env.sh /usr/local/spark/conf/
COPY log4j2.properties /usr/local/spark/conf/


#########
# --- Add new kernel for examples/banking/customer_lifetime_value ---
# You can use ARGs to make the kernel name, Python version, and display name configurable
ARG NEW_KERNEL_ENV_NAME="custom_py310"
ARG NEW_KERNEL_PYTHON_VERSION="3.10"
ARG NEW_KERNEL_DISPLAY_NAME="Python 3.10 (Custom - CLV Analysis)"
ARG NEW_KERNEL_PACKAGES="pandas numpy scikit-learn matplotlib pymc-marketing arviz graphviz vastdb pyarrow" # Space-separated list of packages

RUN echo "Creating new Conda environment for kernel: ${NEW_KERNEL_ENV_NAME} with Python ${NEW_KERNEL_PYTHON_VERSION}" && \
    # Create the new Conda environment with the specified Python version
    mamba create -n "${NEW_KERNEL_ENV_NAME}" python="${NEW_KERNEL_PYTHON_VERSION}" -y && \
    \
    echo "Installing ipykernel and packages (${NEW_KERNEL_PACKAGES}) into ${NEW_KERNEL_ENV_NAME}" && \
    # Install ipykernel and other desired packages into the new environment
    # Note: mamba install -n env_name package1 package2 ...
    mamba install -n "${NEW_KERNEL_ENV_NAME}" ipykernel ${NEW_KERNEL_PACKAGES} -y && \
    \
    # (Optional but recommended for explicit control over display name and ensuring registration)
    # If nb_conda_kernels is present (usual for jupyter/scipy-notebook),
    # it would auto-detect this environment once ipykernel is installed.
    # This explicit registration gives you control over the display name.
    echo "Registering ${NEW_KERNEL_ENV_NAME} as a Jupyter kernel with display name: ${NEW_KERNEL_DISPLAY_NAME}" && \
    mamba run -n "${NEW_KERNEL_ENV_NAME}" python -m ipykernel install --user --name="${NEW_KERNEL_ENV_NAME}_kernel_spec" --display-name="${NEW_KERNEL_DISPLAY_NAME}" && \
    \
    echo "Cleaning up mamba caches" && \
    mamba clean --all -f -y && \
    \
    # Ensure permissions are correct for the new environment and user's kernels directory
    # Conda environments are typically in ${CONDA_DIR}/envs/
    # User-installed kernelspecs are in /home/${NB_USER}/.local/share/jupyter/kernels/
    fix-permissions "${CONDA_DIR}/envs/${NEW_KERNEL_ENV_NAME}" && \
    fix-permissions "/home/${NB_USER}/.local"
# --- End new kernel addition ---
##########

# USER ${NB_UID}

# Set the startup command to run the mount script and then start Jupyter
CMD ["/bin/bash", "-c", "/usr/local/bin/mount_s3.sh && \
if [ ! -z \"$JUPYTER_PASSWORD\" ]; then \
  PW_HASH=$(python -c \"from jupyter_server.auth import passwd; print(passwd('$JUPYTER_PASSWORD'))\"); \
  start-notebook.sh --ServerApp.password=\"$PW_HASH\" --ServerApp.ip='*' --ServerApp.port=8888 --ServerApp.open_browser=False; \
else \
  start-notebook.sh --ServerApp.ip='*' --ServerApp.port=8888 --ServerApp.open_browser=False; \
fi"]

WORKDIR "${HOME}"
EXPOSE 4040
