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

# # Configure logging
# logging.basicConfig(level=logging.ERROR)
# urllib3_logger = logging.getLogger("urllib3")
# urllib3_logger.setLevel(logging.ERROR)
# nipyapi_logger = logging.getLogger("nipyapi")
# nipyapi_logger.setLevel(logging.ERROR)

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
    # Configure NiFi connection settings
    nipyapi.config.nifi_config.host = host_url
    nipyapi.config.nifi_config.verify_ssl = False
    nipyapi.config.registry_config.verify_ssl = False

    # Create custom session with SSL adapter
    session = requests.Session()
    session.verify = False
    adapter = SSLAdapter()
    session.mount('https://', adapter)

    try:
        # Create main API client
        api_client = ApiClient()
        api_client.host = host_url
        api_client.verify_ssl = False
        api_client.rest_client.pool_manager = adapter.poolmanager

        # Configure authentication using AccessApi
        access_api = AccessApi(api_client)
        access_token = access_api.create_access_token(username=username, password=password)

        # Set the authorization header with the obtained token
        api_client.default_headers['Authorization'] = f'Bearer {access_token}'

        return api_client
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        raise


def create_parameter_provider(api_client, env_vars):
    """
    Create a parameter provider with specified environment variables
    """
    controller_api = ControllerApi(api_client)
    
    param_provider_body = ParameterProviderEntity(
        revision={'version': 0},
        component=ParameterProviderDTO(
            name="MyParameterProvider",
            type="org.apache.nifi.parameter.EnvironmentVariableParameterProvider",
            properties={
                "environment-variable-inclusion-strategy": "comma-separated",
                "include-environment-variables": ','.join(env_vars)
            }
        )
    )
    
    try:
        # Create the parameter provider
        created_provider = controller_api.create_parameter_provider(
            body=param_provider_body
        )

        print(f"Parameter Provider created successfully. {created_provider}")
        return created_provider
    except Exception as e:
        print(f"Error creating Parameter Provider: {str(e)}")
        raise

def main():
    # Suppress SSL warnings
    requests.packages.urllib3.disable_warnings()

    ####### CHANGE ME #######
    # NiFi host URL and credentials
    nifi_host = 'https://se-var-vastdb-ingest:18443/nifi-api'
    username = 'admin'
    password = '123456123456'
    ####### CHANGE ME #######
    
    # Environment variables to include
    env_vars = ['S3A_ACCESS_KEY', 'S3A_SECRET_KEY', 'VASTDB_ACCESS_KEY', 'VASTDB_SECRET_KEY',]
    
    try:
        # Setup connection with authentication
        api_client = setup_nifi_connection(nifi_host, username, password)
        
        # Create parameter provider
        provider = create_parameter_provider(api_client, env_vars)
        
        return provider
    except Exception as e:
        print(f"Failed to setup NiFi parameter provider: {str(e)}")
        raise

if __name__ == "__main__":
    main()
