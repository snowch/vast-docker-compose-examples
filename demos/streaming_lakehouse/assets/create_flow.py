#!/usr/bin/env python

import ssl
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import nipyapi
from nipyapi.nifi import ParameterProviderEntity, ParameterProviderDTO
from nipyapi.nifi.api_client import ApiClient
from nipyapi.nifi.apis.controller_api import ControllerApi
from nipyapi.nifi.apis.flow_api import FlowApi
from nipyapi.nifi.apis.access_api import AccessApi
from nipyapi import canvas,config
from nipyapi.nifi.models.process_group_entity import ProcessGroupEntity
from nipyapi.nifi.models.process_group_dto import ProcessGroupDTO
from nipyapi.nifi.apis.process_groups_api import ProcessGroupsApi

class SSLAdapter(HTTPAdapter):        
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
    """
    Set up NiFi connection with proper SSL configuration and authentication
    """
    adapter = SSLAdapter()

    # Create custom session with SSL adapter
    session = requests.Session()
    session.verify = False
    session.mount('https://', adapter)

    # Create main API client
    api_client = ApiClient()
    api_client.host = host_url
    api_client.verify = False
    api_client.rest_client.pool_manager = adapter.poolmanager

    # Configure authentication using AccessApi
    access_api = AccessApi(api_client)
    config.nifi_config.api_client = api_client

    # Configure NiFi connection settings
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

        # Obtain and check the access token
        access_token = response.text.strip()  # Strip any whitespace
        if not access_token:
            raise Exception("No access token found in response.")

        # Set the authorization header in session
        session.headers.update({"Authorization": f"Bearer {access_token}"})

        # Apply cookies from session to nipyapi configuration
        config.nifi_config.cookies = session.cookies

        # Ensure the api_client is properly initialized
        api_client = config.nifi_config.api_client
        if api_client is None:
            raise Exception("API client not initialized in nipyapi config.")

        # Set the Authorization header on the ApiClient
        api_client.default_headers['Authorization'] = f'Bearer {access_token}'
        
        # Transfer each cookie from session to ApiClient
        for cookie in session.cookies:
            api_client.set_default_header("Cookie", f"{cookie.name}={cookie.value}")

        print("NiFi connection successfully set up with authentication.")
        
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        raise


def create_flow():
    
    root_id = nipyapi.canvas.get_root_pg_id()
    root_process_group = nipyapi.canvas.get_process_group(root_id, 'id')
    
    pg_name = 'weather-python'
    existing_pg = nipyapi.canvas.get_process_group(pg_name, identifier_type='name')
    if existing_pg is None:
        my_pg = nipyapi.canvas.create_process_group(
            parent_pg=root_process_group,
            new_pg_name=pg_name,
            location=(400.0, 100.0)
        )
        print(f"Created new process group: {pg_name}")
    else:
        my_pg = existing_pg
        print(f"Using existing process group: {pg_name}")
    
    processor_name_gff = 'GenerateFlowFile'
    existing_processors_gff = nipyapi.canvas.get_processor('GenerateFlowFile')
    if existing_processors_gff is None:
        generate_flowfile_processor = nipyapi.canvas.create_processor(
            parent_pg=my_pg,
            processor=nipyapi.canvas.get_processor_type('GenerateFlowFile'),
            name=processor_name_gff,
            location=(500.0, 100.0),
            config=nipyapi.nifi.ProcessorConfigDTO(
                properties={
                    'Custom Text': 'Example text',
                    'File Size': '1 KB',
                    'time': '${time:format("yyyy-MM-dd HH:mm:ss", "GMT")}'
                },
                scheduling_period='10 sec',
                scheduling_strategy='TIMER_DRIVEN'
            )
        )
        print(f"Created new processor: {processor_name_gff}")
    else:
        generate_flowfile_processor = existing_processors_gff
        print(f"Using existing processor: {processor_name_gff}")

def main():
    # Suppress SSL warnings
    requests.packages.urllib3.disable_warnings()
    
    nifi_host = 'https://se-var-vastdb-ingest:18443/nifi-api'
    username = 'admin'
    password = '123456123456'
    
    try:
        setup_nifi_connection(nifi_host, username, password)
        create_flow()
    
    except Exception as e:
        print(f"Failed to setup NiFi parameter provider: {str(e)}")
        raise

if __name__ == "__main__":
    main()
