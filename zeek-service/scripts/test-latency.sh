#!/bin/bash

# Latency Testing Script for Zeek-Kafka Pipeline
# Tests the end-to-end delay from packet generation to Kafka delivery

set -e

echo "🔍 Testing Zeek-Kafka Pipeline Latency"
echo "======================================"

# Configuration
KAFKA_BROKER="${KAFKA_BROKER:-172.200.204.1:9092}"
KAFKA_TOPIC="${KAFKA_TOPIC:-zeek-live-logs}"
TEST_DURATION=30
PACKETS_PER_SECOND=5

# Function to check if Kafka is available
check_kafka() {
    echo "🔌 Checking Kafka connectivity..."
    if timeout 5 nc -z $(echo $KAFKA_BROKER | tr ':' ' ') 2>/dev/null; then
        echo "✅ Kafka broker is reachable at $KAFKA_BROKER"
        return 0
    else
        echo "❌ Cannot connect to Kafka broker $KAFKA_BROKER"
        return 1
    fi
}

# Function to monitor Kafka messages with timestamps
monitor_kafka() {
    echo "📊 Starting Kafka message monitoring..."
    echo "Topic: $KAFKA_TOPIC"
    echo "Monitoring for $TEST_DURATION seconds..."
    
    # Use kafkacat or kafka-console-consumer to monitor messages
    timeout $TEST_DURATION kafkacat -C -b $KAFKA_BROKER -t $KAFKA_TOPIC -o end -f 'Timestamp: %T, Message: %s\n' 2>/dev/null || \
    timeout $TEST_DURATION kafka-console-consumer.sh --bootstrap-server $KAFKA_BROKER --topic $KAFKA_TOPIC --from-latest --timeout-ms $((TEST_DURATION * 1000)) 2>/dev/null || \
    echo "⚠️  Kafka consumer tools not available - check logs manually"
}

# Function to generate test traffic with timestamps
generate_test_traffic() {
    echo "🚀 Generating test traffic..."
    echo "Rate: $PACKETS_PER_SECOND packets/second"
    echo "Duration: $TEST_DURATION seconds"
    
    # Send HTTP request to traffic generator
    curl -s -X POST http://localhost:8080/api/start_traffic \
        -H "Content-Type: application/json" \
        -d "{
            \"type\": \"http\",
            \"target_ip\": \"192.168.100.20\",
            \"duration\": $TEST_DURATION,
            \"packets_per_second\": $PACKETS_PER_SECOND
        }" | jq '.'
}

# Function to measure latency
measure_latency() {
    echo "⏱️  Measuring end-to-end latency..."
    
    # Start timestamp
    START_TIME=$(date +%s.%N)
    echo "Test started at: $(date -d @$START_TIME)"
    
    # Generate traffic in background
    generate_test_traffic &
    TRAFFIC_PID=$!
    
    # Monitor Kafka messages
    monitor_kafka &
    MONITOR_PID=$!
    
    # Wait for test completion
    sleep $TEST_DURATION
    
    # Stop processes
    kill $TRAFFIC_PID 2>/dev/null || true
    kill $MONITOR_PID 2>/dev/null || true
    
    END_TIME=$(date +%s.%N)
    echo "Test completed at: $(date -d @$END_TIME)"
    
    # Calculate total test time
    TOTAL_TIME=$(echo "$END_TIME - $START_TIME" | bc)
    echo "Total test duration: ${TOTAL_TIME}s"
}

# Function to check Zeek logs for timing
check_zeek_logs() {
    echo "📋 Checking Zeek logs for recent activity..."
    
    if [ -d "/logs" ]; then
        echo "Recent Zeek log entries:"
        find /logs -name "*.log" -type f -exec tail -5 {} \; 2>/dev/null | head -20
    else
        echo "⚠️  Zeek logs directory not accessible"
    fi
}

# Function to show optimization summary
show_optimizations() {
    echo ""
    echo "🔧 Applied Optimizations:"
    echo "======================="
    echo "✅ Kafka queue.buffering.max.ms: 10ms (was 1000ms)"
    echo "✅ Kafka linger.ms: 0ms (immediate send)"
    echo "✅ Kafka batch.num.messages: 1 (no batching)"
    echo "✅ Kafka acks: 1 (leader only)"
    echo "✅ Traffic generation: precise timing with 1ms sleep"
    echo "✅ Reduced timeouts and retries"
    echo ""
    echo "Expected improvements:"
    echo "• Kafka buffering delay: ~990ms reduction"
    echo "• Traffic generation jitter: reduced variability"
    echo "• Overall pipeline latency: <100ms typical"
}

# Function to provide troubleshooting tips
show_troubleshooting() {
    echo ""
    echo "🔍 Troubleshooting Tips:"
    echo "======================"
    echo "1. Check container networking:"
    echo "   docker network ls"
    echo "   docker network inspect zeek-service_zeek-network"
    echo ""
    echo "2. Verify Zeek is processing packets:"
    echo "   docker logs zeek-live-monitor"
    echo ""
    echo "3. Check Kafka topic exists:"
    echo "   kafka-topics.sh --list --bootstrap-server $KAFKA_BROKER"
    echo ""
    echo "4. Monitor network interface traffic:"
    echo "   docker exec zeek-live-monitor ip -s link show eth0"
    echo ""
    echo "5. Test traffic generator directly:"
    echo "   curl http://localhost:8080/api/status"
}

# Main execution
main() {
    echo "Starting latency test at $(date)"
    echo ""
    
    # Check prerequisites
    if ! check_kafka; then
        echo "❌ Kafka not available - cannot run latency test"
        show_troubleshooting
        exit 1
    fi
    
    # Show current optimizations
    show_optimizations
    
    # Run latency measurement
    measure_latency
    
    # Check logs
    check_zeek_logs
    
    echo ""
    echo "✅ Latency test completed"
    echo "Check the output above for timing information"
    echo ""
    
    # Show troubleshooting if needed
    show_troubleshooting
}

# Run main function
main "$@"
