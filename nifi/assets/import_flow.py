import ssl
import logging
import os
import requests
import six
import sys
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
import nipyapi
from nipyapi.nifi.api_client import ApiClient
from nipyapi.nifi.apis.access_api import AccessApi
from nipyapi import config

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


def get_root_pg_id(api_client):
    """
    Convenience function to return the UUID of the Root Process Group

    Returns (str): The UUID of the root PG
    """
    return nipyapi.nifi.FlowApi(api_client).get_process_group_status('root') \
        .process_group_status.id

def recurse_flow(pg_id='root'):
    """
    Returns information about a Process Group and all its Child Flows.
    Recurses the child flows by appending each process group with a
    'nipyapi_extended' parameter which contains the child process groups, etc.
    Note: This previously used actual recursion which broke on large NiFi
        environments, we now use a task/list update approach

    Args:
        pg_id (str): The Process Group UUID

    Returns:
         (ProcessGroupFlowEntity): enriched NiFi Flow object
    """
    assert isinstance(pg_id, six.string_types), "pg_id should be a string"

    out = get_flow(pg_id)
    tasks = [(x.id, x) for x in out.process_group_flow.flow.process_groups]
    while tasks:
        this_pg_id, this_parent_obj = tasks.pop()
        this_flow = get_flow(this_pg_id)
        this_parent_obj.__setattr__(
            'nipyapi_extended',
            this_flow
        )
        tasks += [(x.id, x) for x in
                  this_flow.process_group_flow.flow.process_groups]
    return out

def get_flow(pg_id='root'):
    """
    Returns information about a Process Group and flow.

    This surfaces the native implementation, for the recursed implementation
    see 'recurse_flow'

    Args:
        pg_id (str): id of the Process Group to retrieve, defaults to the root
            process group if not set

    Returns:
         (ProcessGroupFlowEntity): The Process Group object
    """
    assert isinstance(pg_id, six.string_types), "pg_id should be a string"
    with nipyapi.utils.rest_exceptions():
        return nipyapi.nifi.FlowApi().get_flow(pg_id)


def get_process_group_status(pg_id='root', detail='names'):
    """
    Returns an entity containing the status of the Process Group.
    Optionally may be configured to return a simple dict of name:id pairings

    Note that there is also a 'process group status' command available, but it
    returns a subset of this data anyway, and this call is more useful

    Args:
        pg_id (str): The UUID of the Process Group
        detail (str): 'names' or 'all'; whether to return a simple dict of
            name:id pairings, or the full details. Defaults to 'names'

    Returns:
         (ProcessGroupEntity): The Process Group Entity including the status
    """
    assert isinstance(pg_id, six.string_types), "pg_id should be a string"
    assert detail in ['names', 'all']
    raw = nipyapi.nifi.ProcessGroupsApi().get_process_group(id=pg_id)
    if detail == 'names':
        out = {
            raw.component.name: raw.component.id
        }
        return out
    return raw

def get_process_group(identifier, identifier_type='name', greedy=True):
    """
    Filters the list of all process groups against a given identifier string
    occurring in a given identifier_type field.

    Args:
        identifier (str): the string to filter the list for
        identifier_type (str): the field to filter on, set in config.py
        greedy (bool): True for partial match, False for exact match

    Returns:
        None for no matches, Single Object for unique match,
        list(Objects) for multiple matches

    """
    assert isinstance(identifier, six.string_types)
    assert identifier_type in ['name', 'id']
    with nipyapi.utils.rest_exceptions():
        if identifier_type == 'id' or identifier == 'root':
            # assuming unique fetch of pg id, 'root' is special case
            # implementing separately to avoid recursing entire canvas
            out = nipyapi.nifi.ProcessGroupsApi().get_process_group(identifier)
        else:
            obj = list_all_process_groups()
            out = nipyapi.utils.filter_obj(
                obj, identifier, identifier_type, greedy=greedy)
    return out

def list_all_process_groups(pg_id='root'):
    """
    Returns a flattened list of all Process Groups on the canvas.
    Potentially slow if you have a large canvas.

    Note that the ProcessGroupsApi().get_process_groups(pg_id) command only
    provides the first layer of pgs, whereas this trawls the entire canvas

    Args:
        pg_id (str): The UUID of the Process Group to start from, defaults to
            the Canvas root

    Returns:
         list[ProcessGroupEntity]

    """
    assert isinstance(pg_id, six.string_types), "pg_id should be a string"

    def flatten(parent_pg):
        """
        Recursively flattens the native datatypes into a generic list.
        Note that the root is a special case as it has no parent

        Args:
            parent_pg (ProcessGroupEntity): object to flatten

        Yields:
            Generator for all ProcessGroupEntities, eventually
        """
        for child_pg in parent_pg.process_group_flow.flow.process_groups:
            for sub in flatten(child_pg.nipyapi_extended):
                yield sub
            yield child_pg

    # Recurse children
    root_flow = recurse_flow(pg_id)
    # Flatten list of children with extended detail
    out = list(flatten(root_flow))
    # update parent with flattened list of extended child detail
    root_entity = get_process_group(pg_id, 'id')
    root_entity.__setattr__('nipyapi_extended', root_flow)
    out.append(root_entity)
    return out

def upload_flow_definition(nifi_host, api_client, file_path, pg_name, positionX, positionY):

    process_group = get_process_group(pg_name)
    if process_group:
        print(f"ERROR: {pg_name} progress group already exists. Manually delete it and try again.")
        sys.exit(1)

    # File to upload
    with open(file_path, 'rb') as f:
        file_data = f.read()

    fname = file_path.split('/')[1]

    # Set up form data and headers
    files = {'file': (fname, file_data, 'application/json')}
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': api_client.default_headers['Authorization'],
    }
    form_data = {
        'id': 'root',
        'groupName': pg_name,
        'positionX': positionX,
        'positionY': positionY,
        'clientId': 'xxxxx',
        'disconnectedNodeAcknowledged': 'false'
    }

    # Upload file to NiFi
    url = f'{nifi_host}/process-groups/root/process-groups/upload'
    response = requests.post(url, headers=headers, files=files, data=form_data, verify=False)

    # Log response status
    print(response.status_code)
    # print(response.text)

def main():

    DOCKER_HOST_OR_IP = os.getenv("DOCKER_HOST_OR_IP")

    nifi_host = f'https://{DOCKER_HOST_OR_IP}:18443/nifi-api'
    username = 'admin'
    password = '123456123456'

    # Set up NiFi connection
    api_client = setup_nifi_connection(nifi_host, username, password)

    root_pg_id = get_root_pg_id(api_client)
    print(f'Root process group ID: {root_pg_id}')

    upload_flow_definition(nifi_host, api_client, '/app/NiFi_Flow.json', 'Demo_Flow', 100, 100)
    upload_flow_definition(nifi_host, api_client, '/app/NiFi_Waterlevel_Flow.json', 'Waterlevel_Flow', 100, 300)

if __name__ == "__main__":
    main()
