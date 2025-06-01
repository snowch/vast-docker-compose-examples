#!/usr/bin/env python3
"""
Enhanced Network Traffic Generator that creates real network connections
This ensures Zeek can properly monitor and analyze the traffic
"""

import socket
import threading
import time
import random
import subprocess
from datetime import datetime
import json

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests module not available. HTTP traffic will use raw sockets.")

class EnhancedTrafficGenerator:
    def __init__(self):
        self.running = False
        self.threads = []
        
    def generate_real_http_traffic(self, target_ip="192.168.100.2", duration=60, requests_per_second=2):
        """Generate real HTTP requests that create actual network connections"""
        self.running = True
        start_time = time.time()
        end_time = start_time + duration
        request_interval = 1.0 / requests_per_second
        next_request_time = start_time
        
        print(f"Generating real HTTP traffic to {target_ip} for {duration}s")
        
        # URLs to request
        urls = [
            f"http://{target_ip}:8082/",
            f"http://{target_ip}:8082/index.html",
            f"http://{target_ip}:8082/about.html",
            f"http://{target_ip}:8082/products.html",
            f"http://{target_ip}:8082/api/data",
            f"http://{target_ip}:8082/login",
            f"http://{target_ip}:8082/search?q=test"
        ]
        
        while self.running and time.time() < end_time:
            try:
                current_time = time.time()
                if current_time >= next_request_time:
                    url = random.choice(urls)
                    if REQUESTS_AVAILABLE:
                        try:
                            # Make actual HTTP request with short timeout
                            response = requests.get(url, timeout=2)
                            print(f"HTTP request to {url} - Status: {response.status_code}")
                        except requests.exceptions.RequestException as e:
                            print(f"HTTP request to {url} - Error: {e}")
                    else:
                        # Fallback to raw socket HTTP request
                        try:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(2)
                            sock.connect((target_ip, 8082))
                            http_request = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\n\r\n"
                            sock.send(http_request.encode())
                            sock.close()
                            print(f"HTTP request to {url} - Raw socket connection")
                        except Exception as e:
                            print(f"HTTP request to {url} - Socket error: {e}")
                    
                    next_request_time += request_interval
                
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in HTTP traffic generation: {e}")
                break
        
        self.running = False
        print("HTTP traffic generation completed")
    
    def generate_malicious_http_traffic(self, target_ip="192.168.100.2", duration=60, requests_per_second=1):
        """Generate HTTP requests with malicious patterns for detection testing"""
        self.running = True
        start_time = time.time()
        end_time = start_time + duration
        request_interval = 1.0 / requests_per_second
        next_request_time = start_time
        
        print(f"Generating malicious HTTP traffic to {target_ip} for {duration}s")
        
        # Malicious URLs that should trigger Zeek detection - using port 8082 (zeek-live exposed port)
        malicious_urls = [
            f"http://{target_ip}:8082/login?user=admin&pass=' UNION SELECT * FROM users--",
            f"http://{target_ip}:8082/search?q=' DROP TABLE users--",
            f"http://{target_ip}:8082/api/data?id=1' INSERT INTO admin VALUES('hacker')--",
            f"http://{target_ip}:8082/admin?cmd=cat /etc/passwd",
            f"http://{target_ip}:8082/upload?file=../../../etc/shadow",
            f"http://{target_ip}:8082/debug?eval=system('whoami')",
            f"http://{target_ip}:8082/app?q=SELECT password FROM users WHERE id=1",
            f"http://{target_ip}:8082/search?term=<script>alert('xss')</script>"
        ]
        
        while self.running and time.time() < end_time:
            try:
                current_time = time.time()
                if current_time >= next_request_time:
                    url = random.choice(malicious_urls)
                    if REQUESTS_AVAILABLE:
                        try:
                            response = requests.get(url, timeout=2)
                            print(f"Malicious HTTP request to {url} - Status: {response.status_code}")
                        except requests.exceptions.RequestException as e:
                            print(f"Malicious HTTP request to {url} - Error: {e}")
                    else:
                        # Fallback to raw socket HTTP request
                        try:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(2)
                            sock.connect((target_ip, 8082))
                            # Extract path from URL
                            path = url.split(':8082')[1] if ':8082' in url else '/'
                            http_request = f"GET {path} HTTP/1.1\r\nHost: {target_ip}\r\n\r\n"
                            sock.send(http_request.encode())
                            sock.close()
                            print(f"Malicious HTTP request to {url} - Raw socket connection")
                        except Exception as e:
                            print(f"Malicious HTTP request to {url} - Socket error: {e}")
                    
                    next_request_time += request_interval
                
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in malicious HTTP traffic generation: {e}")
                break
        
        self.running = False
        print("Malicious HTTP traffic generation completed")
    
    def generate_real_dns_traffic(self, dns_server="192.168.100.1", duration=60, queries_per_second=2):
        """Generate real DNS queries"""
        self.running = True
        start_time = time.time()
        end_time = start_time + duration
        query_interval = 1.0 / queries_per_second
        next_query_time = start_time
        
        print(f"Generating real DNS traffic to {dns_server} for {duration}s")
        
        # Mix of normal and suspicious domains
        domains = [
            "google.com",
            "github.com",
            "stackoverflow.com",
            "example.com",
            "wikipedia.org",
            "malware-c2.evil",  # Suspicious domain
            "phishing.bad",     # Suspicious domain
            "botnet.cmd",       # Suspicious domain
            "data-exfil.evil"   # Suspicious domain
        ]
        
        while self.running and time.time() < end_time:
            try:
                current_time = time.time()
                if current_time >= next_query_time:
                    domain = random.choice(domains)
                    try:
                        # Create simple DNS query packet manually
                        # DNS header: ID(2) + Flags(2) + QDCOUNT(2) + ANCOUNT(2) + NSCOUNT(2) + ARCOUNT(2)
                        dns_id = random.randint(1, 65535)
                        header = dns_id.to_bytes(2, 'big') + b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
                        
                        # DNS question: domain name + type(2) + class(2)
                        question = b''
                        for part in domain.split('.'):
                            question += len(part).to_bytes(1, 'big') + part.encode()
                        question += b'\x00\x00\x01\x00\x01'  # A record, IN class
                        
                        dns_packet = header + question
                        
                        # Send DNS query using socket
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.settimeout(2)
                        sock.sendto(dns_packet, (dns_server, 53))
                        
                        # Try to receive response
                        try:
                            response_data, addr = sock.recvfrom(512)
                            print(f"DNS query for {domain} - Response received")
                        except socket.timeout:
                            print(f"DNS query for {domain} - Timeout")
                        
                        sock.close()
                        
                    except Exception as e:
                        print(f"DNS query for {domain} - Error: {e}")
                    
                    next_query_time += query_interval
                
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in DNS traffic generation: {e}")
                break
        
        self.running = False
        print("DNS traffic generation completed")
    
    def generate_port_scan_traffic(self, target_ip="192.168.100.2", duration=30, scan_rate=5):
        """Generate port scanning traffic that should trigger Zeek detection"""
        self.running = True
        start_time = time.time()
        end_time = start_time + duration
        scan_interval = 1.0 / scan_rate
        next_scan_time = start_time
        
        print(f"Generating port scan traffic against {target_ip} for {duration}s")
        
        # Common ports to scan
        ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306, 1433, 6379, 27017]
        
        while self.running and time.time() < end_time:
            try:
                current_time = time.time()
                if current_time >= next_scan_time:
                    port = random.choice(ports)
                    try:
                        # Attempt TCP connection (SYN scan simulation)
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)
                        result = sock.connect_ex((target_ip, port))
                        sock.close()
                        
                        if result == 0:
                            print(f"Port scan: {target_ip}:{port} - OPEN")
                        else:
                            print(f"Port scan: {target_ip}:{port} - CLOSED/FILTERED")
                            
                    except Exception as e:
                        print(f"Port scan: {target_ip}:{port} - Error: {e}")
                    
                    next_scan_time += scan_interval
                
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in port scan traffic generation: {e}")
                break
        
        self.running = False
        print("Port scan traffic generation completed")
    
    def generate_ssh_brute_force_traffic(self, target_ip="192.168.100.2", duration=30, attempts_per_second=2):
        """Generate SSH brute force attempts"""
        self.running = True
        start_time = time.time()
        end_time = start_time + duration
        attempt_interval = 1.0 / attempts_per_second
        next_attempt_time = start_time
        
        print(f"Generating SSH brute force traffic against {target_ip} for {duration}s")
        
        # Common username/password combinations
        credentials = [
            ("admin", "admin"),
            ("root", "root"),
            ("admin", "password"),
            ("user", "user"),
            ("admin", "123456"),
            ("root", "toor"),
            ("guest", "guest"),
            ("test", "test")
        ]
        
        while self.running and time.time() < end_time:
            try:
                current_time = time.time()
                if current_time >= next_attempt_time:
                    username, password = random.choice(credentials)
                    try:
                        # Simulate SSH connection attempt
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2)
                        result = sock.connect_ex((target_ip, 22))
                        
                        if result == 0:
                            # Send some data to simulate SSH handshake
                            sock.send(b"SSH-2.0-OpenSSH_7.4\r\n")
                            print(f"SSH brute force attempt: {username}:{password} - Connection established")
                        else:
                            print(f"SSH brute force attempt: {username}:{password} - Connection failed")
                        
                        sock.close()
                        
                    except Exception as e:
                        print(f"SSH brute force attempt: {username}:{password} - Error: {e}")
                    
                    next_attempt_time += attempt_interval
                
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in SSH brute force traffic generation: {e}")
                break
        
        self.running = False
        print("SSH brute force traffic generation completed")
    
    def generate_data_exfiltration_traffic(self, target_ip="192.168.100.2", duration=30, transfers_per_second=1):
        """Generate data exfiltration simulation"""
        self.running = True
        start_time = time.time()
        end_time = start_time + duration
        transfer_interval = 1.0 / transfers_per_second
        next_transfer_time = start_time
        
        print(f"Generating data exfiltration traffic to {target_ip} for {duration}s")
        
        while self.running and time.time() < end_time:
            try:
                current_time = time.time()
                if current_time >= next_transfer_time:
                    try:
                        # Simulate large data transfer over HTTPS
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2)
                        result = sock.connect_ex((target_ip, 443))
                        
                        if result == 0:
                            # Send large amount of data to simulate exfiltration
                            exfil_data = b"EXFIL_DATA_" + b"S" * 1000  # 1KB of suspicious data
                            sock.send(exfil_data)
                            print(f"Data exfiltration: Sent {len(exfil_data)} bytes to {target_ip}:443")
                        else:
                            print(f"Data exfiltration: Connection to {target_ip}:443 failed")
                        
                        sock.close()
                        
                    except Exception as e:
                        print(f"Data exfiltration attempt - Error: {e}")
                    
                    next_transfer_time += transfer_interval
                
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in data exfiltration traffic generation: {e}")
                break
        
        self.running = False
        print("Data exfiltration traffic generation completed")
    
    def run_comprehensive_attack_simulation(self, target_ip="192.168.100.2", duration=120):
        """Run a comprehensive attack simulation with multiple threat vectors"""
        print(f"Starting comprehensive attack simulation against {target_ip} for {duration}s")
        
        # Start multiple attack threads
        attack_threads = [
            threading.Thread(target=self.generate_port_scan_traffic, args=(target_ip, duration//4, 3)),
            threading.Thread(target=self.generate_ssh_brute_force_traffic, args=(target_ip, duration//4, 2)),
            threading.Thread(target=self.generate_malicious_http_traffic, args=(target_ip, duration//2, 1)),
            threading.Thread(target=self.generate_real_dns_traffic, args=("192.168.100.1", duration, 1)),
            threading.Thread(target=self.generate_data_exfiltration_traffic, args=(target_ip, duration//3, 1))
        ]
        
        # Start all attack threads with delays
        for i, thread in enumerate(attack_threads):
            time.sleep(5)  # Stagger the attacks
            thread.start()
            print(f"Started attack thread {i+1}/{len(attack_threads)}")
        
        # Wait for all threads to complete
        for thread in attack_threads:
            thread.join()
        
        print("Comprehensive attack simulation completed")
    
    def stop_all_traffic(self):
        """Stop all traffic generation"""
        self.running = False
        print("Stopping all traffic generation...")

if __name__ == "__main__":
    generator = EnhancedTrafficGenerator()
    
    print("Enhanced Traffic Generator - Creating real network connections for Zeek monitoring")
    print("Available scenarios:")
    print("1. Normal HTTP traffic")
    print("2. Malicious HTTP traffic (SQL injection patterns)")
    print("3. DNS queries (including suspicious domains)")
    print("4. Port scanning")
    print("5. SSH brute force")
    print("6. Data exfiltration")
    print("7. Comprehensive attack simulation")
    
    choice = input("Select scenario (1-7): ").strip()
    
    if choice == "1":
        generator.generate_real_http_traffic(duration=60)
    elif choice == "2":
        generator.generate_malicious_http_traffic(duration=60)
    elif choice == "3":
        generator.generate_real_dns_traffic(duration=60)
    elif choice == "4":
        generator.generate_port_scan_traffic(duration=30)
    elif choice == "5":
        generator.generate_ssh_brute_force_traffic(duration=30)
    elif choice == "6":
        generator.generate_data_exfiltration_traffic(duration=30)
    elif choice == "7":
        generator.run_comprehensive_attack_simulation(duration=120)
    else:
        print("Invalid choice. Running comprehensive simulation...")
        generator.run_comprehensive_attack_simulation(duration=120)
