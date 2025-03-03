import os
import ssl
import sys
import json
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


    #
    # if pg_id == 'root' or pg_id == get_root_pg_id():
    #     # This duplicates the nipyapi_extended structure to the root case
    #     root_entity = get_process_group('root', 'id')
    #     root_entity.__setattr__('nipyapi_extended', root_flow)
    #     out.append(root_entity)
    # return out

def get_processor(api_client, identifier, identifier_type='name', greedy=True):
    """
    Filters the list of all Processors against the given identifier string in
    the given identifier_type field

    Args:
        identifier (str): The String to filter against
        identifier_type (str): The field to apply the filter to. Set in
            config.py
        greedy (bool): Whether to exact match (False) or partial match (True)

    Returns:
        None for no matches, Single Object for unique match,
        list(Objects) for multiple matches
    """
    assert isinstance(identifier, six.string_types)
    assert identifier_type in ['name', 'id']
    if identifier_type == 'id':
        out = nipyapi.nifi.ProcessorsApi(api_client).get_processor(identifier)
    else:
        obj = list_all_processors()
        out = nipyapi.utils.filter_obj(
            obj, identifier, identifier_type, greedy=greedy
        )
    return out

def list_all_processors(pg_id='root'):
    """
    Returns a flat list of all Processors under the provided Process Group

    Args:
        pg_id (str): The UUID of the Process Group to start from, defaults to
            the Canvas root

    Returns:
         list[ProcessorEntity]
    """
    assert isinstance(pg_id, six.string_types), "pg_id should be a string"

    if nipyapi.utils.check_version('1.7.0') <= 0:
        # Case where NiFi > 1.7.0
        targets = nipyapi.nifi.ProcessGroupsApi().get_processors(
            id=pg_id,
            include_descendant_groups=True
        )
        return targets.processors
    # Handle older NiFi instances
    out = []
    # list of child process groups
    pg_ids = [x.id for x in list_all_process_groups(pg_id)]
    # process target list
    for this_pg_id in pg_ids:
        procs = nipyapi.nifi.ProcessGroupsApi().get_processors(this_pg_id)
        if procs.processors:
            out += procs.processors
    return out

def get_processor(api_client, identifier, identifier_type='name', greedy=True):
    """
    Filters the list of all Processors against the given identifier string in
    the given identifier_type field

    Args:
        identifier (str): The String to filter against
        identifier_type (str): The field to apply the filter to. Set in
            config.py
        greedy (bool): Whether to exact match (False) or partial match (True)

    Returns:
        None for no matches, Single Object for unique match,
        list(Objects) for multiple matches
    """
    assert isinstance(identifier, six.string_types)
    assert identifier_type in ['name', 'id']
    if identifier_type == 'id':
        out = nipyapi.nifi.ProcessorsApi(api_client).get_processor(identifier)
    else:
        obj = list_all_processors()
        out = nipyapi.utils.filter_obj(
            obj, identifier, identifier_type, greedy=greedy
        )
    return out

def update_processor(api_client, processor, update, refresh=False):
    """
    Updates configuration parameters for a given Processor.

    An example update would be:
    nifi.ProcessorConfigDTO(scheduling_period='3s')

    Args:
        processor (ProcessorEntity): The Processor to target for update
        update (ProcessorConfigDTO): The new configuration parameters
        refresh (bool): Whether to refresh the Processor object state
          before applying the update

    Returns:
        (ProcessorEntity): The updated ProcessorEntity

    """
    if not isinstance(update, nipyapi.nifi.ProcessorConfigDTO):
        raise ValueError(
            "update param is not an instance of nifi.ProcessorConfigDTO"
        )
    with nipyapi.utils.rest_exceptions():
        if refresh:
            processor = get_processor(processor.id, 'id')
        return nipyapi.nifi.ProcessorsApi(api_client).update_processor(
            id=processor.id,
            body=nipyapi.nifi.ProcessorEntity(
                component=nipyapi.nifi.ProcessorDTO(
                    config=update,
                    id=processor.id
                ),
                revision=processor.revision,
            )
        )

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

def enable_controller_services(nifi_host, api_client, pg_id):

    # Set up form data and headers
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Authorization': api_client.default_headers['Authorization'],
        'Content-Type': 'application/json'
    }
    form_data = {
        "id": pg_id,
        "state":"ENABLED",
        "disconnectedNodeAcknowledged":False
    }

    url = f'{nifi_host}/flow/process-groups/{pg_id}/controller-services'
    response = requests.put(url, headers=headers, data=json.dumps(form_data), verify=False)

    # Log response status
    print(response.status_code)
    if response.status_code in [200, 201]:
        print("Controller services enabled.")
    else:
        print("Could not enable controller services.")
        print(url)
        print(response.text)
        sys.exit(1)

