# Zeek-Kafka Pipeline Latency Optimization

## Problem
The original setup had significant delays (many seconds) between simulated traffic events and their appearance in Kafka. This was caused by multiple bottlenecks in the pipeline.

## Root Causes Identified

### 1. Kafka Producer Buffering (Major Impact)
- **Original**: `queue.buffering.max.ms = 1000` (1 second buffer)
- **Impact**: Up to 1 second delay before messages are sent to Kafka
- **Solution**: Reduced to `10ms` for near-immediate delivery

### 2. Kafka Batching Delays
- **Original**: Default batching behavior with `linger.ms` not set
- **Impact**: Producer waits to batch messages, adding latency
- **Solution**: Set `linger.ms = 0` for immediate sending

### 3. Traffic Generation Timing Issues
- **Original**: Variable delays with `random.uniform(0.5, 2.0)` and simple `time.sleep()`
- **Impact**: Inconsistent packet timing and potential bursts
- **Solution**: Precise timing with scheduled packet intervals

### 4. Network Acknowledgment Delays
- **Original**: Default acknowledgment settings
- **Impact**: Waiting for full cluster acknowledgment
- **Solution**: Set `acks = 1` (leader only) for faster acknowledgment

## Applied Optimizations

### Kafka Configuration Changes
```zeek
redef Kafka::kafka_conf = table(
    ["metadata.broker.list"] = "172.200.204.1:9092",
    ["client.id"] = "zeek-live-monitor",
    ["batch.num.messages"] = "1",           # No batching
    ["queue.buffering.max.ms"] = "10",      # 10ms buffer (was 1000ms)
    ["linger.ms"] = "0",                    # Send immediately
    ["acks"] = "1",                         # Leader acknowledgment only
    ["retries"] = "3",                      # Limited retries
    ["delivery.timeout.ms"] = "5000",       # Faster timeout
    ["request.timeout.ms"] = "2000",        # Faster request timeout
    ["socket.timeout.ms"] = "1000",         # Faster socket timeout
    ["debug"] = "broker,topic,msg",
    ["log_level"] = "7"
);
```

### Traffic Generation Improvements
```python
def generate_http_traffic(self, target_ip="192.168.200.20", duration=60, packets_per_second=1):
    """Generate simulated HTTP traffic with precise timing"""
    self.running = True
    start_time = time.time()
    end_time = start_time + duration
    packet_interval = 1.0 / packets_per_second
    next_packet_time = start_time
    
    while self.running and time.time() < end_time:
        current_time = time.time()
        if current_time >= next_packet_time:
            # Send packet
            packet = IP(dst=target_ip)/TCP(dport=80, sport=src_port)/Raw(load="GET / HTTP/1.1\r\n...")
            send(packet, verbose=0)
            
            # Schedule next packet with precise timing
            next_packet_time += packet_interval
        
        # Small sleep to prevent busy waiting
        time.sleep(0.001)
```

## Expected Performance Improvements

### Latency Reduction
- **Kafka buffering**: ~990ms reduction (1000ms → 10ms)
- **Message batching**: ~50-200ms reduction (immediate vs batched)
- **Traffic timing**: More consistent, predictable intervals
- **Overall pipeline**: <100ms typical latency (was >1000ms)

### Throughput Impact
- **Pros**: Lower latency, more responsive
- **Cons**: Slightly higher CPU usage due to more frequent sends
- **Net**: Better for real-time monitoring scenarios

## Testing the Optimizations

### Automated Testing
Run the latency test script:
```bash
./scripts/test-latency.sh
```

### Manual Verification
1. **Start the services**:
   ```bash
   docker-compose up -d
   ```

2. **Generate test traffic**:
   ```bash
   curl -X POST http://localhost:8080/api/start_traffic \
     -H "Content-Type: application/json" \
     -d '{"type": "http", "duration": 30, "packets_per_second": 2}'
   ```

3. **Monitor Kafka messages** (if tools available):
   ```bash
   kafkacat -C -b 172.200.204.1:9092 -t zeek-live-logs -o end
   ```

4. **Check Zeek logs**:
   ```bash
   docker logs zeek-live-monitor
   ```

## Monitoring and Troubleshooting

### Key Metrics to Watch
- **Kafka producer metrics**: delivery latency, batch size
- **Zeek processing**: packet capture rate, log generation
- **Network interface**: packet counts, drops
- **Container resources**: CPU, memory usage

### Common Issues and Solutions

#### High CPU Usage
- **Cause**: Frequent small sends to Kafka
- **Solution**: Slightly increase `queue.buffering.max.ms` (e.g., to 50ms)

#### Message Loss
- **Cause**: Aggressive timeout settings
- **Solution**: Increase `delivery.timeout.ms` and `retries`

#### Network Congestion
- **Cause**: High packet rate overwhelming interface
- **Solution**: Reduce `packets_per_second` in traffic generation

#### Kafka Connection Issues
- **Cause**: Network connectivity or broker problems
- **Solution**: Check broker status, network routing, firewall rules

## Configuration Tuning

### For Ultra-Low Latency (<10ms)
```zeek
["queue.buffering.max.ms"] = "1",
["socket.timeout.ms"] = "500",
["request.timeout.ms"] = "1000",
```

### For High Throughput (with some latency tolerance)
```zeek
["queue.buffering.max.ms"] = "100",
["batch.num.messages"] = "10",
["linger.ms"] = "50",
```

### For Balanced Performance
```zeek
["queue.buffering.max.ms"] = "10",    # Current setting
["linger.ms"] = "0",
["acks"] = "1",
```

## Validation Checklist

- [ ] Kafka configuration updated with optimized settings
- [ ] Traffic generation uses precise timing
- [ ] Test script runs successfully
- [ ] Latency reduced from seconds to sub-second
- [ ] No message loss during testing
- [ ] CPU usage remains acceptable
- [ ] Network interface handles traffic load

## Next Steps

1. **Deploy optimizations**: Restart containers with new configuration
2. **Run baseline test**: Use `./scripts/test-latency.sh` to measure improvements
3. **Monitor production**: Watch for any performance regressions
4. **Fine-tune**: Adjust settings based on actual traffic patterns
5. **Document results**: Record actual latency measurements for future reference

## Rollback Plan

If optimizations cause issues:

1. **Revert Kafka settings**:
   ```zeek
   ["queue.buffering.max.ms"] = "1000",
   # Remove linger.ms, acks, timeout overrides
   ```

2. **Revert traffic generation**:
   ```python
   time.sleep(1.0 / packets_per_second)  # Simple sleep
   ```

3. **Restart services**:
   ```bash
   docker-compose restart
