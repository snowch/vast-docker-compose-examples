#!/usr/bin/env python3
"""
Scapy Traffic Generator Web Interface with Virtual Network Support
Provides REST API and web interface to generate network traffic on isolated virtual interfaces
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import threading
import time
import os
import json
import subprocess
from datetime import datetime
from scapy.all import *
import random
from network_traffic_generator import NetworkTrafficGenerator
from enhanced_traffic_generator import EnhancedTrafficGenerator
try:
    from kafka import KafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    print("Warning: kafka-python not available. Kafka consumer will be disabled.")

app = Flask(__name__)
CORS(app)

# Global variables for traffic generation control
traffic_threads = {}
active_sessions = {}
kafka_messages = []
kafka_consumer_thread = None
kafka_running = False
continuous_simulation_running = False
continuous_simulation_thread = None
continuous_simulation = None

class KafkaMessageConsumer:
    def __init__(self, broker='172.200.204.1:9092', topic='zeek-live-logs'):
        self.broker = broker
        self.topic = topic
        self.running = False
        self.consumer = None
        
    def start_consuming(self):
        """Start consuming Kafka messages in a separate thread"""
        if not KAFKA_AVAILABLE:
            print("Kafka consumer not available - kafka-python package not installed")
            return False
            
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=[self.broker],
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='zeek-web-consumer',
                value_deserializer=lambda x: x.decode('utf-8') if x else None
            )
            self.running = True
            
            for message in self.consumer:
                if not self.running:
                    break
                    
                try:
                    # Parse the message
                    msg_data = json.loads(message.value) if message.value else {}
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    
                    # Add to global messages list (keep last 100 messages)
                    global kafka_messages
                    kafka_messages.append({
                        'timestamp': timestamp,
                        'data': msg_data
                    })
                    
                    # Keep only last 100 messages
                    if len(kafka_messages) > 100:
                        kafka_messages = kafka_messages[-100:]
                        
                except json.JSONDecodeError:
                    # Handle non-JSON messages
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    kafka_messages.append({
                        'timestamp': timestamp,
                        'data': {'raw_message': message.value}
                    })
                    
        except Exception as e:
            print(f"Kafka consumer error: {e}")
            self.running = False
            return False
            
        return True
        
    def stop_consuming(self):
        """Stop consuming Kafka messages"""
        self.running = False
        if self.consumer:
            self.consumer.close()

def get_zeek_monitor_ip():
    """Discover the IP address of the zeek-live-monitor container"""
    try:
        # Try to get the IP of the zeek-live-monitor container
        result = subprocess.run(
            ['docker', 'inspect', '-f', '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}', 'zeek-live-monitor'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            ip = result.stdout.strip()
            print(f"Found Zeek monitor IP: {ip}")
            return ip
    except Exception as e:
        print(f"Error getting Zeek monitor IP: {e}")
    
    # Fallback: try to find any container in the zeek-network
    try:
        result = subprocess.run(
            ['docker', 'network', 'inspect', 'zeek-network', '-f', '{{range .Containers}}{{.IPv4Address}}{{end}}'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            # Parse the first IP from the network (remove /24 suffix)
            ips = result.stdout.strip().split()
            for ip_with_mask in ips:
                ip = ip_with_mask.split('/')[0]
                if ip and ip != '192.168.100.1':  # Skip gateway
                    print(f"Found container IP in zeek-network: {ip}")
                    return ip
    except Exception as e:
        print(f"Error inspecting zeek-network: {e}")
    
    # Final fallback
    print("Using fallback IP: 192.168.100.2")
    return "192.168.100.2"

class ContinuousSimulation:
    """Manages continuous traffic simulation with weighted scenarios and concurrency support"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.max_concurrent_scenarios = 3  # Default concurrency level
        self.active_scenario_threads = {}  # Track active scenario threads
        
        # Scenario weights (higher = more likely to be selected)
        # Normal traffic scenarios have higher weights
        self.scenario_weights = {
            'web_browsing': 30,      # Most common - normal web traffic
            'office_network': 25,    # Common - office activities
            'file_transfer': 15,     # Moderate - file operations
            'video_streaming': 10,   # Moderate - streaming content
            'dns_queries': 8,        # Background - DNS lookups
            'mixed_traffic': 7,      # Background - general traffic
            'malicious_activity': 3, # Low - security incidents
            'port_scan': 1,          # Very low - attack activity
            'sql_injection': 1       # Very low - attack activity
        }
        
        # Create weighted scenario list for random selection
        self.weighted_scenarios = []
        for scenario, weight in self.scenario_weights.items():
            self.weighted_scenarios.extend([scenario] * weight)
    
    def start_continuous_simulation(self, min_interval=30, max_interval=180, max_concurrent=3):
        """Start continuous simulation with random scenarios and concurrency support"""
        if self.running:
            return False, "Continuous simulation already running"
        
        self.max_concurrent_scenarios = max_concurrent
        self.running = True
        self.thread = threading.Thread(
            target=self._simulation_loop,
            args=(min_interval, max_interval)
        )
        self.thread.daemon = True
        self.thread.start()
        
        return True, f"Continuous simulation started with max {max_concurrent} concurrent scenarios"
    
    def stop_continuous_simulation(self):
        """Stop continuous simulation and all active scenarios"""
        if not self.running:
            return False, "Continuous simulation not running"
        
        self.running = False
        
        # Stop all active scenario threads
        for session_id, (generator, thread) in list(self.active_scenario_threads.items()):
            generator.running = False
            print(f"Stopping scenario thread: {session_id}")
        
        # Wait for main thread to stop
        if self.thread:
            self.thread.join(timeout=5)
        
        # Clean up active threads
        self.active_scenario_threads.clear()
        
        return True, "Continuous simulation stopped"
    
    def _simulation_loop(self, min_interval, max_interval):
        """Main simulation loop that runs scenarios continuously with concurrency support"""
        print(f"Starting continuous simulation loop (interval: {min_interval}-{max_interval}s, max concurrent: {self.max_concurrent_scenarios})")
        
        while self.running:
            try:
                # Clean up finished scenario threads
                self._cleanup_finished_scenarios()
                
                # Check if we can start a new scenario (respect concurrency limit)
                if len(self.active_scenario_threads) < self.max_concurrent_scenarios:
                    # Select random scenario based on weights
                    scenario = random.choice(self.weighted_scenarios)
                    
                    # Determine scenario duration (shorter for attacks, longer for normal traffic)
                    if scenario in ['malicious_activity', 'port_scan', 'sql_injection']:
                        duration = random.randint(30, 90)  # Shorter attack scenarios
                        pps = random.randint(2, 5)
                    else:
                        duration = random.randint(60, 180)  # Longer normal scenarios
                        pps = random.randint(1, 8)
                    
                    print(f"Continuous simulation: Starting {scenario} for {duration}s at {pps} pps (concurrent: {len(self.active_scenario_threads)+1}/{self.max_concurrent_scenarios})")
                    
                    # Create new generator for this scenario
                    generator = TrafficGenerator()
                    session_id = f"continuous_{scenario}_{int(time.time())}"
                    
                    # Start the appropriate scenario
                    thread = self._start_scenario_thread(generator, scenario, duration, pps)
                    if thread:
                        # Store the session in both global and local tracking
                        traffic_threads[session_id] = generator
                        active_sessions[session_id] = {
                            'type': f"continuous_{scenario}",
                            'started': datetime.now().isoformat(),
                            'duration': duration,
                            'scenario': scenario,
                            'pps': pps,
                            'continuous': True
                        }
                        
                        # Start thread and track it locally
                        thread.start()
                        self.active_scenario_threads[session_id] = (generator, thread)
                
                # Wait for a shorter interval when running concurrent scenarios
                if self.running:
                    # Use shorter wait times when we have capacity for more scenarios
                    if len(self.active_scenario_threads) < self.max_concurrent_scenarios:
                        wait_time = random.randint(min_interval // 2, min_interval)
                    else:
                        wait_time = random.randint(min_interval, max_interval)
                    
                    print(f"Continuous simulation: Waiting {wait_time}s before next scenario check (active: {len(self.active_scenario_threads)})")
                    
                    # Sleep in small chunks to allow for quick stopping
                    for _ in range(wait_time):
                        if not self.running:
                            break
                        time.sleep(1)
                
            except Exception as e:
                print(f"Error in continuous simulation loop: {e}")
                time.sleep(10)  # Wait before retrying
        
        print("Continuous simulation loop stopped")
    
    def _cleanup_finished_scenarios(self):
        """Clean up finished scenario threads"""
        finished_sessions = []
        
        for session_id, (generator, thread) in list(self.active_scenario_threads.items()):
            if not generator.running or not thread.is_alive():
                finished_sessions.append(session_id)
        
        for session_id in finished_sessions:
            print(f"Cleaning up finished scenario: {session_id}")
            del self.active_scenario_threads[session_id]
            # Also clean up from global tracking
            if session_id in traffic_threads:
                del traffic_threads[session_id]
            if session_id in active_sessions:
                del active_sessions[session_id]
    
    def _start_scenario_thread(self, generator, scenario, duration, pps):
        """Create and return a thread for the specified scenario"""
        if scenario == "web_browsing":
            return threading.Thread(
                target=generator.generate_web_browsing_scenario,
                args=(duration, pps)
            )
        elif scenario == "file_transfer":
            return threading.Thread(
                target=generator.generate_file_transfer_scenario,
                args=(duration, pps)
            )
        elif scenario == "video_streaming":
            return threading.Thread(
                target=generator.generate_video_streaming_scenario,
                args=(duration, pps)
            )
        elif scenario == "office_network":
            return threading.Thread(
                target=generator.generate_office_network_scenario,
                args=(duration, pps)
            )
        elif scenario == "malicious_activity":
            return threading.Thread(
                target=generator.generate_malicious_activity_scenario,
                args=(duration, pps)
            )
        elif scenario == "port_scan":
            return threading.Thread(
                target=generator.enhanced_generator.generate_port_scan_traffic,
                args=(generator.zeek_monitor_ip, duration, pps)
            )
        elif scenario == "sql_injection":
            return threading.Thread(
                target=generator.enhanced_generator.generate_malicious_http_traffic,
                args=(generator.zeek_monitor_ip, duration, 2)
            )
        elif scenario == "dns_queries":
            return threading.Thread(
                target=generator.generate_dns_traffic,
                args=(None, duration, pps)
            )
        elif scenario == "mixed_traffic":
            return threading.Thread(
                target=generator.generate_mixed_traffic,
                args=(duration, pps)
            )
        else:
            return threading.Thread(
                target=generator.generate_mixed_traffic,
                args=(duration, pps)
            )

class TrafficGenerator(NetworkTrafficGenerator):
    def __init__(self):
        super().__init__()
        self.zeek_monitor_ip = get_zeek_monitor_ip()
        self.enhanced_generator = EnhancedTrafficGenerator()
        
    def generate_http_traffic(self, target_ip=None, duration=60, packets_per_second=1):
        """Generate simulated HTTP traffic with precise timing"""
        # Use discovered Zeek monitor IP if no target specified
        if target_ip is None:
            target_ip = self.zeek_monitor_ip
        
        print(f"Generating HTTP traffic to {target_ip} for {duration}s at {packets_per_second} pps")
        
        self.running = True
        start_time = time.time()
        end_time = start_time + duration
        packet_interval = 1.0 / packets_per_second
        next_packet_time = start_time
        
        while self.running and time.time() < end_time:
            try:
                current_time = time.time()
                if current_time >= next_packet_time:
                    # Create HTTP-like TCP traffic
                    src_port = random.randint(1024, 65535)
                    packet = IP(dst=target_ip)/TCP(dport=80, sport=src_port)/Raw(load="GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
                    send(packet, verbose=0)
                    
                    # Schedule next packet with precise timing
                    next_packet_time += packet_interval
                
                # Small sleep to prevent busy waiting
                time.sleep(0.001)
            except Exception as e:
                print(f"Error generating HTTP traffic: {e}")
                break
                
        self.running = False
    
    def generate_dns_traffic(self, target_ip=None, duration=60, packets_per_second=1):
        """Generate simulated DNS traffic with precise timing"""
        # Use discovered Zeek monitor IP if no target specified
        if target_ip is None:
            target_ip = self.zeek_monitor_ip
        
        print(f"Generating DNS traffic to {target_ip} for {duration}s at {packets_per_second} pps")
        
        self.running = True
        start_time = time.time()
        end_time = start_time + duration
        packet_interval = 1.0 / packets_per_second
        next_packet_time = start_time
        domains = ["example.com", "google.com", "github.com", "stackoverflow.com", "wikipedia.org"]
        
        while self.running and time.time() < end_time:
            try:
                current_time = time.time()
                if current_time >= next_packet_time:
                    domain = random.choice(domains)
                    packet = IP(dst=target_ip)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain))
                    send(packet, verbose=0)
                    
                    # Schedule next packet with precise timing
                    next_packet_time += packet_interval
                
                # Small sleep to prevent busy waiting
                time.sleep(0.001)
            except Exception as e:
                print(f"Error generating DNS traffic: {e}")
                break
                
        self.running = False
    
    def generate_mixed_traffic(self, duration=60, packets_per_second=2):
        """Generate mixed protocol traffic with precise timing"""
        self.running = True
        start_time = time.time()
        end_time = start_time + duration
        packet_interval = 1.0 / packets_per_second
        next_packet_time = start_time
        
        while self.running and time.time() < end_time:
            try:
                current_time = time.time()
                if current_time >= next_packet_time:
                    traffic_type = random.choice(['http', 'dns', 'tcp', 'udp'])
                    
                    if traffic_type == 'http':
                        target = f"192.168.100.{random.randint(20, 29)}"
                        packet = IP(dst=target)/TCP(dport=80, sport=random.randint(1024, 65535))/Raw(load="GET /index.html HTTP/1.1\r\n\r\n")
                    elif traffic_type == 'dns':
                        packet = IP(dst="192.168.100.1")/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=f"host{random.randint(1,100)}.example.com"))
                    elif traffic_type == 'tcp':
                        packet = IP(dst=f"192.168.100.{random.randint(20, 29)}")/TCP(dport=random.choice([22, 443, 993, 995]))
                    else:  # udp
                        packet = IP(dst=f"192.168.100.{random.randint(20, 29)}")/UDP(dport=random.choice([123, 161, 514]))
                    
                    send(packet, verbose=0)
                    
                    # Schedule next packet with precise timing
                    next_packet_time += packet_interval
                
                # Small sleep to prevent busy waiting
                time.sleep(0.001)
            except Exception as e:
                print(f"Error generating mixed traffic: {e}")
                break
                
        self.running = False
    
    def generate_web_browsing_scenario(self, duration=120, packets_per_second=5):
        """Generate web browsing scenario using the same approach as custom traffic"""
        self.running = True
        start_time = time.time()
        end_time = start_time + duration
        packet_interval = 1.0 / packets_per_second
        next_packet_time = start_time
        
        print(f"Starting web browsing scenario for {duration}s at {packets_per_second} pps")
        
        while self.running and time.time() < end_time:
            try:
                current_time = time.time()
                if current_time >= next_packet_time:
                    # Create realistic web browsing traffic
                    traffic_type = random.choice(['http_get', 'https_connect', 'dns_lookup'])
                    
                    if traffic_type == 'http_get':
                        target_ip = f"192.168.100.{random.randint(20, 29)}"
                        src_port = random.randint(1024, 65535)
                        pages = ["/", "/index.html", "/about.html", "/products.html", "/contact.html"]
                        page = random.choice(pages)
                        payload = f"GET {page} HTTP/1.1\r\nHost: example.com\r\nUser-Agent: Mozilla/5.0\r\n\r\n"
                        packet = IP(dst=target_ip)/TCP(dport=80, sport=src_port)/Raw(load=payload)
                    elif traffic_type == 'https_connect':
                        target_ip = f"192.168.100.{random.randint(20, 29)}"
                        packet = IP(dst=target_ip)/TCP(dport=443, sport=random.randint(1024, 65535), flags="S")
                    else:  # dns_lookup
                        domains = ["example.com", "cdn.example.com", "api.example.com", "images.example.com"]
                        domain = random.choice(domains)
                        packet = IP(dst="192.168.100.1")/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain))
                    
                    send(packet, verbose=0)
                    next_packet_time += packet_interval
                
                time.sleep(0.001)
            except Exception as e:
                print(f"Error in web browsing scenario: {e}")
                break
                
        self.running = False
    
    def generate_file_transfer_scenario(self, duration=120, packets_per_second=5):
        """Generate file transfer scenario"""
        self.running = True
        start_time = time.time()
        end_time = start_time + duration
        packet_interval = 1.0 / packets_per_second
        next_packet_time = start_time
        
        print(f"Starting file transfer scenario for {duration}s at {packets_per_second} pps")
        
        while self.running and time.time() < end_time:
            try:
                current_time = time.time()
                if current_time >= next_packet_time:
                    traffic_type = random.choice(['ftp_control', 'ftp_data', 'sftp'])
                    target_ip = f"192.168.100.{random.randint(20, 29)}"
                    
                    if traffic_type == 'ftp_control':
                        commands = ["USER demo", "PASS secret", "LIST", "RETR file.txt", "STOR upload.txt"]
                        command = random.choice(commands)
                        packet = IP(dst=target_ip)/TCP(dport=21, sport=random.randint(1024, 65535))/Raw(load=command + "\r\n")
                    elif traffic_type == 'ftp_data':
                        data_size = random.randint(500, 1400)
                        payload = "FILE_DATA_" + "A" * (data_size - 10)
                        packet = IP(dst=target_ip)/TCP(dport=20, sport=random.randint(1024, 65535))/Raw(load=payload)
                    else:  # sftp
                        packet = IP(dst=target_ip)/TCP(dport=22, sport=random.randint(1024, 65535))
                    
                    send(packet, verbose=0)
                    next_packet_time += packet_interval
                
                time.sleep(0.001)
            except Exception as e:
                print(f"Error in file transfer scenario: {e}")
                break
                
        self.running = False
    
    def generate_video_streaming_scenario(self, duration=120, packets_per_second=5):
        """Generate video streaming scenario"""
        self.running = True
        start_time = time.time()
        end_time = start_time + duration
        packet_interval = 1.0 / packets_per_second
        next_packet_time = start_time
        
        print(f"Starting video streaming scenario for {duration}s at {packets_per_second} pps")
        
        while self.running and time.time() < end_time:
            try:
                current_time = time.time()
                if current_time >= next_packet_time:
                    # High bandwidth streaming traffic
                    src_ip = f"192.168.100.{random.randint(20, 29)}"  # Server
                    dst_ip = f"192.168.100.{random.randint(10, 19)}"  # Client
                    
                    data_size = random.randint(800, 1400)
                    payload = "VIDEO_STREAM_" + "X" * (data_size - 13)
                    packet = IP(src=src_ip, dst=dst_ip)/UDP(sport=8080, dport=random.randint(1024, 65535))/Raw(load=payload)
                    
                    send(packet, verbose=0)
                    next_packet_time += packet_interval
                
                time.sleep(0.001)
            except Exception as e:
                print(f"Error in video streaming scenario: {e}")
                break
                
        self.running = False
    
    def generate_office_network_scenario(self, duration=120, packets_per_second=5):
        """Generate office network scenario"""
        self.running = True
        start_time = time.time()
        end_time = start_time + duration
        packet_interval = 1.0 / packets_per_second
        next_packet_time = start_time
        
        print(f"Starting office network scenario for {duration}s at {packets_per_second} pps")
        
        while self.running and time.time() < end_time:
            try:
                current_time = time.time()
                if current_time >= next_packet_time:
                    services = ["email", "file_share", "print", "web_proxy"]
                    service = random.choice(services)
                    src_ip = f"192.168.100.{random.randint(10, 19)}"
                    
                    if service == "email":
                        dst_ip = f"192.168.100.{random.randint(20, 29)}"
                        protocols = [("smtp", 25), ("pop3", 110), ("imap", 143), ("smtps", 465)]
                        protocol, port = random.choice(protocols)
                        packet = IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=port)
                    elif service == "file_share":
                        dst_ip = f"192.168.100.{random.randint(20, 29)}"
                        packet = IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=445)  # SMB
                    elif service == "print":
                        dst_ip = f"192.168.100.{random.randint(30, 39)}"  # Printer range
                        packet = IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=631)  # IPP
                    else:  # web_proxy
                        dst_ip = f"192.168.100.{random.randint(20, 29)}"
                        packet = IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=8080)
                    
                    send(packet, verbose=0)
                    next_packet_time += packet_interval
                
                time.sleep(0.001)
            except Exception as e:
                print(f"Error in office network scenario: {e}")
                break
                
        self.running = False
    
    def generate_malicious_activity_scenario(self, duration=120, packets_per_second=5):
        """Generate malicious activity scenario for IDS testing"""
        self.running = True
        start_time = time.time()
        end_time = start_time + duration
        packet_interval = 1.0 / packets_per_second
        next_packet_time = start_time
        
        print(f"Starting malicious activity scenario for {duration}s at {packets_per_second} pps")
        
        while self.running and time.time() < end_time:
            try:
                current_time = time.time()
                if current_time >= next_packet_time:
                    attacks = ["port_scan", "brute_force", "suspicious_dns", "data_exfiltration"]
                    attack = random.choice(attacks)
                    src_ip = f"192.168.100.{random.randint(100, 109)}"  # Suspicious source range
                    dst_ip = f"192.168.100.{random.randint(10, 29)}"
                    
                    if attack == "port_scan":
                        ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
                        port = random.choice(ports)
                        packet = IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=port, flags="S")
                    elif attack == "brute_force":
                        packet = IP(src=src_ip, dst=dst_ip)/TCP(sport=random.randint(1024, 65535), dport=22)
                    elif attack == "suspicious_dns":
                        domains = ["malware-c2.evil", "phishing.bad", "botnet.cmd"]
                        domain = random.choice(domains)
                        packet = IP(src=src_ip, dst="192.168.100.1")/UDP(sport=random.randint(1024, 65535), dport=53)/DNS(rd=1, qd=DNSQR(qname=domain))
                    else:  # data_exfiltration
                        data_size = random.randint(1000, 1400)
                        payload = "EXFIL_DATA_" + "S" * (data_size - 11)
                        packet = IP(src=dst_ip, dst=src_ip)/TCP(sport=random.randint(1024, 65535), dport=443)/Raw(load=payload)
                    
                    send(packet, verbose=0)
                    next_packet_time += packet_interval
                
                time.sleep(0.001)
            except Exception as e:
                print(f"Error in malicious activity scenario: {e}")
                break
                
        self.running = False

