#!/usr/bin/env python3
"""
Enhanced Network Traffic Generator with Virtual Interface Support
Supports realistic simulation scenarios on isolated virtual networks
"""

from scapy.all import *
import threading
import time
import os
import subprocess
from datetime import datetime
import random

class NetworkTrafficGenerator:
    def __init__(self):
        self.running = False
        self.thread = None
        self.available_interfaces = self.get_network_interfaces()
        self.network_info = self.discover_network_config()
        
    def get_network_interfaces(self):
        """Get list of available network interfaces, prioritizing virtual sim interfaces"""
        try:
            interfaces = get_if_list()
            
            # Prioritize simulation interfaces
            sim_interfaces = [iface for iface in interfaces if 'veth' in iface or 'br-zeek' in iface or 'tap-monitor' in iface]
            other_interfaces = [iface for iface in interfaces if not any(sim in iface for sim in ['veth', 'br-zeek', 'tap-monitor', 'lo', 'docker'])]
            
            # Return simulation interfaces first, then others
            return sim_interfaces + other_interfaces if sim_interfaces else other_interfaces
        except:
            return ['br-zeek-sim']  # fallback to our simulation bridge
    
    def discover_network_config(self):
        """Discover the container's network configuration"""
        network_info = {
            'subnet': '192.168.100.0/24',  # default fallback
            'gateway': '192.168.100.1',
            'container_ip': None,
            'network_base': '192.168.100'
        }
        
        try:
            # Try to get container's IP address
            import socket
            hostname = socket.gethostname()
            container_ip = socket.gethostbyname(hostname)
            network_info['container_ip'] = container_ip
            
            # Extract network base from container IP
            if container_ip and '.' in container_ip:
                ip_parts = container_ip.split('.')
                if len(ip_parts) >= 3:
                    network_base = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
                    network_info['network_base'] = network_base
                    network_info['subnet'] = f"{network_base}.0/24"
                    network_info['gateway'] = f"{network_base}.1"
                    
            print(f"Discovered network config: {network_info}")
            
        except Exception as e:
            print(f"Network discovery failed, using defaults: {e}")
            
        return network_info
    
    def get_random_ip_in_range(self, ip_range_start, ip_range_end):
        """Generate random IP in the discovered network range"""
        network_base = self.network_info['network_base']
        return f"{network_base}.{random.randint(ip_range_start, ip_range_end)}"
    
    def get_gateway_ip(self):
        """Get the network gateway IP"""
        return self.network_info['gateway']
    
    def generate_simulation_traffic(self, interface="br-zeek-sim", scenario="web_browsing", 
                                  duration=60, packets_per_second=5):
        """Generate realistic simulation scenarios on virtual interfaces"""
        self.running = True
        end_time = time.time() + duration
        packets_sent = 0
        
        print(f"Starting {scenario} simulation on interface: {interface}")
        
        while self.running and time.time() < end_time:
            try:
                if scenario == "web_browsing":
                    packet = self.create_web_browsing_traffic()
                elif scenario == "file_transfer":
                    packet = self.create_file_transfer_traffic()
                elif scenario == "video_streaming":
                    packet = self.create_video_streaming_traffic()
                elif scenario == "office_network":
                    packet = self.create_office_network_traffic()
                elif scenario == "malicious_activity":
                    packet = self.create_malicious_traffic()
                else:
                    packet = self.create_mixed_simulation_traffic()
                
                # Send packet - try interface-specific first, fallback to IP layer
                try:
                    # Try sending with specific interface first
                    sendp(packet, iface=interface, verbose=0)
                    packets_sent += 1
                except Exception as iface_error:
                    try:
                        # Fallback: send at IP layer (remove Ethernet header)
                        if packet.haslayer(Ether) and packet.haslayer(IP):
                            ip_packet = packet[IP]
                            send(ip_packet, verbose=0)
                            packets_sent += 1
                        else:
                            print(f"Packet format error: {iface_error}")
                    except Exception as send_error:
                        print(f"Send failed: {send_error}")
                
                # Variable delays for realistic timing
                delay = random.uniform(0.5, 2.0) / packets_per_second
                time.sleep(delay)
                
            except Exception as e:
                print(f"Error in simulation: {e}")
                break
        
        self.running = False
        print(f"Simulation complete: {packets_sent} packets sent")
        return packets_sent
    
    def create_web_browsing_traffic(self):
        """Create realistic web browsing patterns"""
        src_ip = self.get_random_ip_in_range(10, 19)
        dst_ip = self.get_random_ip_in_range(20, 29)
        
        traffic_types = ["http_get", "https_handshake", "dns_lookup", "http_post"]
        traffic_type = random.choice(traffic_types)
        
        if traffic_type == "http_get":
            pages = ["/index.html", "/about.html", "/products.html", "/contact.html"]
            page = random.choice(pages)
            payload = f"GET {page} HTTP/1.1\r\nHost: example.com\r\nUser-Agent: Mozilla/5.0\r\n\r\n"
            return Ether()/IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=80)/Raw(load=payload)
        
        elif traffic_type == "https_handshake":
            return Ether()/IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=443, flags="S")
        
        elif traffic_type == "dns_lookup":
            domains = ["example.com", "cdn.example.com", "api.example.com", "images.example.com"]
            domain = random.choice(domains)
            return Ether()/IP(src=src_ip, dst=self.get_gateway_ip())/UDP(sport=random.randint(1024, 65535), dport=53)/DNS(rd=1, qd=DNSQR(qname=domain))
        
        else:  # http_post
            payload = "POST /api/data HTTP/1.1\r\nHost: api.example.com\r\nContent-Length: 25\r\n\r\n{\"user\":\"demo\",\"data\":123}"
            return Ether()/IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=80)/Raw(load=payload)
    
    def create_file_transfer_traffic(self):
        """Create file transfer simulation (FTP, SFTP, etc.)"""
        src_ip = self.get_random_ip_in_range(10, 19)
        dst_ip = self.get_random_ip_in_range(20, 29)
        
        protocols = ["ftp_data", "ftp_control", "sftp", "scp"]
        protocol = random.choice(protocols)
        
        if protocol == "ftp_data":
            # Large data transfer simulation
            data_size = random.randint(500, 1400)
            payload = "A" * data_size  # Simulate file data
            return Ether()/IP(src=src_ip, dst=dst_ip)/TCP(sport=20, dport=random.randint(1024, 65535))/Raw(load=payload)
        
        elif protocol == "ftp_control":
            commands = ["USER demo", "PASS secret", "LIST", "RETR file.txt", "STOR upload.txt"]
            command = random.choice(commands)
            return Ether()/IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=21)/Raw(load=command + "\r\n")
        
        else:  # sftp/scp
            return Ether()/IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=22)
    
    def create_video_streaming_traffic(self):
        """Create video streaming simulation"""
        src_ip = self.get_random_ip_in_range(20, 29)  # Server
        dst_ip = self.get_random_ip_in_range(10, 19)  # Client
        
        # High bandwidth, consistent packets
        data_size = random.randint(800, 1400)
        payload = "VIDEO_DATA_" + "X" * (data_size - 11)
        
        return Ether()/IP(src=src_ip, dst=dst_ip)/UDP(sport=8080, dport=random.randint(1024, 65535))/Raw(load=payload)
    
    def create_office_network_traffic(self):
        """Create typical office network patterns"""
        src_ip = self.get_random_ip_in_range(10, 19)
        
        services = ["email", "file_share", "print", "web_proxy", "dhcp"]
        service = random.choice(services)
        
        if service == "email":
            dst_ip = self.get_random_ip_in_range(20, 29)
            protocols = [("smtp", 25), ("pop3", 110), ("imap", 143), ("smtps", 465)]
            protocol, port = random.choice(protocols)
            return Ether()/IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=port)
        
        elif service == "file_share":
            dst_ip = self.get_random_ip_in_range(20, 29)
            return Ether()/IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=445)  # SMB
        
        elif service == "print":
            dst_ip = self.get_random_ip_in_range(30, 39)  # Printer range
            return Ether()/IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=631)  # IPP
        
        elif service == "dhcp":
            return Ether()/IP(src="0.0.0.0", dst="255.255.255.255")/UDP(sport=68, dport=67)/Raw(load="DHCP_DISCOVER")
        
        else:  # web_proxy
            dst_ip = self.get_random_ip_in_range(20, 29)
            return Ether()/IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=8080)
    
    def create_malicious_traffic(self):
        """Create simulated malicious activity patterns (for IDS testing)"""
        src_ip = self.get_random_ip_in_range(100, 109)  # Suspicious source range
        dst_ip = self.get_random_ip_in_range(10, 29)
        
        attacks = ["port_scan", "brute_force", "suspicious_dns", "data_exfiltration"]
        attack = random.choice(attacks)
        
        if attack == "port_scan":
            # Rapid port scanning
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
            port = random.choice(ports)
            return Ether()/IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=port, flags="S")
        
        elif attack == "brute_force":
            # SSH brute force attempt
            return Ether()/IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=22)
        
        elif attack == "suspicious_dns":
            # DNS queries to suspicious domains
            domains = ["malware-c2.evil", "phishing.bad", "botnet.cmd"]
            domain = random.choice(domains)
            return Ether()/IP(src=src_ip, dst=self.get_gateway_ip())/UDP(sport=random.randint(1024, 65535), dport=53)/DNS(rd=1, qd=DNSQR(qname=domain))
        
        else:  # data_exfiltration
            # Large outbound data transfer
            data_size = random.randint(1000, 1400)
            payload = "EXFIL_DATA_" + "S" * (data_size - 11)
            return Ether()/IP(src=dst_ip, dst=src_ip)/TCP(sport=random.randint(1024, 65535), dport=443)/Raw(load=payload)
    
    def create_mixed_simulation_traffic(self):
        """Create mixed realistic traffic"""
        scenarios = ["web_browsing", "file_transfer", "video_streaming", "office_network"]
        scenario = random.choice(scenarios)
        
        if scenario == "web_browsing":
            return self.create_web_browsing_traffic()
        elif scenario == "file_transfer":
            return self.create_file_transfer_traffic()
        elif scenario == "video_streaming":
            return self.create_video_streaming_traffic()
        else:
            return self.create_office_network_traffic()
    
    def generate_traffic_to_interface(self, interface="br-zeek-sim", traffic_type="mixed", 
                                    target_ip="192.168.200.20", duration=60, 
                                    packets_per_second=2, save_pcap=False):
        """Generate traffic and send to specific network interface"""
        self.running = True
        end_time = time.time() + duration
        packets_sent = 0
        
        print(f"Starting traffic generation on interface: {interface}")
        print(f"Target: {target_ip}, Type: {traffic_type}, Duration: {duration}s, Rate: {packets_per_second} pps")
        
        while self.running and time.time() < end_time:
            try:
                packet = self.create_packet(traffic_type, target_ip)
                
                # Send to specific interface
                sendp(packet, iface=interface, verbose=0)
                packets_sent += 1
                
                time.sleep(1.0 / packets_per_second)
                
            except Exception as e:
                print(f"Error sending packet: {e}")
                break
        
        self.running = False
        print(f"Traffic generation complete. Sent {packets_sent} packets.")
        return packets_sent
    
    def generate_namespace_traffic(self, interface, traffic_type, duration=60, packets_per_second=2):
        """Generate traffic within network namespaces for complete isolation"""
        self.running = True
        end_time = time.time() + duration
        packets_sent = 0
        
        print(f"Generating namespace traffic: {traffic_type} for {duration}s")
        
        # Use ip netns exec to run traffic generation in isolated namespace
        namespaces = ["sim-client", "sim-server"]
        
        try:
            while self.running and time.time() < end_time:
                for ns in namespaces:
                    if not self.running:
                        break
                        
                    # Generate traffic from within namespace
                    if traffic_type == "ping":
                        cmd = f"ip netns exec {ns} ping -c 1 -W 1 192.168.200.{20 if ns == 'sim-client' else 10} >/dev/null 2>&1"
                    elif traffic_type == "http":
                        target = "192.168.200.20" if ns == "sim-client" else "192.168.200.10"
                        # Use netcat to simulate HTTP
                        cmd = f"ip netns exec {ns} echo 'GET / HTTP/1.1' | nc -w 1 {target} 80 >/dev/null 2>&1"
                    else:
                        # Generate mixed traffic using scapy within namespace
                        packet = self.create_packet(traffic_type, "192.168.200.20")
                        sendp(packet, iface=interface, verbose=0)
                        packets_sent += 1
                        continue
                    
                    try:
                        subprocess.run(cmd, shell=True, timeout=2)
                        packets_sent += 1
                    except:
                        pass
                
                time.sleep(1.0 / packets_per_second)
                
        except Exception as e:
            print(f"Namespace traffic error: {e}")
        
        self.running = False
        print(f"Namespace traffic complete: {packets_sent} operations")
        return packets_sent
    
    def create_packet(self, traffic_type, target_ip):
        """Create different types of network packets"""
        src_ip = self.get_random_source_ip()
        
        if traffic_type == "http":
            return self.create_http_packet(src_ip, target_ip)
        elif traffic_type == "dns":
            return self.create_dns_packet(src_ip, target_ip)
        elif traffic_type == "icmp":
            return self.create_icmp_packet(src_ip, target_ip)
        elif traffic_type == "tcp_syn":
            return self.create_tcp_syn_packet(src_ip, target_ip)
        else:  # mixed
            packet_types = ["http", "dns", "icmp", "tcp_syn"]
            return self.create_packet(random.choice(packet_types), target_ip)
    
    def create_http_packet(self, src_ip, target_ip):
        """Create HTTP GET request packet"""
        src_port = random.randint(1024, 65535)
        http_payload = "GET /index.html HTTP/1.1\r\nHost: example.com\r\nUser-Agent: ScapyTrafficGen/1.0\r\n\r\n"
        return Ether()/IP(src=src_ip, dst=target_ip)/TCP(sport=src_port, dport=80)/Raw(load=http_payload)
    
    def create_dns_packet(self, src_ip, target_ip):
        """Create DNS query packet"""
        domains = ["example.com", "google.com", "github.com", "stackoverflow.com", "wikipedia.org"]
        domain = random.choice(domains)
        return Ether()/IP(src=src_ip, dst=target_ip)/UDP(sport=random.randint(1024, 65535), dport=53)/DNS(rd=1, qd=DNSQR(qname=domain))
    
    def create_icmp_packet(self, src_ip, target_ip):
        """Create ICMP ping packet"""
        return Ether()/IP(src=src_ip, dst=target_ip)/ICMP()
    
    def create_tcp_syn_packet(self, src_ip, target_ip):
        """Create TCP SYN packet"""
        ports = [22, 80, 443, 993, 995, 8080, 3389]
        return Ether()/IP(src=src_ip, dst=target_ip)/TCP(sport=random.randint(1024, 65535), dport=random.choice(ports), flags="S")
    
    def get_random_source_ip(self):
        """Generate random source IP from discovered network range"""
        return self.get_random_ip_in_range(10, 50)
    
    def capture_interface_traffic(self, interface, filename, duration=60, filter_expr=""):
        """Capture real traffic from an interface"""
        print(f"Starting capture on {interface} for {duration} seconds")
        
        # Use tcpdump for reliable capture
        cmd = ['tcpdump', '-i', interface, '-s', '0', '-w', f'/output/{filename}']
        
        if filter_expr:
            cmd.append(filter_expr)
        
        try:
            # Start tcpdump process
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for specified duration
            time.sleep(duration)
            
            # Terminate tcpdump
            process.terminate()
            process.wait(timeout=5)
            
            print(f"Capture complete: {filename}")
            return True
            
        except Exception as e:
            print(f"Capture failed: {e}")
            return False
    
    def list_interfaces_with_stats(self):
        """List all available interfaces with current statistics"""
        interfaces_info = []
        
        for iface in self.available_interfaces:
            stats = self.get_interface_stats(iface)
            info = {
                'name': iface,
                'stats': stats,
                'is_up': self.is_interface_up(iface)
            }
            interfaces_info.append(info)
        
        return interfaces_info
    
    def get_interface_stats(self, interface):
        """Get interface packet statistics"""
        try:
            with open(f'/sys/class/net/{interface}/statistics/rx_packets', 'r') as f:
                rx_packets = int(f.read().strip())
            with open(f'/sys/class/net/{interface}/statistics/tx_packets', 'r') as f:
                tx_packets = int(f.read().strip())
            return {'rx_packets': rx_packets, 'tx_packets': tx_packets}
        except:
            return {'rx_packets': 0, 'tx_packets': 0}
    
    def is_interface_up(self, interface):
        """Check if interface is up"""
        try:
            with open(f'/sys/class/net/{interface}/operstate', 'r') as f:
                state = f.read().strip()
            return state == 'up'
        except:
            return False
