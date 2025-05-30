#!/bin/bash

# Virtual Network Setup Script for Safe Traffic Simulation
# Creates isolated network namespaces and virtual interfaces

set -e

VETH_PAIR1="veth-sim0"
VETH_PAIR2="veth-sim1"
BRIDGE_NAME="br-zeek-sim"
NAMESPACE1="sim-client"
NAMESPACE2="sim-server"

echo "🌐 Setting up virtual network environment for traffic simulation..."

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up virtual network..."
    ip netns del $NAMESPACE1 2>/dev/null || true
    ip netns del $NAMESPACE2 2>/dev/null || true
    ip link del $BRIDGE_NAME 2>/dev/null || true
    ip link del $VETH_PAIR1 2>/dev/null || true
    echo "Cleanup completed"
}

# Check if we're running in daemon mode
DAEMON_MODE=false
if [ "$1" = "--daemon" ]; then
    DAEMON_MODE=true
    echo "🔄 Running in daemon mode - virtual network will persist"
else
    # Set trap for cleanup only in non-daemon mode
    trap cleanup EXIT
fi

# Clean up any existing interfaces first
echo "🧹 Cleaning up any existing virtual network..."
cleanup

# Create network bridge for simulation
echo "📡 Creating simulation bridge: $BRIDGE_NAME"
ip link add name $BRIDGE_NAME type bridge
ip link set $BRIDGE_NAME up
ip addr add 192.168.200.1/24 dev $BRIDGE_NAME

# Create virtual ethernet pair for client simulation
echo "🔗 Creating virtual ethernet pair: $VETH_PAIR1 <-> $VETH_PAIR2"
ip link add $VETH_PAIR1 type veth peer name $VETH_PAIR2

# Create network namespaces
echo "📦 Creating network namespaces..."
ip netns add $NAMESPACE1  # Client namespace
ip netns add $NAMESPACE2  # Server namespace

# Move one end of veth pair to client namespace
ip link set $VETH_PAIR1 netns $NAMESPACE1
ip netns exec $NAMESPACE1 ip link set $VETH_PAIR1 up
ip netns exec $NAMESPACE1 ip addr add 192.168.200.10/24 dev $VETH_PAIR1
ip netns exec $NAMESPACE1 ip route add default via 192.168.200.1

# Move other end to server namespace
ip link set $VETH_PAIR2 netns $NAMESPACE2
ip netns exec $NAMESPACE2 ip link set $VETH_PAIR2 up
ip netns exec $NAMESPACE2 ip addr add 192.168.200.20/24 dev $VETH_PAIR2
ip netns exec $NAMESPACE2 ip route add default via 192.168.200.1

# Create additional virtual interfaces attached to bridge
for i in {3..6}; do
    VETH_HOST="veth-host$i"
    VETH_GUEST="veth-guest$i"
    
    echo "🔌 Creating virtual interface pair: $VETH_HOST <-> $VETH_GUEST"
    ip link add $VETH_HOST type veth peer name $VETH_GUEST
    
    # Connect host side to bridge
    ip link set $VETH_HOST master $BRIDGE_NAME
    ip link set $VETH_HOST up
    
    # Configure guest side with unique IP
    ip link set $VETH_GUEST up
    ip addr add 192.168.200.$((10 + i))/24 dev $VETH_GUEST
done

# Enable IP forwarding for the bridge
echo 1 > /proc/sys/net/ipv4/ip_forward

# Create TAP interface for packet capture
echo "📡 Creating TAP interface for monitoring..."
ip tuntap add mode tap name tap-monitor
ip link set tap-monitor up
ip link set tap-monitor master $BRIDGE_NAME

echo "✅ Virtual network setup complete!"
echo ""
echo "📊 Network Topology:"
echo "  Bridge: $BRIDGE_NAME (192.168.200.1/24)"
echo "  Client Namespace: $NAMESPACE1 (192.168.200.10/24)"
echo "  Server Namespace: $NAMESPACE2 (192.168.200.20/24)"
echo "  Virtual Hosts: 192.168.200.13-16/24"
echo "  Monitor TAP: tap-monitor"
echo ""
echo "🔍 Available interfaces for traffic simulation:"
ip link show | grep -E "(veth|br-zeek|tap)" | awk '{print "  - " $2}' | sed 's/:$//'
echo ""
echo "🧪 Test connectivity:"
echo "  ip netns exec $NAMESPACE1 ping -c 2 192.168.200.20"
echo "  ip netns exec $NAMESPACE2 ping -c 2 192.168.200.10"

# Test connectivity
echo "🧪 Testing virtual network connectivity..."
if ip netns exec $NAMESPACE1 ping -c 2 -W 2 192.168.200.20 >/dev/null 2>&1; then
    echo "✅ Client -> Server connectivity: OK"
else
    echo "❌ Client -> Server connectivity: FAILED"
fi

if ip netns exec $NAMESPACE2 ping -c 2 -W 2 192.168.200.10 >/dev/null 2>&1; then
    echo "✅ Server -> Client connectivity: OK"
else
    echo "❌ Server -> Client connectivity: FAILED"
fi

# Verify bridge was created successfully
if ip link show $BRIDGE_NAME >/dev/null 2>&1; then
    echo "✅ Bridge $BRIDGE_NAME created successfully"
    echo "📊 Bridge details:"
    ip addr show $BRIDGE_NAME
else
    echo "❌ Failed to create bridge $BRIDGE_NAME"
    exit 1
fi

if [ "$DAEMON_MODE" = true ]; then
    echo "🔄 Daemon mode: Keeping virtual network active..."
    echo "Use 'docker-compose down' to cleanup the virtual network"
    
    # Keep the script running in background to maintain the network
    while true; do
        sleep 30
        # Verify network is still healthy
        if ! ip link show $BRIDGE_NAME >/dev/null 2>&1; then
            echo "❌ Bridge interface lost - recreating..."
            exit 1
        fi
        # Print status every 5 minutes
        if [ $(($(date +%s) % 300)) -eq 0 ]; then
            echo "✅ Virtual network still active: $BRIDGE_NAME"
        fi
    done
else
    echo "🔄 Virtual network active - press Ctrl+C to cleanup and exit"
    # Keep the script running to maintain the network
    while true; do
        sleep 30
        # Verify network is still healthy
        if ! ip link show $BRIDGE_NAME >/dev/null 2>&1; then
            echo "❌ Bridge interface lost - recreating..."
            exit 1
        fi
    done
fi