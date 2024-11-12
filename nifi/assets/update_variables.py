import os
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
from nipyapi import canvas, config
from nipyapi.nifi.models.process_group_entity import ProcessGroupEntity
from nipyapi.nifi.models.process_group_dto import ProcessGroupDTO
from nipyapi.nifi.apis.process_groups_api import ProcessGroupsApi
import six

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
    """
    Set up NiFi connection with proper SSL configuration and authentication.
    """
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

def list_all_controllers(pg_id='root', descendants=True):
    """
    Lists all controllers under a given Process Group, defaults to Root
        Optionally recurses all child Process Groups as well
    Args:
        pg_id (str): String of the ID of the Process Group to list from
        descendants (bool): True to recurse child PGs, False to not

    Returns:
        None, ControllerServiceEntity, or list(ControllerServiceEntity)

    """
    assert isinstance(pg_id, six.string_types)
    assert isinstance(descendants, bool)
    handle = nipyapi.nifi.FlowApi()
    # Testing shows that descendant doesn't work on NiFi-1.1.2
    # Or 1.2.0, despite the descendants option being available
    if nipyapi.utils.check_version('1.2.0') >= 0:
        # Case where NiFi <= 1.2.0
        out = []
        if descendants:
            pgs = list_all_process_groups(pg_id)
        else:
            pgs = [get_process_group(pg_id, 'id')]
        for pg in pgs:
            new_conts = handle.get_controller_services_from_group(
                pg.id).controller_services
            # trim duplicates from inheritance
            out += [
                x for x in new_conts
                if x.id not in [y.id for y in out]
            ]
    else:
        # Case where NiFi > 1.2.0
        # duplicate trim already handled by server
        out = handle.get_controller_services_from_group(
            pg_id,
            include_descendant_groups=descendants
        ).controller_services
    return out


def get_controller(api_client, identifier, identifier_type='name', bool_response=False):
    """
    Retrieve a given Controller

    Args:
        identifier (str): ID or Name of a Controller to find
        identifier_type (str): 'id' or 'name', defaults to name
        bool_response (bool): If True, will return False if the Controller is
            not found - useful when testing for deletion completion

    Returns:

    """
    assert isinstance(identifier, six.string_types)
    assert identifier_type in ['name', 'id']
    handle = nipyapi.nifi.ControllerServicesApi(api_client)
    out = None
    try:
        if identifier_type == 'id':
            out = handle.get_controller_service(identifier)
        else:
            obj = list_all_controllers()
            out = nipyapi.utils.filter_obj(obj, identifier, identifier_type)
    except nipyapi.nifi.rest.ApiException as e:
        if bool_response:
            return False
        _raise(ValueError(e.body), e)
    return out


def update_controller(controller, update):
    """
    Updates the Configuration of a Controller Service

    Args:
        controller (ControllerServiceEntity): Target Controller to update
        update (ControllerServiceDTO): Controller Service configuration object
            containing the new config params and properties

    Returns:
        (ControllerServiceEntity)

    """
    assert isinstance(controller, nipyapi.nifi.ControllerServiceEntity)
    assert isinstance(update, nipyapi.nifi.ControllerServiceDTO)
    # Insert the ID into the update
    update.id = controller.id
    return nipyapi.nifi.ControllerServicesApi().update_controller_service(
        id=controller.id,
        body=nipyapi.nifi.ControllerServiceEntity(
            component=update,
            revision=controller.revision,
            id=controller.id
        )
    )


def main():


    DOCKER_HOST_OR_IP = os.getenv("DOCKER_HOST_OR_IP")
    VASTDB_ENDPOINT = os.getenv("VASTDB_ENDPOINT")
    VASTDB_ACCESS_KEY = os.getenv("VASTDB_ACCESS_KEY")
    VASTDB_SECRET_KEY = os.getenv("VASTDB_SECRET_KEY")

    S3_ENDPOINT = os.getenv("S3A_ENDPOINT")
    S3_ACCESS_KEY = os.getenv("S3A_ACCESS_KEY")
    S3_SECRET_KEY = os.getenv("S3A_SECRET_KEY")

    nifi_host = f'https://{DOCKER_HOST_OR_IP}:18443/nifi-api'
    username = 'admin'
    password = '123456123456'

    # Set up NiFi connection
    api_client = setup_nifi_connection(nifi_host, username, password)

    # S3 Controller
    update=nipyapi.nifi.ControllerServiceDTO(
                properties={
                    'Access Key': S3_ACCESS_KEY,
                    'Secret Key': S3_SECRET_KEY
                }
            )
    controller = get_controller(api_client, 'S3A - AWSCredentialsProviderControllerService')
    updated = update_controller(controller, update)

    # VastDB Controller
    update=nipyapi.nifi.ControllerServiceDTO(
                properties={
                    'Access Key': VASTDB_ACCESS_KEY,
                    'Secret Key': VASTDB_SECRET_KEY
                }
            )
    controller = get_controller(api_client, 'VastDB - AWSCredentialsProviderControllerService')
    updated = update_controller(controller, update)

if __name__ == "__main__":
    main()
