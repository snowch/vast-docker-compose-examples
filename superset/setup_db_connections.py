import os
import json
import argparse
from supersetapiclient.client import SupersetClient

# ANSI escape code for red text
RED = "\033[91m"
# Reset color to default
RESET = "\033[0m"

# Set environment variable for insecure OAuth transport
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Set the Docker host or IP address
DOCKER_HOST_OR_IP = os.getenv("DOCKER_HOST_OR_IP")

# Initialize Superset client
client = SupersetClient(
    host=f"http://{DOCKER_HOST_OR_IP}:8088",
    username="admin",
    password="admin",
)

print("Connected.")

# Common database details template
base_data = {
    "engine": "trino",
    "configuration_method": "sqlalchemy_form",
    "engine_information": {
        "disable_ssh_tunneling": False,
        "supports_file_upload": True
    },
    "sqlalchemy_uri_placeholder": "engine+driver://user:password@host:port/dbname[?key=value&key=value...]",
    "extra": "{\"allows_virtual_table_explore\":true,\"engine_params\":{\"connect_args\":{\"http_scheme\":\"https\"}}}",
    "expose_in_sqllab": True,
    "allow_ctas": True,
    "allow_cvas": True,
    "allow_dml": True,
    "allow_file_upload": True,
}

# Data for the "Trino VastDB" database
vastdb_data = {
    **base_data,
    "database_name": "Trino VastDB",
    "sqlalchemy_uri": f"trino://admin@{DOCKER_HOST_OR_IP}:8443/vast?verify=false"
}

# Data for the "Trino Vast Iceberg" database
iceberg_data = {
    **base_data,
    "database_name": "Trino Vast Iceberg",
    "sqlalchemy_uri": f"trino://admin@{DOCKER_HOST_OR_IP}:8443/iceberg?verify=false"
}

# Data for the "Trino Vast Hive" database
hive_data = {
    **base_data,
    "database_name": "Trino Vast Hive",
    "sqlalchemy_uri": f"trino://admin@{DOCKER_HOST_OR_IP}:8443/iceberg?verify=false"
}

def delete_database_if_exists(database_name, force_delete):
    # Fetch list of databases
    response = client.get(f"http://{DOCKER_HOST_OR_IP}:8088/api/v1/database/")
    databases = response.json().get("result", [])
    
    # Find the database ID by name
    for db in databases:
        if db.get("database_name") == database_name:
            if not force_delete:
                print(f"{RED}\nDatabase '{database_name}' exists, but deletion was not forced.")
                print(f"To delete this database, rerun the script with the --force-delete flag.\n{RESET}")
                return False

            db_id = db.get("id")
            print(f"Database '{database_name}' found, deleting...")
            # Delete the database
            delete_response = client.delete(f"http://{DOCKER_HOST_OR_IP}:8088/api/v1/database/{db_id}")
            if delete_response.status_code == 200:
                print(f"Database '{database_name}' deleted successfully.")
            else:
                print(f"Failed to delete database '{database_name}'")
            return True

    print(f"Database '{database_name}' does not exist.")
    return False

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Database connection manager.")
parser.add_argument("--force-delete", action="store_true", help="Force delete existing databases")
args = parser.parse_args()

# Delete the databases if they exist
delete_database_if_exists("Trino VastDB", args.force_delete)
delete_database_if_exists("Trino Vast Iceberg", args.force_delete)
delete_database_if_exists("Trino Vast Hive", args.force_delete)

print("""
#########################################
Attempting to create database connection.
#########################################
""")

# Post requests to create databases
response_vastdb = client.post(
    url=f"http://{DOCKER_HOST_OR_IP}:8088/api/v1/database/",
    json=vastdb_data
)

response_iceberg = client.post(
    url=f"http://{DOCKER_HOST_OR_IP}:8088/api/v1/database/",
    json=iceberg_data
)

response_hive = client.post(
    url=f"http://{DOCKER_HOST_OR_IP}:8088/api/v1/database/",
    json=hive_data
)

# Print the response for both database creation requests
print("VastDB Response:", response_vastdb.text)
print("Iceberg Response:", response_iceberg.text)
print("Hive Response:", response_hive.text)
