# Use official Zeek Docker image as base
FROM zeek/zeek:latest

# Install required build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    g++ \
    cmake \
    make \
    libpcap-dev \
    curl \
    ca-certificates \
    libsasl2-dev \
    libssl-dev \
    pkg-config \
    netcat-openbsd \
    iproute2 \
    tcpdump \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install librdkafka
WORKDIR /tmp
RUN curl -L https://github.com/edenhill/librdkafka/archive/v1.4.4.tar.gz | tar xvz && \
    cd librdkafka-1.4.4/ && \
    ./configure --enable-sasl && \
    make && \
    make install && \
    ldconfig && \
    cd / && \
    rm -rf /tmp/librdkafka-1.4.4

# Install Zeek Kafka plugin using zkg
RUN zkg install seisollc/zeek-kafka --version v1.2.0 --force

# Verify plugin installation
RUN zeek -N Seiso::Kafka

# Create necessary directories
RUN mkdir -p /logs /scripts /var/log/supervisor

# Copy monitoring scripts and configurations
COPY scripts/monitor-live.sh /scripts/
COPY nginx-proxy.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN chmod +x /scripts/*.sh

# Set working directory
WORKDIR /

# Default command - can be overridden by docker-compose
# If no command specified, run supervisor to manage nginx and zeek
CMD ["/usr/bin/supervisord"]
