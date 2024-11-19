# Developer Guide

```bash
# Healthcheck logs
docker inspect --format "{{json .State.Health }}" <container name>
```


```bash
# List open (listening) TCP ports
awk '$4 == "0A" { printf "TCP Port: "; system("echo $((0x" substr($2,10,4) "))") }' /proc/net/tcp
```

```bash
# List open (listening) UDP ports
awk '$4 == "0A" { printf "UDP Port: "; system("echo $((0x" substr($2,10,4) "))") }' /proc/net/udp
```
