# Developer Guide

```bash
docker inspect --format "{{json .State.Health }}" <container name>
```

# List open (listening) TCP ports
```bash
awk '$4 == "0A" { printf "TCP Port: "; system("echo $((0x" substr($2,10,4) "))") }' /proc/net/tcp
```

# List open (listening) UDP ports
```bash
awk '$4 == "0A" { printf "UDP Port: "; system("echo $((0x" substr($2,10,4) "))") }' /proc/net/udp
```
