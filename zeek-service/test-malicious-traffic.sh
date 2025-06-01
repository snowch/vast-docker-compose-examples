#!/bin/bash

echo "🔍 Testing Malicious Traffic Detection"
echo "======================================"

# Get the zeek-live container IP
ZEEK_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' zeek-live-monitor 2>/dev/null)

if [ -z "$ZEEK_IP" ]; then
    echo "❌ Could not find zeek-live-monitor container IP"
    echo "Make sure the containers are running with: docker-compose up -d"
    exit 1
fi

echo "✅ Found Zeek monitor at: $ZEEK_IP"

# Test 1: SQL Injection Traffic
echo ""
echo "🧪 Test 1: Generating SQL Injection Traffic"
echo "Target: http://$ZEEK_IP:8082"

# Generate malicious HTTP requests
curl -s "http://$ZEEK_IP:8082/login?user=admin&pass=' UNION SELECT * FROM users--" || echo "Request sent (connection may be refused)"
curl -s "http://$ZEEK_IP:8082/search?q=' DROP TABLE users--" || echo "Request sent (connection may be refused)"
curl -s "http://$ZEEK_IP:8082/api/data?id=1' INSERT INTO admin VALUES('hacker')--" || echo "Request sent (connection may be refused)"

echo "✅ SQL injection requests sent"

# Test 2: Port Scan
echo ""
echo "🧪 Test 2: Generating Port Scan Traffic"
echo "Scanning common ports on $ZEEK_IP"

for port in 21 22 23 25 53 80 110 143 443 993 995; do
    timeout 1 nc -z $ZEEK_IP $port 2>/dev/null && echo "Port $port: OPEN" || echo "Port $port: CLOSED/FILTERED"
done

echo "✅ Port scan completed"

# Test 3: DNS Queries with suspicious domains
echo ""
echo "🧪 Test 3: Generating Suspicious DNS Queries"

# Use the gateway as DNS server (should be monitored)
GATEWAY_IP=$(docker network inspect zeek-network -f '{{range .IPAM.Config}}{{.Gateway}}{{end}}' 2>/dev/null)
if [ -n "$GATEWAY_IP" ]; then
    echo "Using DNS server: $GATEWAY_IP"
    nslookup malware-c2.evil $GATEWAY_IP 2>/dev/null || echo "DNS query sent"
    nslookup phishing.bad $GATEWAY_IP 2>/dev/null || echo "DNS query sent"
    nslookup botnet.cmd $GATEWAY_IP 2>/dev/null || echo "DNS query sent"
else
    echo "Could not determine gateway IP, skipping DNS test"
fi

echo "✅ Suspicious DNS queries sent"

echo ""
echo "🔍 Checking for detection results..."
echo "======================================"

# Wait a moment for processing
sleep 5

# Check for notice logs
if [ -f "zeek-logs/notice.log" ]; then
    echo "📋 Notice log found:"
    tail -10 zeek-logs/notice.log
else
    echo "⚠️  No notice.log file found yet"
fi

# Check recent HTTP logs
echo ""
echo "📋 Recent HTTP logs:"
if ls zeek-logs/http.*.log 1> /dev/null 2>&1; then
    tail -5 zeek-logs/http.*.log | grep -E "(UNION|DROP|INSERT|SELECT)" || echo "No SQL injection patterns found in HTTP logs yet"
else
    echo "No HTTP logs found"
fi

echo ""
echo "💡 Tips:"
echo "- Check the Kafka consumer in the web interface at http://localhost:8080"
echo "- Monitor zeek-logs/ directory for new notice.log files"
echo "- SQL injection detection should appear in HTTP logs and notices"
echo "- Port scan detection should appear in notice logs"
echo "- It may take a few moments for all events to be processed"

echo ""
echo "🔧 To restart Zeek with new configuration:"
echo "docker-compose restart zeek-live"
