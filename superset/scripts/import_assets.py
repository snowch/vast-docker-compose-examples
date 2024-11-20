import os
import json
import argparse
import requests
from supersetapiclient.client import SupersetClient


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

data = {
    "passwords": "{}",  # Empty JSON map
    "overwrite": "false",  # Boolean as string
    "ssh_tunnel_passwords": "{}",  # Empty JSON map
    "ssh_tunnel_private_keys": "{}",  # Empty JSON map
    "ssh_tunnel_private_key_passwords": "{}",  # Empty JSON map
}

file_path = '/generated/dataset_export_tweets.zip'
with open(file_path, "rb") as file:
    files = {
        "formData": (file_path.split("/")[-1], file, "application/zip")
    }
    url=f"http://{DOCKER_HOST_OR_IP}:8088/api/v1/dataset/import/"

    print(client.session.headers)
    response = client.session.post(url, data=data, files=files)

# Print the response
if response.status_code == 200:
    print("Upload successful:", response.json())
else:
    print(f"Error {response.status_code}: {response.text}")