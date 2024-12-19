import pyarrow as pa
import vastdb
import time
import random
import datetime
import os
import sys

hosts = [f"192.168.0.{i}" for i in range(1, 201)]
external_ips = [f"10.0.{i}.{j}" for i in range(0,255) for j in range(1, 255)]  # Simulate external IPs
protocols = ['TCP', 'UDP']
ports = [80, 443, 22, 8080, 53]  # Common ports

columns = pa.schema([
    ('timestamp', pa.timestamp('ms', tz=None)),
    ('src_ip', pa.utf8()),
    ('dst_ip', pa.utf8()),
    ('src_port', pa.int32()),
    ('dst_port', pa.int32()),
    ('protocol', pa.utf8()),
    ('duration', pa.int64()),
    ('bytes_sent', pa.int64()),
    ('packets', pa.int64())
])

def current_milli_time():
    return int(time.time() * 1000)

def generate_flows():
    current_time = current_milli_time()
    netflow_ts = []
    src_ip = []
    dst_ip = []
    src_port = []
    dst_port = []
    protocol = []
    duration = []
    bytes_sent = []
    packets = []
    for i in range(1, ( 3000 + random.randint(0,7000) ) ):
        ms = current_time + random.randint(0,1000)
        netflow_ts.append( datetime.datetime.fromtimestamp(ms / 1e3) )
        src_ip.append( random.choice(hosts) )
        dst_ip.append( random.choice(external_ips) )
        src_port.append( random.randint(49152, 65535) )
        dst_port.append( random.choice(ports) )
        protocol.append( random.choice(protocols) )
        duration.append( random.randint(200,1200) )
        bytes_sent.append( random.randint(500, 5000) )
        packets.append( random.randint(5, 50) )

    flow_list = pa.Table.from_pydict(
        dict(
            zip(columns.names, (
                netflow_ts,
                src_ip,
                dst_ip,
                src_port,
                dst_port,
                protocol,
                duration,
                bytes_sent,
                packets
            ))
        ), schema = columns
    )

    return flow_list

######

VASTDB_ENDPOINT = os.getenv("VASTDB_ENDPOINT")
VASTDB_ACCESS_KEY = os.getenv("VASTDB_ACCESS_KEY")
VASTDB_SECRET_KEY = os.getenv("VASTDB_SECRET_KEY")

VASTDB_NETFLOW_BUCKET = os.getenv("VASTDB_NETFLOW_BUCKET")
VASTDB_NETFLOW_SCHEMA = os.getenv("VASTDB_NETFLOW_SCHEMA")
VASTDB_NETFLOW_TABLE = os.getenv("VASTDB_NETFLOW_TABLE")

if not VASTDB_ENDPOINT:
    print("VASTDB_ENDPOINT env var not found.")
    sys.exit(1)

######

session = vastdb.connect(
    endpoint=VASTDB_ENDPOINT,
    access=VASTDB_ACCESS_KEY,
    secret=VASTDB_SECRET_KEY
    )

with session.transaction() as tx:
    bucket = tx.bucket(VASTDB_NETFLOW_BUCKET)
    schema = bucket.create_schema(VASTDB_NETFLOW_SCHEMA, fail_if_exists=False)
    table = schema.create_table(VASTDB_NETFLOW_TABLE, columns, fail_if_exists=False)

    for m in range(1,5):
        table.insert( generate_flows() )

    #time.sleep(9.700)
