import os
import argparse
from supersetapiclient.client import SupersetClient

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Database connection manager.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing assets")
    return parser.parse_args()

def set_environment():
    """Set environment variables."""
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def get_docker_host():
    """Retrieve the Docker host or IP address."""
    docker_host = os.getenv("DOCKER_HOST_OR_IP")
    if not docker_host:
        raise EnvironmentError("DOCKER_HOST_OR_IP environment variable is not set.")
    return docker_host

def initialize_client(docker_host):
    """Initialize and return the Superset client."""
    client = SupersetClient(
        host=f"http://{docker_host}:8088",
        username="admin",
        password="admin",
    )
    print("Connected to Superset.")
    return client

def upload_file(client, docker_host, file_path, endpoint):
    """Upload a file to the specified Superset API endpoint."""
    with open(file_path, "rb") as file:
        files = {
            "formData": (os.path.basename(file_path), file, "application/zip")
        }
        url = f"http://{docker_host}:8088{endpoint}"
        response = client.session.post(url, data=data, files=files)

    # Print the response
    if response.status_code == 200:
        print(f"Upload successful for {file_path}: {response.text}")
    else:
        print(f"Error {response.status_code} for {file_path}: {response.text}")

if __name__ == "__main__":
    args = parse_arguments()
    set_environment()

    try:
        docker_host = get_docker_host()
        client = initialize_client(docker_host)

        data = {
            "passwords": "{}",  # Empty JSON map
            "overwrite": "true" if args.overwrite else "false",
            "ssh_tunnel_passwords": "{}",  # Empty JSON map
            "ssh_tunnel_private_keys": "{}",  # Empty JSON map
            "ssh_tunnel_private_key_passwords": "{}",  # Empty JSON map
        }

        upload_file(client, docker_host, '/generated/dataset_export_tweets.zip', '/api/v1/dataset/import/')
        upload_file(client, docker_host, '/generated/dashboard_export_tweets.zip', '/api/v1/dashboard/import/')
        upload_file(client, docker_host, '/generated/dashboard_export_netflow.zip', '/api/v1/dashboard/import/')
        upload_file(client, docker_host, '/generated/saved_query_export_catalog.zip', '/api/v1/saved_query/import/')
        upload_file(client, docker_host, '/generated/saved_query_export_auditlog.zip', '/api/v1/saved_query/import/')
        upload_file(client, docker_host, '/generated/saved_query_export_latest_tweets.zip', '/api/v1/saved_query/import/')
        upload_file(client, docker_host, '/generated/saved_query_export_tweets_in_iceberg.zip', '/api/v1/saved_query/import/')
        upload_file(client, docker_host, '/generated/saved_query_export_copy_tweets.zip', '/api/v1/saved_query/import/')
        upload_file(client, docker_host, '/generated/saved_query_export_netflow.zip', '/api/v1/saved_query/import/')

    except EnvironmentError as e:
        print(f"Environment setup error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
