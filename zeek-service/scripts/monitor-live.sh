#!/bin/bash

# Simplified Live Traffic Monitor Script for Zeek-Kafka
# Monitors container's default network interface

set -eau

echo "🔍 Starting Zeek live traffic monitoring (simplified)..."

# Configuration
ZEEK_CONFIG="/config/kafka-live.zeek"
INTERFACE="${MONITOR_INTERFACE:-eth0}"
KAFKA_BROKER="${KAFKA_BROKER:-172.200.204.1:9092}"
KAFKA_TOPIC="${KAFKA_TOPIC:-zeek-live-logs}"

# Wait for network interface to be ready
echo "⏳ Waiting for network interface: $INTERFACE"
for i in {1..10}; do
    if ip link show "$INTERFACE" >/dev/null 2>&1; then
        echo "✅ Interface $INTERFACE is available"
        break
    fi
    echo "Waiting for interface... attempt $i/10"
    sleep 1
done

# Verify interface is up
if ! ip link show "$INTERFACE" >/dev/null 2>&1; then
    echo "❌ Interface $INTERFACE not found. Available interfaces:"
    ip link show | grep -E '^[0-9]+:' | awk '{print $2}' | sed 's/:$//'
    exit 1
fi

# Show interface details
echo "📡 Monitoring interface details:"
ip addr show "$INTERFACE"

# Test Kafka connectivity (optional - don't fail if unreachable)
echo "🔌 Testing Kafka connectivity to $KAFKA_BROKER..."
if timeout 5 nc -z $(echo $KAFKA_BROKER | tr ':' ' ') 2>/dev/null; then
    echo "✅ Kafka broker is reachable"
else
    echo "⚠️  Warning: Cannot connect to Kafka broker $KAFKA_BROKER"
    echo "Proceeding anyway - Zeek will retry connections"
fi

# Check if configuration file exists
if [ ! -f "$ZEEK_CONFIG" ]; then
    echo "❌ Configuration file not found: $ZEEK_CONFIG"
    echo "Please ensure the zeek-config directory is properly mounted"
    exit 1
else
    echo "✅ Using existing configuration: $ZEEK_CONFIG"
fi

echo "🚀 Starting Zeek live monitoring on interface: $INTERFACE"
echo "📊 Configuration: $ZEEK_CONFIG"
echo "🔗 Kafka Broker: $KAFKA_BROKER"
echo "📤 Kafka Topic: $KAFKA_TOPIC"
echo ""
echo "💡 This simplified setup monitors traffic on the container's default network interface"
echo "💡 All containers in the zeek-network will have their traffic monitored"

# Start Zeek in live monitoring mode with checksum validation disabled
# The -C flag ignores invalid checksums (common in containerized environments)
exec zeek -C -i "$INTERFACE" "$ZEEK_CONFIG"
