# Simplified live traffic monitoring configuration for Zeek-Kafka with debugging
@load base/protocols/conn
@load base/protocols/dns
@load base/protocols/http
@load base/protocols/ssl
@load base/protocols/ftp
@load base/protocols/ssh
@load base/protocols/smtp
@load Seiso/Kafka

# Enable verbose logging
redef Log::enable_local_logging = T;
redef Log::default_rotation_interval = 1hr;
redef Log::default_logdir = "/logs";

# Kafka configuration with debug settings
redef Kafka::topic_name = "zeek-live-logs";
redef Kafka::kafka_conf = table(
    ["metadata.broker.list"] = "172.200.204.1:9092",
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

# Enhanced event handlers with more detailed logging
event zeek_init() {
    print "🚀 Zeek initialized - starting packet capture";
    print fmt("📊 Kafka broker: %s", "172.200.204.1:9092");
    print fmt("📤 Kafka topic: %s", "zeek-live-logs");
    print "🔧 Kafka plugin loaded and configured";
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
}

event http_request(c: connection, method: string, original_URI: string, unescaped_URI: string, version: string) {
    local log_msg = fmt("[HTTP] %s %s from %s to %s", method, original_URI, c$id$orig_h, c$id$resp_h);
    print log_msg;
}

event http_reply(c: connection, version: string, code: count, reason: string) {
    local log_msg = fmt("[HTTP_REPLY] %s -> %s: %s %s", c$id$resp_h, c$id$orig_h, code, reason);
    print log_msg;
}

# Kafka status logging - removed non-existent event handler
# The Kafka plugin will handle message delivery internally

# Simple packet counting
global packet_count = 0;

event new_packet(c: connection, p: pkt_hdr) {
    ++packet_count;
    if (packet_count % 100 == 0) {
        print fmt("[PACKET_COUNT] Processed %d packets", packet_count);
    }
}
