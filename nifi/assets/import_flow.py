import ssl
import logging
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from nipyapi.nifi import ParameterProviderEntity, ParameterProviderDTO
from nipyapi.nifi.api_client import ApiClient
from nipyapi.nifi.apis.controller_api import ControllerApi
from nipyapi.nifi.apis.flow_api import FlowApi
from nipyapi.nifi.apis.access_api import AccessApi
from nipyapi import canvas, config
from nipyapi.nifi.models.process_group_entity import ProcessGroupEntity
from nipyapi.nifi.models.process_group_dto import ProcessGroupDTO
from nipyapi.nifi.apis.process_groups_api import ProcessGroupsApi
import six

DOCKER_HOST_OR_IP = os.getenv("DOCKER_HOST_OR_IP")

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# Configure logging
logging.basicConfig(level=logging.ERROR)
urllib3_logger = logging.getLogger("urllib3")
urllib3_logger.setLevel(logging.ERROR)
nipyapi_logger = logging.getLogger("nipyapi")
nipyapi_logger.setLevel(logging.ERROR)

class SSLAdapter(HTTPAdapter):
    """Custom adapter to handle SSL without certificate verification."""
    def init_poolmanager(self, connections, maxsize, block=False):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLS,
            ssl_context=context
        )

def setup_nifi_connection(host_url, username, password):

    adapter = SSLAdapter()

    # Create custom session with SSL adapter
    session = requests.Session()
    session.verify = False
    session.mount('https://', adapter)

    # Create API client and configure authentication
    api_client = ApiClient()
    api_client.host = host_url
    api_client.verify = False
    api_client.rest_client.pool_manager = adapter.poolmanager

    # Configure NiFi connection settings
    access_api = AccessApi(api_client)
    config.nifi_config.api_client = api_client
    config.nifi_config.host = host_url
    config.nifi_config.verify_ssl = False

    try:
        # Authenticate and get access token
        response = session.post(
            f"{host_url}/access/token",
            data={"username": username, "password": password}
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Authentication failed with status code {response.status_code}")

        access_token = response.text.strip()  # Strip any whitespace
        if not access_token:
            raise Exception("No access token found in response.")

        # Set authorization headers
        session.headers.update({"Authorization": f"Bearer {access_token}"})

        # Transfer cookies to NiFi configuration
        config.nifi_config.cookies = session.cookies

        # Set the Authorization header on ApiClient
        api_client.default_headers['Authorization'] = f'Bearer {access_token}'

        # Transfer cookies from session to ApiClient
        for cookie in session.cookies:
            api_client.set_default_header("Cookie", f"{cookie.name}={cookie.value}")

        print("NiFi connection successfully set up with authentication.")
        return api_client

    except Exception as e:
        print(f"Authentication error: {str(e)}")
        raise

def main():
    """Main function to upload NiFi flow JSON file."""
    nifi_host = f'https://{DOCKER_HOST_OR_IP}:18443/nifi-api'
    username = 'admin'
    password = '123456123456'

    # Set up NiFi connection
    api_client = setup_nifi_connection(nifi_host, username, password)

    # File to upload
    file_path = '/assets/NiFi_Flow.json'
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Set up form data and headers
    pg_name = "Demo_Flow"
    files = {'file': ('NiFi_Flow.json', file_data, 'application/json')}
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': api_client.default_headers['Authorization'],
    }
    form_data = {
        'id': 'root',
        'groupName': pg_name,
        'positionX': '100',
        'positionY': '100',
        'clientId': 'xxxxx',
        'disconnectedNodeAcknowledged': 'false'
    }

    # Upload file to NiFi
    url = f'{nifi_host}/process-groups/root/process-groups/upload'
    response = requests.post(url, headers=headers, files=files, data=form_data, verify=False)

    # Log response status
    print(response.status_code)
    # print(response.text)

if __name__ == "__main__":
    main()
