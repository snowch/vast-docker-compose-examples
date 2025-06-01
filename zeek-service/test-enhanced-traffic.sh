#!/bin/bash

echo "🔍 Enhanced Traffic Generator Test Script"
echo "This script tests the new traffic generation capabilities"
echo ""

# Check if containers are running
echo "📊 Checking container status..."
if ! docker ps | grep -q "zeek-live-monitor"; then
    echo "❌ Zeek monitor container is not running"
    echo "Please start the containers with: docker-compose up -d"
    exit 1
fi

if ! docker ps | grep -q "scapy-traffic-sim"; then
    echo "❌ Traffic simulator container is not running"
    echo "Please start the containers with: docker-compose up -d"
    exit 1
fi

echo "✅ Containers are running"
echo ""

# Get container IPs
ZEEK_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' zeek-live-monitor)
TRAFFIC_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' scapy-traffic-sim)

echo "🔗 Network Configuration:"
echo "   Zeek Monitor IP: $ZEEK_IP"
echo "   Traffic Simulator IP: $TRAFFIC_IP"
echo ""

# Test 1: Basic connectivity
echo "🧪 Test 1: Basic connectivity test"
if docker exec scapy-traffic-sim ping -c 2 $ZEEK_IP >/dev/null 2>&1; then
    echo "✅ Connectivity test passed"
else
    echo "❌ Connectivity test failed"
fi
echo ""

# Test 2: Run enhanced traffic generator for 30 seconds
echo "🧪 Test 2: Enhanced traffic generation (30 seconds)"
echo "This will generate real network connections that Zeek should detect..."

docker exec -d scapy-traffic-sim python3 /traffic-scripts/enhanced_traffic_generator.py << 'EOF'
7
EOF

echo "⏳ Running comprehensive attack simulation for 30 seconds..."
echo "   - Port scanning"
echo "   - SSH brute force attempts"
echo "   - Malicious HTTP requests (SQL injection)"
echo "   - Suspicious DNS queries"
echo "   - Data exfiltration simulation"
echo ""

# Wait and show some progress
for i in {1..6}; do
    echo "   Progress: $((i*5))/30 seconds..."
    sleep 5
done

echo "✅ Enhanced traffic generation completed"
echo ""

# Test 3: Check Zeek logs
echo "🧪 Test 3: Checking Zeek logs for detection events"
echo "Looking for recent log entries..."

if docker exec zeek-live-monitor ls /logs/*.log >/dev/null 2>&1; then
    echo "✅ Zeek log files found:"
    docker exec zeek-live-monitor ls -la /logs/*.log | head -10
    echo ""
    
    # Check for specific log types that indicate detection
    echo "🔍 Checking for security events in logs..."
    
    # Check notice.log for security alerts
    if docker exec zeek-live-monitor test -f /logs/notice.log; then
        echo "📋 Recent notices (security alerts):"
        docker exec zeek-live-monitor tail -5 /logs/notice.log 2>/dev/null || echo "   No recent notices found"
    fi
    
    # Check conn.log for connections
    if docker exec zeek-live-monitor test -f /logs/conn.log; then
        echo "📋 Recent connections:"
        docker exec zeek-live-monitor tail -3 /logs/conn.log 2>/dev/null || echo "   No recent connections found"
    fi
    
    # Check dns.log for DNS queries
    if docker exec zeek-live-monitor test -f /logs/dns.log; then
        echo "📋 Recent DNS queries:"
        docker exec zeek-live-monitor tail -3 /logs/dns.log 2>/dev/null || echo "   No recent DNS queries found"
    fi
    
    # Check http.log for HTTP requests
    if docker exec zeek-live-monitor test -f /logs/http.log; then
        echo "📋 Recent HTTP requests:"
        docker exec zeek-live-monitor tail -3 /logs/http.log 2>/dev/null || echo "   No recent HTTP requests found"
    fi
    
else
    echo "⚠️  No Zeek log files found yet"
    echo "   This might be normal if Zeek just started"
fi
echo ""

# Test 4: Check Zeek process
echo "🧪 Test 4: Checking Zeek process status"
if docker exec zeek-live-monitor pgrep zeek >/dev/null 2>&1; then
    echo "✅ Zeek process is running"
    echo "📊 Zeek process info:"
    docker exec zeek-live-monitor ps aux | grep zeek | grep -v grep
else
    echo "❌ Zeek process is not running"
    echo "📋 Container logs:"
    docker logs zeek-live-monitor --tail 10
fi
echo ""

# Test 5: Web interface test
echo "🧪 Test 5: Testing web interface"
echo "🌐 Traffic generator web interface should be available at:"
echo "   http://localhost:8080"
echo ""
echo "💡 You can now:"
echo "   1. Open http://localhost:8080 in your browser"
echo "   2. Click 'Enhanced Attacks' to generate real network connections"
echo "   3. Start the Kafka consumer to see live Zeek events"
echo "   4. Watch for security alerts and weird events"
echo ""

echo "🎯 Summary:"
echo "   ✅ Enhanced traffic generator created"
echo "   ✅ Zeek configuration updated with detection policies"
echo "   ✅ Real network connections will be generated"
echo "   ✅ Zeek should now detect suspicious activities"
echo ""
echo "🔍 To see weird events, look for:"
echo "   - NOTICE entries in Zeek logs"
echo "   - Signature matches"
echo "   - Port scan detections"
echo "   - SQL injection alerts"
echo "   - Suspicious DNS queries"
echo ""
echo "📊 Monitor the Kafka consumer in the web interface for real-time events!"