# Web interface HTML template
WEB_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>Network Traffic Generator</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 10px; background: #f8f9fa; font-size: 14px; }
        .header { display: flex; justify-content: space-between; align-items: center; background: white; padding: 15px 20px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header h1 { margin: 0; font-size: 24px; color: #2c3e50; }
        .status-badge { background: #e3f2fd; color: #1976d2; padding: 8px 12px; border-radius: 20px; font-weight: 500; font-size: 13px; }
        .main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px; }
        .control-panel { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .scenarios { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 8px; margin: 15px 0; }
        .scenario-btn { background: linear-gradient(135deg, #28a745, #20c997); color: white; border: none; padding: 12px 8px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 500; transition: all 0.2s; text-align: center; }
        .scenario-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
        .custom-form { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; align-items: end; margin: 15px 0; }
        .form-group { display: flex; flex-direction: column; }
        .form-group label { font-size: 12px; color: #6c757d; margin-bottom: 4px; font-weight: 500; }
        input, select { padding: 8px; border: 1px solid #dee2e6; border-radius: 4px; font-size: 13px; }
        .btn { background: #007bff; color: white; border: none; padding: 10px 16px; border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: 500; transition: background 0.2s; }
        .btn:hover { background: #0056b3; }
        .btn-success { background: #28a745; }
        .btn-success:hover { background: #218838; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #545b62; }
        .status-section { background: white; padding: 15px 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 15px; }
        .status-display { padding: 10px; border-radius: 4px; margin: 10px 0; font-weight: 500; }
        .status-success { background: #d4edda; color: #155724; border-left: 4px solid #28a745; }
        .status-error { background: #f8d7da; color: #721c24; border-left: 4px solid #dc3545; }
        .status-info { background: #d1ecf1; color: #0c5460; border-left: 4px solid #17a2b8; }
        .logs-grid { display: grid; grid-template-columns: 1fr 2fr; gap: 15px; min-width: 0; }
        .log-panel { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 0; }
        .log-header { padding: 15px 20px; border-bottom: 1px solid #dee2e6; display: flex; justify-content: space-between; align-items: center; }
        .log-header h3 { margin: 0; font-size: 16px; color: #495057; }
        .log-controls { display: flex; gap: 8px; }
        .log-box { height: 300px; overflow-x: auto; overflow-y: auto; padding: 15px; font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace; font-size: 11px; line-height: 1.4; background: #f8f9fa; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; white-space: nowrap; }
        .kafka-log-box { height: 300px; width: 100%; min-width: 0; max-width: 100%; overflow-x: scroll; overflow-y: auto; padding: 15px; font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace; font-size: 11px; line-height: 1.4; background: #f8f9fa; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; white-space: pre; box-sizing: border-box; }
        .kafka-status { display: inline-block; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
        .kafka-connected { background: #d4edda; color: #155724; }
        .kafka-disconnected { background: #f8d7da; color: #721c24; }
        .btn-sm { padding: 6px 10px; font-size: 11px; }
        .section-title { font-size: 16px; font-weight: 600; color: #495057; margin: 0 0 15px 0; }
        .tip { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 10px; border-radius: 4px; font-size: 12px; margin: 10px 0; }
        @media (max-width: 768px) {
            .main-grid, .logs-grid { grid-template-columns: 1fr; }
            .scenarios { grid-template-columns: repeat(2, 1fr); }
            .custom-form { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Network Traffic Generator for Zeek Monitoring</h1>
        <div class="status-badge">📊 Status: Active | 🔗 Network: zeek-network</div>
    </div>
    
    <div class="main-grid">
        <div class="control-panel">
            <h2 class="section-title">🔄 Continuous Simulation</h2>
            <div class="custom-form">
                <div class="form-group">
                    <label>Min Interval (s)</label>
                    <input type="number" id="minInterval" value="30" min="10" max="300">
                </div>
                <div class="form-group">
                    <label>Max Interval (s)</label>
                    <input type="number" id="maxInterval" value="180" min="30" max="600">
                </div>
                <div class="form-group">
                    <label>Max Concurrent</label>
                    <input type="number" id="maxConcurrent" value="3" min="1" max="10">
                </div>
                <div class="form-group">
                    <label>&nbsp;</label>
                    <button id="continuous-start-btn" class="btn btn-success" onclick="startContinuousSimulation()">Start Continuous</button>
                    <button id="continuous-stop-btn" class="btn btn-danger" onclick="stopContinuousSimulation()" style="display: none;">Stop Continuous</button>
                </div>
            </div>
            <div class="tip">🔄 Runs random scenarios continuously with weighted selection. Normal traffic (70%) vs attacks (30%). Concurrency allows multiple scenarios to run simultaneously for increased load.</div>
            <div id="concurrent-status" class="status-display status-info" style="display: none;">Concurrent scenarios: 0/3</div>
        </div>
        
        <div class="control-panel">
            <h2 class="section-title">🎭 Quick Scenarios</h2>
            <div class="scenarios">
                <button class="scenario-btn" onclick="startScenario('web_browsing')">🌐<br>Web Browsing</button>
                <button class="scenario-btn" onclick="startScenario('file_transfer')">📁<br>File Transfer</button>
                <button class="scenario-btn" onclick="startScenario('video_streaming')">🎥<br>Video Stream</button>
                <button class="scenario-btn" onclick="startScenario('office_network')">🏢<br>Office Network</button>
                <button class="scenario-btn" onclick="startScenario('malicious_activity')">🛡️<br>Security Test</button>
                <button class="scenario-btn" onclick="startScenario('enhanced_attacks')">⚡<br>Enhanced Attacks</button>
                <button class="scenario-btn" onclick="startScenario('port_scan')">🔍<br>Port Scan</button>
                <button class="scenario-btn" onclick="startScenario('sql_injection')">💉<br>SQL Injection</button>
            </div>
            <div class="tip">💡 Standard scenarios run for 2 minutes. Enhanced attacks create real network connections for better detection.</div>
        </div>
        
        <div class="control-panel">
            <h2 class="section-title">⚙️ Custom Traffic</h2>
            <div class="custom-form">
                <div class="form-group">
                    <label>Type</label>
                    <select id="trafficType">
                        <option value="http">HTTP</option>
                        <option value="dns">DNS</option>
                        <option value="mixed">Mixed</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Duration (s)</label>
                    <input type="number" id="duration" value="60" min="1" max="3600">
                </div>
                <div class="form-group">
                    <label>Packets/sec</label>
                    <input type="number" id="pps" value="2" min="1" max="100">
                </div>
                <div class="form-group">
                    <label>&nbsp;</label>
                    <button class="btn btn-success" onclick="startCustomTraffic()">Start Traffic</button>
                </div>
            </div>
            <div class="tip">💡 Traffic automatically targets the Zeek monitor container for proper monitoring</div>
        </div>
    </div>
    
    <div class="status-section">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2 class="section-title">📈 System Status</h2>
            <button class="btn btn-secondary btn-sm" onclick="getStatus()">Refresh</button>
        </div>
        <div id="status" class="status-display status-info">Ready to generate traffic</div>
    </div>
    
    <div class="logs-grid">
        <div class="log-panel">
            <div class="log-header">
                <h3>📝 Activity Log</h3>
                <button class="btn btn-secondary btn-sm" onclick="clearActivityLog()">Clear</button>
            </div>
            <div id="log" class="log-box"></div>
        </div>
        
        <div class="log-panel">
            <div class="log-header">
                <h3>📡 Kafka Consumer</h3>
                <div class="log-controls">
                    <span id="kafka-status" class="kafka-status kafka-disconnected">Disconnected</span>
                    <button id="kafka-start-btn" class="btn btn-success btn-sm" onclick="startKafkaConsumer()">Start</button>
                    <button id="kafka-stop-btn" class="btn btn-danger btn-sm" onclick="stopKafkaConsumer()" style="display: none;">Stop</button>
                    <button class="btn btn-secondary btn-sm" onclick="clearKafkaMessages()">Clear</button>
                </div>
            </div>
            <div id="kafka-log" class="kafka-log-box"></div>
        </div>
    </div>

    <script>
        function log(message) {
            const logDiv = document.getElementById('log');
            const timestamp = new Date().toLocaleTimeString();
            logDiv.innerHTML += `[${timestamp}] ${message}<br>\n`;
            logDiv.scrollTop = logDiv.scrollHeight;
        }
        
        function showStatus(message, type = 'info') {
            const statusDiv = document.getElementById('status');
            statusDiv.className = `status-display status-${type}`;
            statusDiv.textContent = message;
        }
        
        async function apiCall(endpoint, data = {}) {
            try {
                const response = await fetch(`/api/${endpoint}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                return await response.json();
            } catch (error) {
                log(`API Error: ${error.message}`);
                showStatus(`Error: ${error.message}`, 'error');
                return null;
            }
        }
        
        async function startScenario(scenario) {
            log(`Starting ${scenario} scenario...`);
            const result = await apiCall('start_scenario', {
                scenario: scenario,
                duration: 120,
                packets_per_second: 5
            });
            if (result && result.success) {
                showStatus(`${scenario} scenario started`, 'success');
                log(`Scenario started - Session ID: ${result.session_id}`);
            }
        }
        
        async function startCustomTraffic() {
            const trafficType = document.getElementById('trafficType').value;
            const duration = parseInt(document.getElementById('duration').value);
            const pps = parseInt(document.getElementById('pps').value);
            
            log(`Starting custom ${trafficType} traffic...`);
            const result = await apiCall('start_traffic', {
                type: trafficType,
                duration: duration,
                packets_per_second: pps
            });
            if (result && result.success) {
                showStatus(`Custom ${trafficType} traffic started`, 'success');
                log(`Custom traffic started - Session ID: ${result.session_id}`);
            }
        }
        
        async function stopAllTraffic() {
            log('Stopping all traffic generation...');
            const result = await apiCall('stop_all');
            if (result && result.success) {
                showStatus('All traffic generation stopped', 'success');
                log('All traffic sessions stopped');
            }
        }
        
        async function getStatus() {
            const result = await apiCall('status');
            if (result) {
                const active = result.active_sessions || 0;
                showStatus(`Active sessions: ${active}`, active > 0 ? 'success' : 'info');
                log(`Status check: ${active} active sessions`);
            }
        }
        
        // Kafka consumer functions
        async function startKafkaConsumer() {
            log('Starting Kafka consumer...');
            const result = await apiCall('kafka/start');
            if (result && result.success) {
                document.getElementById('kafka-status').className = 'kafka-status kafka-connected';
                document.getElementById('kafka-status').textContent = 'Connected';
                document.getElementById('kafka-start-btn').style.display = 'none';
                document.getElementById('kafka-stop-btn').style.display = 'inline-block';
                log('Kafka consumer started successfully');
                // Start polling for messages
                startKafkaPolling();
            } else {
                log(`Failed to start Kafka consumer: ${result ? result.error : 'Unknown error'}`);
            }
        }
        
        async function stopKafkaConsumer() {
            log('Stopping Kafka consumer...');
            const result = await apiCall('kafka/stop');
            if (result && result.success) {
                document.getElementById('kafka-status').className = 'kafka-status kafka-disconnected';
                document.getElementById('kafka-status').textContent = 'Disconnected';
                document.getElementById('kafka-start-btn').style.display = 'inline-block';
                document.getElementById('kafka-stop-btn').style.display = 'none';
                log('Kafka consumer stopped');
                stopKafkaPolling();
            }
        }
        
        async function clearKafkaMessages() {
            const result = await apiCall('kafka/clear');
            if (result && result.success) {
                document.getElementById('kafka-log').innerHTML = '';
                log('Kafka messages cleared');
            }
        }
        
        function clearActivityLog() {
            document.getElementById('log').innerHTML = '';
        }
        
        let kafkaPollingInterval;
        
        function startKafkaPolling() {
            kafkaPollingInterval = setInterval(async () => {
                try {
                    const response = await fetch('/api/kafka/messages');
                    const result = await response.json();
                    if (result && result.success) {
                        updateKafkaLog(result.messages);
                    }
                } catch (error) {
                    console.error('Error polling Kafka messages:', error);
                }
            }, 1000); // Poll every second
        }
        
        function stopKafkaPolling() {
            if (kafkaPollingInterval) {
                clearInterval(kafkaPollingInterval);
                kafkaPollingInterval = null;
            }
        }
        
        function updateKafkaLog(messages) {
            const kafkaLogDiv = document.getElementById('kafka-log');
            let content = '';
            
            messages.forEach(msg => {
                const timestamp = msg.timestamp;
                const data = msg.data;
                content += `[${timestamp}] RAW: ${JSON.stringify(data)}\n`;
            });
            
            kafkaLogDiv.textContent = content; // This preserves whitespace and formatting
            kafkaLogDiv.scrollTop = kafkaLogDiv.scrollHeight;
        }
        
        // Continuous simulation functions
        async function startContinuousSimulation() {
            const minInterval = parseInt(document.getElementById('minInterval').value);
            const maxInterval = parseInt(document.getElementById('maxInterval').value);
            const maxConcurrent = parseInt(document.getElementById('maxConcurrent').value);
            
            log('Starting continuous simulation...');
            const result = await apiCall('continuous/start', {
                min_interval: minInterval,
                max_interval: maxInterval,
                max_concurrent: maxConcurrent
            });
            if (result && result.success) {
                document.getElementById('continuous-start-btn').style.display = 'none';
                document.getElementById('continuous-stop-btn').style.display = 'inline-block';
                document.getElementById('concurrent-status').style.display = 'block';
                showStatus('Continuous simulation started', 'success');
                log(`Continuous simulation started (${minInterval}-${maxInterval}s intervals, max ${maxConcurrent} concurrent)`);
            }
        }
        
        async function stopContinuousSimulation() {
            log('Stopping continuous simulation...');
            const result = await apiCall('continuous/stop');
            if (result && result.success) {
                document.getElementById('continuous-start-btn').style.display = 'inline-block';
                document.getElementById('continuous-stop-btn').style.display = 'none';
                document.getElementById('concurrent-status').style.display = 'none';
                showStatus('Continuous simulation stopped', 'info');
                log('Continuous simulation stopped');
            }
        }
        
        async function getContinuousStatus() {
            try {
                const response = await fetch('/api/continuous/status');
                const result = await response.json();
                if (result && result.success) {
                    if (result.running) {
                        document.getElementById('continuous-start-btn').style.display = 'none';
                        document.getElementById('continuous-stop-btn').style.display = 'inline-block';
                        document.getElementById('concurrent-status').style.display = 'block';
                        
                        // Update concurrent status display
                        const statusDiv = document.getElementById('concurrent-status');
                        const active = result.active_concurrent || 0;
                        const max = result.max_concurrent || 3;
                        statusDiv.textContent = `Concurrent scenarios: ${active}/${max}`;
                        statusDiv.className = `status-display ${active > 0 ? 'status-success' : 'status-info'}`;
                    } else {
                        document.getElementById('continuous-start-btn').style.display = 'inline-block';
                        document.getElementById('continuous-stop-btn').style.display = 'none';
                        document.getElementById('concurrent-status').style.display = 'none';
                    }
                }
            } catch (error) {
                console.error('Error checking continuous status:', error);
            }
        }
        
        // Auto-refresh status every 30 seconds
        setInterval(getStatus, 30000);
        setInterval(getContinuousStatus, 10000);
        
        // Initial status check
        getStatus();
        getContinuousStatus();
        log('Virtual Network Traffic Generator initialized');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(WEB_INTERFACE)

@app.route('/api/start_scenario', methods=['POST'])
def start_scenario():
    try:
        data = request.get_json()
        scenario = data.get('scenario', 'web_browsing')
        duration = data.get('duration', 120)
        packets_per_second = data.get('packets_per_second', 5)
        
        # Generate unique session ID
        session_id = f"scenario_{scenario}_{int(time.time())}"
        
        # Create traffic generator
        generator = TrafficGenerator()
        
        # Start scenario simulation - use the same approach as custom traffic
        if scenario == "web_browsing":
            thread = threading.Thread(
                target=generator.generate_web_browsing_scenario,
                args=(duration, packets_per_second)
            )
        elif scenario == "file_transfer":
            thread = threading.Thread(
                target=generator.generate_file_transfer_scenario,
                args=(duration, packets_per_second)
            )
        elif scenario == "video_streaming":
            thread = threading.Thread(
                target=generator.generate_video_streaming_scenario,
                args=(duration, packets_per_second)
            )
        elif scenario == "office_network":
            thread = threading.Thread(
                target=generator.generate_office_network_scenario,
                args=(duration, packets_per_second)
            )
        elif scenario == "malicious_activity":
            thread = threading.Thread(
                target=generator.generate_malicious_activity_scenario,
                args=(duration, packets_per_second)
            )
        elif scenario == "enhanced_attacks":
            thread = threading.Thread(
                target=generator.enhanced_generator.run_comprehensive_attack_simulation,
                args=(generator.zeek_monitor_ip, duration)
            )
        elif scenario == "port_scan":
            thread = threading.Thread(
                target=generator.enhanced_generator.generate_port_scan_traffic,
                args=(generator.zeek_monitor_ip, duration, 5)
            )
        elif scenario == "sql_injection":
            thread = threading.Thread(
                target=generator.enhanced_generator.generate_malicious_http_traffic,
                args=(generator.zeek_monitor_ip, duration, 2)
            )
        else:
            thread = threading.Thread(
                target=generator.generate_mixed_traffic,
                args=(duration, packets_per_second)
            )
        
        thread.start()
        
        # Store the session
        traffic_threads[session_id] = generator
        active_sessions[session_id] = {
            'type': f"scenario_{scenario}",
            'interface': 'br-zeek-sim',
            'started': datetime.now().isoformat(),
            'duration': duration,
            'scenario': scenario,
            'pps': packets_per_second
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': f'{scenario} scenario started on virtual network'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/start_traffic', methods=['POST'])
def start_traffic():
    try:
        data = request.get_json()
        traffic_type = data.get('type', 'mixed')
        duration = data.get('duration', 60)
        packets_per_second = data.get('packets_per_second', 2)
        
        # Generate unique session ID
        session_id = f"{traffic_type}_{int(time.time())}"
        
        # Create traffic generator
        generator = TrafficGenerator()
        
        # Start appropriate traffic generation in a thread
        # HTTP and DNS will automatically use the discovered Zeek monitor IP
        if traffic_type == 'http':
            thread = threading.Thread(
                target=generator.generate_http_traffic,
                args=(None, duration, packets_per_second)  # None = use auto-discovered IP
            )
        elif traffic_type == 'dns':
            thread = threading.Thread(
                target=generator.generate_dns_traffic,
                args=(None, duration, packets_per_second)  # None = use auto-discovered IP
            )
        else:  # mixed
            thread = threading.Thread(
                target=generator.generate_mixed_traffic,
                args=(duration, packets_per_second)
            )
        
        thread.start()
        
        # Store the session
        traffic_threads[session_id] = generator
        active_sessions[session_id] = {
            'type': traffic_type,
            'started': datetime.now().isoformat(),
            'duration': duration,
            'target_ip': generator.zeek_monitor_ip,
            'pps': packets_per_second
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': f'{traffic_type.upper()} traffic generation started'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop_all', methods=['POST'])
def stop_all_traffic():
    try:
        stopped_count = 0
        for session_id, generator in traffic_threads.items():
            generator.running = False
            stopped_count += 1
        
        traffic_threads.clear()
        active_sessions.clear()
        
        return jsonify({
            'success': True,
            'message': f'Stopped {stopped_count} traffic sessions'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/status', methods=['POST', 'GET'])
def get_status():
    try:
        # Clean up finished sessions
        active_count = 0
        for session_id, generator in list(traffic_threads.items()):
            if not generator.running:
                del traffic_threads[session_id]
                if session_id in active_sessions:
                    del active_sessions[session_id]
            else:
                active_count += 1
        
        return jsonify({
            'success': True,
            'active_sessions': active_count,
            'sessions': active_sessions,
            'kafka_running': kafka_running,
            'kafka_available': KAFKA_AVAILABLE
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/kafka/start', methods=['POST'])
def start_kafka_consumer():
    global kafka_consumer_thread, kafka_running
    
    if not KAFKA_AVAILABLE:
        return jsonify({
            'success': False, 
            'error': 'Kafka consumer not available - kafka-python package not installed'
        })
    
    if kafka_running:
        return jsonify({
            'success': False, 
            'error': 'Kafka consumer already running'
        })
    
    try:
        consumer = KafkaMessageConsumer()
        kafka_consumer_thread = threading.Thread(target=consumer.start_consuming)
        kafka_consumer_thread.daemon = True
        kafka_consumer_thread.start()
        kafka_running = True
        
        return jsonify({
            'success': True,
            'message': 'Kafka consumer started'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/kafka/stop', methods=['POST'])
def stop_kafka_consumer():
    global kafka_running
    
    kafka_running = False
    
    return jsonify({
        'success': True,
        'message': 'Kafka consumer stopped'
    })

@app.route('/api/kafka/messages', methods=['GET'])
def get_kafka_messages():
    global kafka_messages
    
    return jsonify({
        'success': True,
        'messages': kafka_messages[-50:],  # Return last 50 messages
        'total_count': len(kafka_messages)
    })

@app.route('/api/kafka/clear', methods=['POST'])
def clear_kafka_messages():
    global kafka_messages
    
    kafka_messages.clear()
    
    return jsonify({
        'success': True,
        'message': 'Kafka messages cleared'
    })

@app.route('/api/continuous/start', methods=['POST'])
def start_continuous_simulation():
    global continuous_simulation, continuous_simulation_running
    
    try:
        data = request.get_json() or {}
        min_interval = data.get('min_interval', 30)
        max_interval = data.get('max_interval', 180)
        max_concurrent = data.get('max_concurrent', 3)  # New concurrency parameter
        
        if continuous_simulation_running:
            return jsonify({
                'success': False,
                'error': 'Continuous simulation already running'
            })
        
        # Create new continuous simulation instance
        continuous_simulation = ContinuousSimulation()
        success, message = continuous_simulation.start_continuous_simulation(min_interval, max_interval, max_concurrent)
        
        if success:
            continuous_simulation_running = True
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/continuous/stop', methods=['POST'])
def stop_continuous_simulation():
    global continuous_simulation, continuous_simulation_running
    
    try:
        if not continuous_simulation_running or not continuous_simulation:
            return jsonify({
                'success': False,
                'error': 'Continuous simulation not running'
            })
        
        success, message = continuous_simulation.stop_continuous_simulation()
        
        if success:
            continuous_simulation_running = False
            continuous_simulation = None
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/continuous/status', methods=['GET'])
def get_continuous_status():
    global continuous_simulation, continuous_simulation_running
    
    status_data = {
        'success': True,
        'running': continuous_simulation_running,
        'weights': continuous_simulation.scenario_weights if continuous_simulation else {}
    }
    
    if continuous_simulation:
        status_data.update({
            'max_concurrent': continuous_simulation.max_concurrent_scenarios,
            'active_concurrent': len(continuous_simulation.active_scenario_threads),
            'active_scenarios': list(continuous_simulation.active_scenario_threads.keys())
        })
    
    return jsonify(status_data)

if __name__ == '__main__':
    print("Starting Virtual Network Traffic Generator Server...")
    print("Web interface available at: http://localhost:8080")
    print("Virtual network topology: 192.168.200.0/24")
    app.run(host='0.0.0.0', port=8080, debug=False)