def main():

    DOCKER_HOST_OR_IP = os.getenv("DOCKER_HOST_OR_IP")
    
    VASTDB_ENDPOINT = os.getenv("VASTDB_ENDPOINT")
    VASTDB_ACCESS_KEY = os.getenv("VASTDB_ACCESS_KEY")
    VASTDB_SECRET_KEY = os.getenv("VASTDB_SECRET_KEY")
    VASTDB_TWITTER_INGEST_BUCKET = os.getenv("VASTDB_TWITTER_INGEST_BUCKET")
    VASTDB_TWITTER_INGEST_SCHEMA = os.getenv("VASTDB_TWITTER_INGEST_SCHEMA")
    VASTDB_TWITTER_INGEST_TABLE = os.getenv("VASTDB_TWITTER_INGEST_TABLE")
    VASTDB_BULK_IMPORT_BUCKET = os.getenv("VASTDB_BULK_IMPORT_BUCKET")
    VASTDB_BULK_IMPORT_SCHEMA = os.getenv("VASTDB_BULK_IMPORT_SCHEMA")
    VASTDB_BULK_IMPORT_TABLE = os.getenv("VASTDB_BULK_IMPORT_TABLE")
    VASTDB_WATERLEVEL_BUCKET = os.getenv("VASTDB_WATERLEVEL_BUCKET")
    VASTDB_WATERLEVEL_SCHEMA = os.getenv("VASTDB_WATERLEVEL_SCHEMA")
    
    S3A_ENDPOINT = os.getenv("S3A_ENDPOINT")
    S3A_ACCESS_KEY = os.getenv("S3A_ACCESS_KEY")
    S3A_SECRET_KEY = os.getenv("S3A_SECRET_KEY")
    S3A_BUCKET = os.getenv("S3A_BUCKET")

    nifi_host = f'https://{DOCKER_HOST_OR_IP}:18443/nifi-api'
    username = 'admin'
    password = '123456123456'

    # Set up NiFi connection
    api_client = setup_nifi_connection(nifi_host, username, password)

    ###############
    # S3 Controller
    ###############

    update=nipyapi.nifi.ControllerServiceDTO(
                properties={
                    'Access Key': S3A_ACCESS_KEY,
                    'Secret Key': S3A_SECRET_KEY
                }
            )
    controller = get_controller(api_client, 'S3A - AWSCredentialsProviderControllerService')
    if isinstance(controller, list):
        for c in controller:
            print(f'Updating S3A - AWSCredentialsProviderControllerService controller {c.id} {update}')
            updated = update_controller(c, update)
    else:
        print(f'Updating S3A - AWSCredentialsProviderControllerService controller {controller.id} {update}')
        updated = update_controller(controller, update)

    ###################
    # VastDB Controller
    ###################

    update=nipyapi.nifi.ControllerServiceDTO(
                properties={
                    'Access Key': VASTDB_ACCESS_KEY,
                    'Secret Key': VASTDB_SECRET_KEY
                }
            )
    controller = get_controller(api_client, 'VastDB - AWSCredentialsProviderControllerService')
    if isinstance(controller, list):
        for c in controller:
            print(f'Updating VastDB - AWSCredentialsProviderControllerService controller {c.id} {update}')
            updated = update_controller(c, update)
    else:
        print(f'Updating S3A - VastDB - AWSCredentialsProviderControllerService controller {controller.id} {update}')
        updated = update_controller(controller, update)


    ##################
    # Kafka Controller
    ##################

    update=nipyapi.nifi.ControllerServiceDTO(
                properties={
                    'bootstrap.servers': f'{DOCKER_HOST_OR_IP}:19092'
                }
            )
    controller = get_controller(api_client, 'Kafka3ConnectionService')
    if isinstance(controller, list):
        for c in controller:
            print(f'Updating Kafka3ConnectionService process {c.id} {update}')
            updated = update_controller(c, update)
    else:
        print(f'Updating Kafka3ConnectionService process {controller.id} {update}')
        updated = update_controller(controller, update)


    #####################
    # PutVastDB Processor
    #####################

    update=nipyapi.nifi.ProcessorConfigDTO(
                properties={
                    'VastDB Endpoint': VASTDB_ENDPOINT,
                    'VastDB Bucket': VASTDB_TWITTER_INGEST_BUCKET,
                    'VastDB Database Schema': VASTDB_TWITTER_INGEST_SCHEMA,
                    'VastDB Table Name': VASTDB_TWITTER_INGEST_TABLE
                }
            )
    processor = get_processor(api_client, 'PutVastDB', greedy=False)
    # there are multiple PutVastDB processors
    for p in processor:
        print(f'Updating PutVasDB process {p.id} {update}')
        updated = update_processor(api_client, p, update)

    ########################
    # ImportVastDB Processor
    ########################

    update=nipyapi.nifi.ProcessorConfigDTO(
                properties={
                    'VastDB Endpoint': f'{VASTDB_ENDPOINT}',
                    'VastDB Bucket': VASTDB_BULK_IMPORT_BUCKET,
                    'VastDB Database Schema': VASTDB_BULK_IMPORT_SCHEMA,
                    'VastDB Table Name': VASTDB_BULK_IMPORT_TABLE
                }
            )
    processor = get_processor(api_client, 'ImportVastDB')
    if isinstance(processor, list):
        for p in processor:
            print(f'Updating ImportVastDB process {p.id} {update}')
            updated = update_processor(api_client, p, update)
    else:
        print(f'Updating ImportVastDB process {processor.id} {update}')
        updated = update_processor(api_client, processor, update)

    ##################
    # ListS3 Processor
    ##################

    update=nipyapi.nifi.ProcessorConfigDTO(
                properties={
                    'Endpoint Override URL': f'{S3A_ENDPOINT}',
                    'Bucket': f'{S3A_BUCKET}'
                }
            )
    processor = get_processor(api_client, 'ListS3')
    if isinstance(processor, list):
        for p in processor:
            print(f'Updating ListS3 process {p.id} {update}')
            updated = update_processor(api_client, p, update)
    else:
        print(f'Updating ListS3 process {processor.id} {update}')
        updated = update_processor(api_client, processor, update)

    ###################################################################################################
    # Weather Flow
    ###################################################################################################

    ###################
    # AWS Controller Service
    ###################

    update=nipyapi.nifi.ControllerServiceDTO(
                properties={
                    'Access Key': VASTDB_ACCESS_KEY,
                    'Secret Key': VASTDB_SECRET_KEY
                }
            )
    controller = get_controller(api_client, 'Weather-AWSCredentialsProviderControllerService')
    if isinstance(controller, list):
        for c in controller:
            print(f'Updating Weather-AWSCredentialsProviderControllerService controller {c.id} {update}')
            updated = update_controller(c, update)
    else:
        print(f'Updating S3A - Weather-AWSCredentialsProviderControllerService controller {controller.id} {update}')
        updated = update_controller(controller, update)

    #####################
    # PutVastDB-Weather-Weatherstations Processor
    #####################

    update=nipyapi.nifi.ProcessorConfigDTO(
                properties={
                    'VastDB Endpoint': VASTDB_ENDPOINT,
                    'VastDB Bucket': VASTDB_WATERLEVEL_BUCKET,
                    'VastDB Database Schema': VASTDB_WATERLEVEL_SCHEMA,
                    'VastDB Table Name': 'weatherstations'
                }
            )
    processor = get_processor(api_client, 'PutVastDB-Weather-Weatherstations', greedy=False)
    # there are multiple PutVastDB processors
    if not processor:
        print(f'Processor PutVastDB-Weather-Weatherstations not Found')
        #sys.exit(1)
    elif isinstance(processor, list):
        for p in processor:
            print(f'Updating PutVastDB-Weather-Weatherstations process {p.id} {update}')
            updated = update_processor(api_client, p, update)
    else:
        print(f'Updating PutVastDB-Weather-Weatherstations process {p.id} {update}')
        updated = update_processor(api_client, processor, update)



    #####################
    # PutVastDB-Weather-Watermeasures Processor
    #####################

    update=nipyapi.nifi.ProcessorConfigDTO(
                properties={
                    'VastDB Endpoint': VASTDB_ENDPOINT,
                    'VastDB Bucket': VASTDB_WATERLEVEL_BUCKET,
                    'VastDB Database Schema': VASTDB_WATERLEVEL_SCHEMA,
                    'VastDB Table Name': 'watermeasures'
                }
            )
    processor = get_processor(api_client, 'PutVastDB-Weather-Watermeasures', greedy=False)
    # there are multiple PutVastDB processors
    if not processor:
        print(f'Processor PutVastDB-Weather-Watermeasures not Found')
        #sys.exit(1)
    elif isinstance(processor, list):
        for p in processor:
            print(f'Updating PutVastDB-Weather-Watermeasures process {p.id} {update}')
            updated = update_processor(api_client, p, update)
    else:
        print(f'Updating PutVastDB-Weather-Watermeasures process {p.id} {update}')
        updated = update_processor(api_client, processor, update)


    ###################################################################################################
    # Enable all controller services
    ###################################################################################################

    pg_name = "Demo_Flow"
    process_group = get_process_group(pg_name)
    enable_controller_services(nifi_host, api_client, process_group.id)

    pg_name = "Waterlevel_Flow"
    process_group = get_process_group(pg_name)
    enable_controller_services(nifi_host, api_client, process_group.id)
        
if __name__ == "__main__":
    main()
