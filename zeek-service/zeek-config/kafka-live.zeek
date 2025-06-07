# Simplified live traffic monitoring configuration for Zeek-Kafka with basic detection
@load base/protocols/conn
@load base/protocols/dns
@load base/protocols/http
@load base/protocols/ssl
@load base/protocols/ftp
@load base/protocols/ssh
@load base/protocols/smtp

# Load basic detection frameworks
@load base/frameworks/notice
@load policy/protocols/conn/known-hosts
@load policy/protocols/conn/known-services
@load policy/protocols/dns/detect-external-names
@load policy/protocols/ftp/detect
@load policy/protocols/http/detect-sqli
@load policy/protocols/http/detect-webapps
@load policy/protocols/ssh/detect-bruteforcing
@load policy/protocols/ssl/validate-certs
@load policy/tuning/json-logs
@load policy/misc/detect-traceroute
@load policy/frameworks/software/vulnerable
@load policy/frameworks/software/version-changes

# Load Kafka plugin
@load Seiso/Kafka

# Enable verbose logging
redef Log::enable_local_logging = T;
redef Log::default_rotation_interval = 1hr;
redef Log::default_logdir = "/logs";



# Configure detection thresholds to be more sensitive for demo purposes
redef SSH::password_guesses_limit = 3;

# Enhanced event handlers with more detailed logging
# Check environment variables and configure Kafka at load time
@if ( getenv("KAFKA_BROKER") == "" )
@error "KAFKA_BROKER environment variable not set!"
@endif

@if ( getenv("KAFKA_TOPIC") == "" )  
@error "KAFKA_TOPIC environment variable not set!"
@endif

# Configure Kafka with environment variables
redef Kafka::topic_name = getenv("KAFKA_TOPIC");
redef Kafka::kafka_conf = table(
    ["metadata.broker.list"] = getenv("KAFKA_BROKER"),
    ["client.id"] = "zeek-live-monitor",
    ["batch.num.messages"] = "1", # set to 1 to immediately save to kafka
    ["queue.buffering.max.ms"] = "10", # Reduced from 1000ms to 10ms for minimal latency
    ["linger.ms"] = "0", # Send immediately, don't wait
    ["acks"] = "1", # Only wait for leader acknowledgment
    ["retries"] = "3",
    ["delivery.timeout.ms"] = "5000",
    ["request.timeout.ms"] = "2000",
    ["socket.timeout.ms"] = "1000",
    ["debug"] = "broker,topic,msg",
    ["log_level"] = "7"
);

# Enable all active logs to be sent to Kafka
redef Kafka::send_all_active_logs = T;

# Use ISO8601 timestamps
redef Kafka::json_timestamps = JSON::TS_ISO8601;

# Tag JSON messages
redef Kafka::tag_json = T;

# Live monitoring specific settings
redef LogAscii::use_json = T;

# Fix for TCP checksum offloading in containerized environments
# Ignore invalid checksums that are common with NIC offloading
redef ignore_checksums = T;

event zeek_init() {
    print "🚀 Zeek initialized with enhanced detection capabilities";
    print fmt("📊 Kafka broker: %s", getenv("KAFKA_BROKER"));
    print fmt("📤 Kafka topic: %s", getenv("KAFKA_TOPIC"));
    print "🔧 Kafka plugin loaded and configured";
    print "🛡️ Security detection policies loaded";
}

event connection_established(c: connection) {
    local msg = fmt("[CONNECTION] %s:%s -> %s:%s (proto: %s)", 
                   c$id$orig_h, c$id$orig_p, c$id$resp_h, c$id$resp_p, c$id$proto);
    print msg;
}

event new_connection(c: connection) {
    local msg = fmt("[NEW_CONN] %s:%s -> %s:%s", 
                   c$id$orig_h, c$id$orig_p, c$id$resp_h, c$id$resp_p);
    print msg;
}

event dns_request(c: connection, msg: dns_msg, query: string, qtype: count, qclass: count) {
    local log_msg = fmt("[DNS] %s -> %s (type: %s)", c$id$orig_h, query, qtype);
    print log_msg;
    
    # Check for suspicious domains
    if (/\.(evil|bad|malware|botnet|phishing)\./ in query) {
        NOTICE([$note=DNS::External_Name,
                $msg=fmt("Suspicious DNS query: %s", query),
                $src=c$id$orig_h]);
    }
}

event http_request(c: connection, method: string, original_URI: string, unescaped_URI: string, version: string) {
    local log_msg = fmt("[HTTP] %s %s from %s to %s", method, original_URI, c$id$orig_h, c$id$resp_h);
    print log_msg;
    
    # Enhanced SQL injection detection with more patterns
    if (/union.*select|drop.*table|insert.*into|select.*from|delete.*from|update.*set|exec|script|javascript|vbscript|onload|onerror|eval\(|system\(|cmd/i in unescaped_URI) {
        NOTICE([$note=HTTP::SQL_Injection_Attacker,
                $msg=fmt("Potential SQL injection or code injection: %s", unescaped_URI),
                $src=c$id$orig_h]);
    }
    
    # Log all HTTP requests for debugging
    print fmt("[HTTP_DEBUG] Method: %s, URI: %s, Unescaped: %s", method, original_URI, unescaped_URI);
}

event http_reply(c: connection, version: string, code: count, reason: string) {
    local log_msg = fmt("[HTTP_REPLY] %s -> %s: %s %s", c$id$resp_h, c$id$orig_h, code, reason);
    print log_msg;
}

# Enhanced notice handling - using hook instead of event
hook Notice::notice(n: Notice::Info) {
    local notice_msg = fmt("[NOTICE] %s: %s (src: %s)", n$note, n$msg, n$src);
    print notice_msg;
}

# SSH brute force detection will be handled by the loaded policy
# The SSH::detect-bruteforcing policy will automatically generate notices

# Weird activity will be captured automatically by Zeek's built-in mechanisms
# All weird events are logged to weird.log and sent to Kafka automatically

# Simple packet counting
global packet_count = 0;
global connection_count = 0;

event new_packet(c: connection, p: pkt_hdr) {
    ++packet_count;
    if (packet_count % 100 == 0) {
        print fmt("[PACKET_COUNT] Processed %d packets", packet_count);
    }
}

event connection_state_remove(c: connection) {
    ++connection_count;
    if (connection_count % 10 == 0) {
        print fmt("[CONNECTION_COUNT] Processed %d connections", connection_count);
    }
}