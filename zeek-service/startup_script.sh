#!/bin/bash

set -eau

if docker compose version &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker compose"
elif docker-compose version &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker-compose"
else
  echo "Neither 'docker compose' nor 'docker-compose' command found. Please install Docker Compose."
  exit 1
fi

# Startup script for Zeek-Kafka Docker Compose setup with Virtual Network and Live Monitoring

echo "🚀 Starting Zeek-Kafka Live Network Traffic Analysis System"
echo "=============================================================="

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p zeek-config zeek-logs scripts traffic-scripts

# Make scripts executable
chmod +x scripts/setup-virtual-network.sh scripts/monitor-live.sh

# Check if live Kafka configuration exists
if [ ! -f "zeek-config/kafka-live.zeek" ]; then
    echo "⚠️  Live Kafka configuration not found. Creating default config..."
    cat > zeek-config/kafka-live.zeek << 'EOF'
# Live traffic monitoring configuration for Zeek-Kafka

# AUTO-GENERATED FILE - DO NOT EDIT

@load base/protocols/conn
@load base/protocols/dns
@load base/protocols/http
@load base/protocols/ssl
@load base/protocols/ftp
@load base/protocols/ssh
@load base/protocols/smtp
@load Seiso/Kafka

# Kafka configuration - Update these values for your environment
redef Kafka::topic_name = "zeek-live-logs";
redef Kafka::kafka_conf = table(
    ["metadata.broker.list"] = "172.200.204.1:9092",
    ["client.id"] = "zeek-live-monitor",
    ["batch.num.messages"] = "1000",
    ["queue.buffering.max.ms"] = "100"
);

# Enable all active logs to be sent to Kafka
redef Kafka::send_all_active_logs = T;

# Use ISO8601 timestamps for better readability
redef Kafka::json_timestamps = JSON::TS_ISO8601;

# Tag JSON messages for easier identification
redef Kafka::tag_json = T;

# Enable JSON logging
redef LogAscii::use_json = T;
EOF
fi

# Build and start the containers
echo "🔨 Building Docker containers..."
$DOCKER_COMPOSE_CMD build

echo "🌐 Starting virtual network setup..."
$DOCKER_COMPOSE_CMD up -d network-setup

# Wait for network setup
echo "⏳ Waiting for virtual network to be ready..."
sleep 15

# Verify virtual network
echo "🔍 Checking virtual network status..."
if ip link show br-zeek-sim >/dev/null 2>&1; then
    echo "✅ Virtual bridge network is ready: br-zeek-sim"
    ip addr show br-zeek-sim | grep inet
else
    echo "❌ Virtual network setup failed"
    echo "Checking network setup logs..."
    $DOCKER_COMPOSE_CMD logs network-setup
fi

echo "🚀 Starting traffic simulation and live monitoring services..."
$DOCKER_COMPOSE_CMD up -d traffic-simulator zeek-live

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Display status
echo ""
echo "✅ Services Status:"
$DOCKER_COMPOSE_CMD ps

echo ""
echo "🌐 Virtual Network Topology:"
echo "  📡 Simulation Bridge: br-zeek-sim (192.168.200.1/24)"
echo "  🖥️  Client Namespace: sim-client (192.168.200.10/24)"
echo "  🖥️  Server Namespace: sim-server (192.168.200.20/24)"
echo "  🔌 Virtual Hosts: veth-guest3-6 (192.168.200.13-16/24)"
echo "  📊 Monitor TAP: tap-monitor"
echo ""
echo "🌐 Web Interfaces:"
echo "  - Scapy Traffic Generator: http://localhost:8080"
echo ""
echo "🎭 Available Simulation Scenarios:"
echo "  1. Web Browsing - Realistic HTTP/HTTPS traffic"
echo "  2. File Transfer - FTP, SFTP, SMB traffic"
echo "  3. Video Streaming - High-bandwidth UDP streams"
echo "  4. Office Network - Email, printing, file shares"
echo "  5. Security Testing - Simulated malicious activity for IDS/IPS testing"
echo ""
echo "📊 Traffic Generation Modes:"
echo "  - Realistic Scenario Simulation (recommended)"
echo "  - Direct Interface Injection"
echo "  - Network Namespace Isolation"
echo "  - Live Traffic Monitoring (NEW!)"
echo ""
echo "🔧 Management Commands:"
echo "  - View all logs: $DOCKER_COMPOSE_CMD logs -f"
echo "  - View traffic logs: $DOCKER_COMPOSE_CMD logs -f traffic-simulator"
echo "  - View live Zeek logs: $DOCKER_COMPOSE_CMD logs -f zeek-live"
echo "  - Stop services: $DOCKER_COMPOSE_CMD down"
echo "  - Restart: $DOCKER_COMPOSE_CMD restart"
echo ""
echo "📁 Directory Structure:"
echo "  - zeek-logs/: Zeek output logs (local copy)"
echo "  - zeek-config/: Zeek configuration files"
echo "  - traffic-scripts/: Traffic generation scripts"
echo ""
echo "🛡️  Security Features:"
echo "  - Isolated virtual network (no impact on host networking)"
echo "  - Network namespaces for complete traffic isolation"
echo "  - Simulated malicious traffic for security testing"
echo "  - Safe environment for IDS/IPS testing"
echo ""
echo "⚡ Live Monitoring Features:"
echo "  - Real-time packet analysis (no PCAP files needed)"
echo "  - Direct Kafka streaming from network interfaces"
echo "  - Low-latency security event detection"
echo "  - Continuous traffic analysis"
echo ""
echo "📈 Monitoring Virtual Network:"
echo "  - Monitor bridge: ip -s link show br-zeek-sim"
echo "  - Test connectivity: ip netns exec sim-client ping 192.168.200.20"
echo "  - Capture traffic: tcpdump -i br-zeek-sim"
echo ""
echo "🚀 Quick Start:"
echo "  1. Open http://localhost:8080"
echo "  2. Click 'Web Browsing Simulation' to start"
echo "  3. Watch live Zeek analysis in real-time"
echo "  4. Monitor Kafka logs in your VAST cluster"
echo "  5. Check live processing: $DOCKER_COMPOSE_CMD logs -f zeek-live"

# Test virtual network connectivity
echo ""
echo "🧪 Testing virtual network connectivity..."
if $DOCKER_COMPOSE_CMD exec -T traffic-simulator ip netns exec sim-client ping -c 2 -W 2 192.168.200.20 >/dev/null 2>&1; then
    echo "✅ Virtual network connectivity: WORKING"
else
    echo "⚠️  Virtual network connectivity test failed - check network setup"
fi

# Test Zeek live monitoring
echo ""
echo "🔍 Testing live monitoring setup..."
if $DOCKER_COMPOSE_CMD exec -T zeek-live ip link show br-zeek-sim >/dev/null 2>&1; then
    echo "✅ Live monitoring interface access: WORKING"
else
    echo "⚠️  Live monitoring interface access test failed"
fi

echo ""
echo "🎉 Live Network Traffic Analysis System is ready!"
echo "📱 Access the web interface at: http://localhost:8080"
echo "📊 Monitor live analysis: $DOCKER_COMPOSE_CMD logs -f zeek-live"