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
from datetime import datetime
from scapy.all import *
import random
from network_traffic_generator import NetworkTrafficGenerator

app = Flask(__name__)
CORS(app)

# Global variables for traffic generation control
traffic_threads = {}
active_sessions = {}

class TrafficGenerator(NetworkTrafficGenerator):
    def __init__(self):
        super().__init__()
        
    def generate_http_traffic(self, target_ip="192.168.100.20", duration=60, packets_per_second=1):
        """Generate simulated HTTP traffic with precise timing"""
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
    
    def generate_dns_traffic(self, target_ip="192.168.100.1", duration=60, packets_per_second=1):
        """Generate simulated DNS traffic with precise timing"""
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

# Web interface HTML template
WEB_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>Scapy Virtual Network Traffic Generator</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .virtual-net { background: #e8f5e8; border-color: #4caf50; }
        .live-monitoring { background: #e3f2fd; border-color: #2196f3; }
        button { background: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        button:hover { background: #0056b3; }
        button.stop { background: #dc3545; }
        button.stop:hover { background: #c82333; }
        button.scenario { background: #28a745; }
        button.scenario:hover { background: #218838; }
        input, select { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        #log { background: #f8f9fa; padding: 10px; border: 1px solid #dee2e6; border-radius: 4px; height: 200px; overflow-y: scroll; font-family: monospace; }
        .topology { background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 Live Network Traffic Simulator</h1>
        <div style="margin: 20px 0; padding: 15px; background: #e3f2fd; border-left: 4px solid #2196f3; border-radius: 4px;">
            <h4 style="margin: 0 0 10px 0; color: #1976d2;">📡 Network Traffic Generator for Zeek Monitoring</h4>
            <p style="margin: 0; color: #0d47a1;">Generate realistic network traffic to test your Zeek-Kafka pipeline. All traffic is sent to the virtual network (192.168.100.0/24) where Zeek monitors and forwards events to Kafka with optimized low-latency settings.</p>
        </div>
                
        <div class="section">
            <h3>🎭 Realistic Simulation Scenarios</h3>
            <p><strong>Pre-configured traffic patterns that simulate real-world network behavior:</strong></p>
            <div style="margin: 10px 0; font-size: 14px; color: #666;">
                Each scenario runs for <strong>2 minutes</strong> at <strong>5 packets/second</strong> with realistic protocol mixes
            </div>
            <button class="scenario" onclick="startScenario('web_browsing')" title="HTTP/HTTPS requests, DNS lookups, typical web traffic patterns">🌐 Web Browsing</button>
            <button class="scenario" onclick="startScenario('file_transfer')" title="FTP, SFTP, SCP traffic with large data transfers">📁 File Transfer</button>
            <button class="scenario" onclick="startScenario('video_streaming')" title="High-bandwidth UDP streams simulating video content">🎥 Video Streaming</button>
            <button class="scenario" onclick="startScenario('office_network')" title="Email, file shares, printing, DHCP - typical office protocols">🏢 Office Network</button>
            <button class="scenario" onclick="startScenario('malicious_activity')" title="Port scans, brute force, suspicious DNS - for IDS testing">🛡️ Security Testing</button>
        </div>

        <div class="section">
            <h3>⚡ Quick Start Traffic Generation</h3>
            <p><strong>One-click traffic generation with predefined settings:</strong></p>
            <div style="margin: 15px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; font-size: 14px;">
                <div><strong>HTTP Traffic:</strong> 2 packets/sec for 60 seconds → 192.168.100.20:80</div>
                <div><strong>DNS Traffic:</strong> 1 packet/sec for 60 seconds → 192.168.100.1:53</div>
                <div><strong>Mixed Traffic:</strong> 3 packets/sec for 120 seconds (HTTP, DNS, TCP, UDP mix)</div>
            </div>
            <button onclick="startHTTPTraffic()" title="Generates HTTP GET requests to simulate web browsing">Generate HTTP Traffic</button>
            <button onclick="startDNSTraffic()" title="Generates DNS queries for common domains">Generate DNS Traffic</button>
            <button onclick="startMixedTraffic()" title="Generates random mix of HTTP, DNS, TCP, and UDP traffic">Generate Mixed Traffic</button>
            <button class="stop" onclick="stopAllTraffic()">Stop All Traffic</button>
        </div>
        


        <div class="section">
            <h3>⚙️ Custom Traffic Configuration</h3>
            <p><strong>Configure your own traffic parameters for specific testing needs:</strong></p>
            <div style="margin: 10px 0; padding: 10px; background: #fff3cd; border-radius: 4px; font-size: 14px; color: #856404;">
                <strong>💡 Tips:</strong> Use HTTP for web traffic testing, DNS for name resolution testing, Mixed for general network activity simulation. Higher packet rates generate more events but may impact system performance.
            </div>
            <div>
                <label>Traffic Type:</label>
                <select id="trafficType" title="Choose the protocol type to generate">
                    <option value="http">HTTP (Web traffic to port 80)</option>
                    <option value="dns">DNS (Name resolution queries to port 53)</option>
                    <option value="mixed">Mixed (Random HTTP, DNS, TCP, UDP)</option>
                </select>
            </div>
            <div>
                <label>Target IP:</label>
                <input type="text" id="targetIP" value="192.168.100.20" placeholder="192.168.100.20" title="Destination IP address in virtual network range">
            </div>
            <div>
                <label>Duration (seconds):</label>
                <input type="number" id="duration" value="60" min="1" max="3600" title="How long to generate traffic (1-3600 seconds)">
            </div>
            <div>
                <label>Packets per second:</label>
                <input type="number" id="pps" value="2" min="1" max="100" title="Traffic rate - higher values create more events">
            </div>
            <button onclick="startCustomTraffic()">Start Custom Traffic</button>
        </div>
        
        <div class="section">
            <h3>📈 Status</h3>
            <div id="status"></div>
            <button onclick="getStatus()">Refresh Status</button>
        </div>
        
        <div class="section">
            <h3>📝 Activity Log</h3>
            <div id="log"></div>
        </div>
    </div>

    <script>
        function log(message) {
            const logDiv = document.getElementById('log');
            const timestamp = new Date().toLocaleTimeString();
            logDiv.innerHTML += `[${timestamp}] ${message}<br>\\n`;
            logDiv.scrollTop = logDiv.scrollHeight;
        }
        
        function showStatus(message, type = 'info') {
            const statusDiv = document.getElementById('status');
            statusDiv.className = `status ${type}`;
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
        

        
        async function startHTTPTraffic() {
            log('Starting HTTP traffic generation...');
            const result = await apiCall('start_traffic', {
                type: 'http',
                target_ip: '192.168.100.20',
                duration: 60,
                packets_per_second: 2
            });
            if (result && result.success) {
                showStatus('HTTP traffic generation started', 'success');
                log(`HTTP traffic started - Session ID: ${result.session_id}`);
            }
        }
        
        async function startDNSTraffic() {
            log('Starting DNS traffic generation...');
            const result = await apiCall('start_traffic', {
                type: 'dns',
                target_ip: '192.168.100.1',
                duration: 60,
                packets_per_second: 1
            });
            if (result && result.success) {
                showStatus('DNS traffic generation started', 'success');
                log(`DNS traffic started - Session ID: ${result.session_id}`);
            }
        }
        
        async function startMixedTraffic() {
            log('Starting mixed traffic generation...');
            const result = await apiCall('start_traffic', {
                type: 'mixed',
                duration: 120,
                packets_per_second: 3
            });
            if (result && result.success) {
                showStatus('Mixed traffic generation started', 'success');
                log(`Mixed traffic started - Session ID: ${result.session_id}`);
            }
        }
        
        async function startCustomTraffic() {
            const trafficType = document.getElementById('trafficType').value;
            const targetIP = document.getElementById('targetIP').value;
            const duration = parseInt(document.getElementById('duration').value);
            const pps = parseInt(document.getElementById('pps').value);
            
            log(`Starting custom ${trafficType} traffic...`);
            const result = await apiCall('start_traffic', {
                type: trafficType,
                target_ip: targetIP,
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
        
        // Auto-refresh status every 30 seconds
        setInterval(getStatus, 30000);
        

        
        // Initial status check
        getStatus();
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
        
        # Start scenario simulation
        thread = threading.Thread(
            target=generator.generate_simulation_traffic,
            args=("br-zeek-sim", scenario, duration, packets_per_second)
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
        target_ip = data.get('target_ip', '192.168.200.20')
        packets_per_second = data.get('packets_per_second', 2)
        
        # Generate unique session ID
        session_id = f"{traffic_type}_{int(time.time())}"
        
        # Create traffic generator
        generator = TrafficGenerator()
        
        # Start appropriate traffic generation in a thread
        if traffic_type == 'http':
            thread = threading.Thread(
                target=generator.generate_http_traffic,
                args=(target_ip, duration, packets_per_second)
            )
        elif traffic_type == 'dns':
            thread = threading.Thread(
                target=generator.generate_dns_traffic,
                args=(target_ip, duration, packets_per_second)
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
            'target_ip': target_ip,
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
            'sessions': active_sessions
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("Starting Virtual Network Traffic Generator Server...")
    print("Web interface available at: http://localhost:8080")
    print("Virtual network topology: 192.168.200.0/24")
    app.run(host='0.0.0.0', port=8080, debug=False)
