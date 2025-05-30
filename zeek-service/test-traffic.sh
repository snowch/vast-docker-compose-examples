#!/bin/bash

echo "🧪 Testing Zeek Traffic Monitoring"
echo "=================================="

echo ""
echo "1. Testing external traffic to web server (should be captured by Zeek)..."
curl -s http://localhost:8081 > /dev/null
echo "✅ HTTP request to web server completed"

echo ""
echo "2. Testing traffic to traffic simulator..."
curl -s http://localhost:8080 > /dev/null
echo "✅ HTTP request to traffic simulator completed"

echo ""
echo "3. Waiting 5 seconds for Zeek to process..."
sleep 5

echo ""
echo "4. Checking Zeek logs..."
if [ -d "zeek-logs" ] && [ "$(ls -A zeek-logs)" ]; then
    echo "✅ Zeek log files found:"
    ls -la zeek-logs/
    echo ""
    echo "📊 Connection logs:"
    if [ -f "zeek-logs/conn.log" ]; then
        tail -5 zeek-logs/conn.log
    else
        echo "No conn.log file yet"
    fi
else
    echo "⚠️  No Zeek log files found yet"
fi

echo ""
echo "5. Checking Zeek container logs..."
docker compose logs zeek-live --tail=10
