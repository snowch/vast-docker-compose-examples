# Simplified Zeek Network Monitoring Service

A simplified Docker-based Zeek network monitoring setup that uses container default network interfaces instead of complex virtual networking.

## 🚀 Quick Start

```bash
# Build and start the simplified monitoring setup
docker compose up --build

# View Zeek logs
docker compose logs -f zeek-live

# Stop all services
docker compose down
```

## 📋 What's Included

### Services

1. **zeek-live** - Zeek network monitoring container
   - Monitors traffic on container's `eth0` interface
   - Sends logs to Kafka (if configured)
   - Uses Docker bridge networking

2. **traffic-simulator** - Traffic generation container
   - Generates network traffic for testing
   - Available on port 8080

3. **web-server** - Simple nginx test server
   - Generates HTTP traffic for monitoring
   - Available on port 8081
   - Interactive web interface for traffic generation

### Network Architecture

```
┌─────────────────────────────────────────────────────────┐
│                Docker Bridge Network                    │
│                   (zeek-network)                        │
│                  172.20.0.0/16                         │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │    Zeek     │  │   Traffic   │  │ Web Server  │     │
│  │  Monitor    │  │ Simulator   │  │   (nginx)   │     │
│  │   (eth0)    │  │             │  │             │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                         │
└─────────────────────────────────────────────────────────┘
                           │
                    ┌─────────────┐
                    │ Host System │
                    │ Port 8080   │ ← Traffic Simulator
                    │ Port 8081   │ ← Web Server
                    └─────────────┘
```

## 🔧 Configuration

### Environment Variables

- `KAFKA_BROKER` - Kafka broker address (default: 172.200.204.1:9092)
- `KAFKA_TOPIC` - Kafka topic name (default: zeek-live-logs)
- `MONITOR_INTERFACE` - Network interface to monitor (default: eth0)

### Key Simplifications

**Before (Complex Setup):**
- Custom bridge networks (`br-zeek-sim`)
- Network namespaces
- Multiple veth pairs
- Host networking mode
- Complex virtual network setup script

**After (Simplified Setup):**
- Standard Docker bridge network
- Container's default `eth0` interface
- No custom network namespaces
- Standard Docker networking
- Automatic traffic capture between containers

## 📊 Monitoring Traffic

### What Zeek Monitors

Zeek monitors all traffic between containers in the `zeek-network`:
- HTTP requests/responses
- DNS queries
- SSL/TLS connections
- SSH connections
- FTP transfers
- SMTP traffic

### Generating Test Traffic

1. **Web Interface**: Visit http://localhost:8081
   - Click buttons to generate different types of HTTP traffic
   - Automatic traffic generation every 30 seconds

2. **Traffic Simulator**: Available on http://localhost:8080
   - Programmatic traffic generation
   - Custom traffic patterns

3. **Container-to-Container**: All communication between containers is monitored

## 📁 Directory Structure

```
zeek-service/
├── docker-compose.yml          # Simplified Docker Compose configuration
├── Dockerfile                  # Zeek container with Kafka plugin
├── Dockerfile.scapy           # Traffic simulator container
├── scripts/
│   └── monitor-live.sh        # Simplified monitoring script
├── zeek-config/
│   ├── kafka-live.zeek        # Zeek configuration for live monitoring
│   └── kafka-pcap.zeek        # Zeek configuration for PCAP analysis
├── zeek-logs/                 # Zeek output logs
├── traffic-scripts/           # Traffic generation scripts
├── web-content/               # Test web server content
└── README.md                  # This file
```

## 🔍 Viewing Logs

### Container Logs
```bash
# View Zeek monitoring logs
docker compose logs -f zeek-live

# View traffic simulator logs
docker compose logs -f traffic-simulator

# View web server logs
docker compose logs -f web-server
```

### Zeek Output Files
```bash
# View Zeek logs directory
ls -la zeek-logs/

# View connection logs
cat zeek-logs/conn.log

# View HTTP logs
cat zeek-logs/http.log
```

## 🛠️ Troubleshooting

### Common Issues

1. **Interface not found**
   ```bash
   # Check available interfaces in container
   docker exec zeek-live-monitor ip link show
   ```

2. **No traffic captured**
   - Ensure containers are in the same network
   - Check if traffic is being generated
   - Verify Zeek is monitoring the correct interface

3. **Kafka connection issues**
   - Check Kafka broker address
   - Verify Kafka is running and accessible
   - Zeek will continue monitoring even without Kafka

### Debug Commands

```bash
# Check network configuration
docker network ls
docker network inspect zeek-service_zeek-network

# Check container networking
docker exec zeek-live-monitor ip addr show
docker exec zeek-live-monitor ip route show

# Test connectivity between containers
docker exec traffic-simulator ping web-server
```

## 🔄 Migration from Complex Setup

If migrating from the previous complex virtual network setup:

1. **Backup existing logs**: `cp -r zeek-logs zeek-logs.backup`
2. **Stop old setup**: `docker compose down`
3. **Update configuration**: Use the new simplified `docker-compose.yml`
4. **Start new setup**: `docker compose up --build`

### Benefits of Simplified Setup

- ✅ Easier to understand and maintain
- ✅ Standard Docker networking
- ✅ No complex virtual network scripts
- ✅ Faster startup time
- ✅ Better container isolation
- ✅ Easier debugging and troubleshooting
- ✅ More portable across different environments

## 📚 Additional Resources

- [Zeek Documentation](https://docs.zeek.org/)
- [Zeek-Kafka Plugin](https://github.com/SeisoLLC/zeek-kafka)
- [Docker Networking](https://docs.docker.com/network/)
