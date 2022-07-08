"""EIQ APIs and QRadara APIs defined to fetch data from eiq platform.

Process data to ingest in Qradar  .
"""
import json
import datetime
import time

from app.configs.sighting import SIGHTING_SCHEMA
from app.checkpoint_store import read_checkpoint, write_checkpoint
from app.database.handler import insert_data_to_table
from app.collector.request import Request
from app.configs.datastore import DATA_STORE_DIR, DATA_STORE_SETUP_FILE
from app.configs.eiq_api import (
    EIQ_ENTITIES,
    EIQ_OBSERVABLES_BY_ID,
    EIQ_OUTGOING_FEEDS,
    EIQ_PERMISSIONS,
    EIQ_USER_PERMISSIONS,
    QRADAR_BULK_LOAD,
    QRADAR_REFERENCE_TABLE,
    QRADRAR_REFERENCE_DELETE_TASKS,
)
from app.constants.defaults import (
    DEFAULT_LIMIT,
    DEFAULT_MAX_RETRY,
    DEFAULT_MAX_RETRY_USER_PERMISSIONS,
    DEFAULT_PAGE_SIZE,
    DEFAULT_RETRY_INTERVAL,
    DEFAULT_TIMEOUT,
    DEFAULT_TIMEOUT_USER_PERMISSIONS,
    DEFAULT_VERIFY_SSL,
)
from app.constants.general import (
    ALNIC,
    API_KEY,
    AUTH_USER,
    BACKFILL_TIME,
    BEARER_TOKEN,
    CONFIDENCE_KEY,
    COUNT,
    CREATED_AT,
    DATA,
    DELETE,
    DESC_BY_LAST_UPDATED_AT,
    DESC_KEY,
    EIQ,
    EIQ_,
    EIQ_SIGHTING,
    EIQ_VALUE,
    ELEMENT_TYPE,
    FILTER_LAST_UPDATED_AT,
    FILTER_OUTGOING_FEEDS,
    GET,
    GLUE_COLONS,
    HEADERS,
    HOST,
    HTTPS,
    ID,
    INGEST_TIME_KEY,
    KEY_NAME,
    KEY_NAME_TYPES,
    LAST_UPDATED_AT,
    LIMIT,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_INFO,
    MALICIOUSNESS,
    MAX_RETRY,
    META,
    MODIFY_EXTRACTS,
    META_KEY,
    NAME,
    NO_AUTH,
    OBSERVABLE_TYPES,
    OBSERVABLES,
    OFFSET,
    OUTER_KEY_LABEL,
    OUTGOING_FEEDS,
    PAGE_SIZE,
    PERMISSIONS,
    PLUS,
    POST,
    QRADAR_SECURITY_TOKEN,
    READ_ENTITIES,
    READ_EXTRACTS,
    READ_OUTGOING_FEEDS,
    READ_PERMSSIONS,
    RETRY_INTERVAL,
    SEC_KEY,
    SELF,
    SECURITY_CONTROL,
    SLASH,
    SORT,
    SPACE_STRING,
    START_TIME,
    STATUS_CODE_200,
    STATUS_CODE_201,
    STATUS_CODE_202,
    STATUS_CODE_400,
    STATUS_CODE_401,
    STATUS_CODE_403,
    STATUS_CODE_404,
    STATUS_CODE_409,
    STATUS_CODE_422,
    STATUS_CODE_500,
    STR_TWO,
    TAGS_KEY,
    TIME_KEY,
    TIME_STAMP,
    TIMEOUT,
    TITLE,
    TYPE,
    UNDERSCORE,
    VALUE,
    VERIFY_SSL,
    VERSION,
)
from app.constants.messages import (
    ADD_OBSERVABLES,
    ALL_PERMISSIONS_GRANTED_TO_USER,
    BREAK_LOOP,
    BULK_LOAD_ERROR_PARSING,
    BULK_LOAD_INTERNAL_ERROR,
    BULK_LOAD_REQUEST_PARAM_NOT_VALID,
    BULK_LOAD_SUCCESSFULL,
    BULK_LOAD_UPDATE_ERROR,
    CHECK_QRADAR_REFERENCE_TABLE,
    CHECK_QRADAR_REFERENCE_TABLES,
    CHECKPOINT_FOUND,
    CHECKPOINT_SUCCESSFULLY_WRITTEN,
    COLLECTING_OBSERVABLE,
    CONNECTION_ERROR,
    DATA_FOUND_FOR_FEED_ID_AND_TYPE,
    DATA_NOT_FOUND_FOR_SELECTED_OUTGOING_FEED,
    DELETING_TABLE,
    ENDPOINT_CALLED,
    ERROR_IN_USER_PERMISSIONS,
    ERROR_OCCURED_IN_PLATFORM_PERMISSIONS,
    ERROR_IN_FETCHING_TABLES,
    ERROR_OCCURED_WHILE_DELETING_TABLE,
    ERROR_OCCURED_WHILE_RETREVING_TASK_STATUS,
    FETCH_OUTGOING_FEED_ID,
    FETCH_OUTGOING_FEEDS,
    GET_OBSERVABLE,
    GET_OBSERVABLE_DATA,
    GET_REFERENCE_TABLE,
    GET_REFERENCE_TABLES_ERROR,
    GET_REFERENCE_TABLES_INTERNAL_ERROR,
    GET_REFERENCE_TABLES_NOT_FOUND,
    GET_REFERENCE_TABLES_PARAM_NOT_VALID,
    GETTING_PLATFORM_PERMISSIONS,
    GETTING_USER_PERMISSIONS,
    GET_TABLES,
    IN_DELETE,
    INTERNAL_ERROR,
    JSON_EXCEPTION,
    MISSING_PERMISSIONS,
    MISSING_READ_PERMISSIONS,
    NO_OBSERVABLES_FOUND,
    OBSERVABLE_DATA_DICT,
    OBSERVABLE_TYPE_MODIFIED,
    OBSERVABLE_TYPE_RECEIVED,
    OBSERVABLES_AND_CHECKPOINT_RECEIVED,
    OBSERVABLES_FOUND,
    PENDING_OBSERVABLES,
    REFERENCE_TABLE_DOES_NOT_EXIST,
    REQUEST_DOES_NOT_EXIST,
    REFERENCE_TABLE_REQUEST_ACCEPTED,
    REQUEST_PARAM_INVALID,
    REQUEST_PARAM_INVALID_TO_DELETE,
    REQUEST_PARAM_NOT_VALID,
    REQUEST_UNAUTHORIZED,
    RESPONSE_RECEIVED,
    RETREIVE_TASK_STATUS,
    SEND_REQUEST,
    SUCCESSFULLY_FETCHED_PLATFORM_PERMISSIONS,
    SUCCESSFULLY_FETCHED_REFERENCE_TABLES,
    SUCCESSFULLY_FETCHED_USER_PERMISSIONS,
    TABLE_ALREADY_EXISTS,
    TABLE_CREATED,
    TABLE_NAME,
    TASK_DOES_NOT_EXIST,
    TASK_STATUS_RETREIVED,
    URL_MSG,
    USER_MISSING_PERMISSIONS,
    USER_UNAUTHORIZED,
    WRITING_CHECKPOINT,
)
from app.datastore import read_data_store
from app.decipher import get_credentials
from app.utils.converters import (
    get_current_time,
    get_formatted_date,
    format_time_to_iso,
)
from qpylib import qpylib

configs = {
    TIMEOUT: DEFAULT_TIMEOUT,
    MAX_RETRY: DEFAULT_MAX_RETRY,
    RETRY_INTERVAL: DEFAULT_RETRY_INTERVAL,
    VERIFY_SSL: DEFAULT_VERIFY_SSL,
    PAGE_SIZE: DEFAULT_PAGE_SIZE,
}


class CustomAuth:
    """Credentials required for user authentication to EIQ platform  and QRadar ."""

    def __init__(self, config):
        self._host = config[HOST]
        self._api_key = config[API_KEY]
        self._sec_token = config[QRADAR_SECURITY_TOKEN]
        self._version = config[VERSION]
        self._auth_user = config[AUTH_USER]

    @property
    def host(self):
        """Get value for host.

        :return: host
        :rtype: str
        """
        return self._host

    @host.setter
    def host(self, host):
        self.host = host

    @property
    def api_key(self):
        """Get value for api_key.

        :return: api_key
        :rtype: str
        """
        return self._api_key

    @api_key.setter
    def api_key(self, api_key):
        self._api_key = api_key

    @property
    def sec_token(self):
        """Get value for sec_token.

        :return: sec_token
        :rtype: str
        """
        return self._sec_token

    @sec_token.setter
    def sec_token(self, sec_token):
        self._sec_token = sec_token

    @property
    def version(self):
        """Get value for version.

        :return: version
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    @property
    def auth_user(self):
        """Get value for auth_user.

        :return: auth_user
        :rtype: str
        """
        return self._auth_user

    @auth_user.setter
    def auth_user(self, auth_user):
        self._auth_user = auth_user

    def get_eiq_request(self,configs=configs):
        """Get request object for eiq platform APIs.

        :return: request object
        :rtype: request
        """
        return Request(self._host, auth=BEARER_TOKEN, token=self._api_key, **configs)

    @staticmethod
    def get_qradar_request(url):
        """Get request object for Qradar APIs .

        :param url: url console address for Qradar.
        :type url: str
        :return: request object
        :rtype: request
        """
        return Request(url, auth=NO_AUTH, **configs)  # console_address


class EIQApi:
    """Get and process the data from EclecticIQ platform APIs ."""

    def __init__(self, config=None):
        if not config:
            config = get_credentials(True)
        self.auth_config = CustomAuth(config)
        self.setup_data = read_data_store(DATA_STORE_DIR, DATA_STORE_SETUP_FILE)

    def create_sighting(
        self, value, description, title, tags, entity_type, confidence_level
    ):  # pylint: disable=R0913,R0914
        """Create sighting in EclecticIQ platform.

        :param description: description of sighting
        :type: str
        :param title: title of sighting
        :type: str
        :param tags: tags associated with sighting
        :type: str
        :param type: type of entity
        :type: str
        :return: response
        :rtype: Response Obj
        """
        response = self.lookup_observables(entity_type, value)
        obs_id_list = []
        if str(response.status_code).startswith("2"):
            content = EIQApi.get_response_content(response)
            data = content.get(DATA)
            for item in data:
                obs_id_list.append(item[ID])
        else:
            qpylib.log(
                NO_OBSERVABLES_FOUND.format(entity_type, value),
                log_level=LOG_LEVEL_INFO,
            )

        today = datetime.datetime.utcnow().date()
        sighting = SIGHTING_SCHEMA
        sighting[DATA][DATA][DESC_KEY] = description
        sighting[DATA][DATA][TIME_STAMP] = format_time_to_iso(
            datetime.datetime.utcnow()
        )
        sighting[DATA][DATA]["confidence"] = confidence_level
        sighting[DATA][DATA][TITLE] = title
        sighting[DATA][DATA][SECURITY_CONTROL][TIME_KEY][
            START_TIME
        ] = format_time_to_iso(
            datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
        )
        sighting[DATA][META_KEY][TAGS_KEY] = tags
        sighting[DATA][META_KEY][INGEST_TIME_KEY] = format_time_to_iso(
            datetime.datetime.utcnow()
        )
        request = self.auth_config.get_eiq_request()
        response = request.send(
            POST,
            endpoint=self.auth_config.version + EIQ_ENTITIES,
            data=json.dumps(sighting),
            verify=DEFAULT_VERIFY_SSL,
        )
        if str(response.status_code).startswith(STR_TWO):
            results = [
                {
                    VALUE: value,
                    TYPE: entity_type,
                    TITLE: title,
                    DESC_KEY: description,
                    CONFIDENCE_KEY: confidence_level,
                    TAGS_KEY: str(tags),
                    TIME_KEY: int(datetime.datetime.now().timestamp()),
                }
            ]
            insert_data_to_table(results, EIQ_SIGHTING, list(results[0].keys()))
        return response

    def lookup_observables(self, obs_type, value):
        """Lookup observables related to entity.

        :param type: type of entity
        :type: str
        :param value: value of entity
        :type: str
        :return: response
        :rtype: Response Obj
        """
        request = self.auth_config.get_eiq_request()
        param = {"filter[type]": obs_type, "filter[value]": value}
        response = request.send(
            GET,
            endpoint=self.auth_config.version + EIQ_OBSERVABLES_BY_ID,
            params=param,
            verify=DEFAULT_VERIFY_SSL,
        )
        return response

    def get_observable_by_id(self, obs_id):
        """Get observables by id.

        :param obs_id: Observable ID
        :type: str
        :return: response content
        :rtype: dict
        """
        endpoint = self.auth_config.version + EIQ_OBSERVABLES_BY_ID + SLASH + obs_id

        qpylib.log(ENDPOINT_CALLED.format(endpoint), level=LOG_LEVEL_INFO)
        request = self.auth_config.get_eiq_request()
        response = request.send(GET, endpoint=endpoint)
        if response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
            qpylib.log(
                RESPONSE_RECEIVED.format(response.status_code), level=LOG_LEVEL_INFO
            )
            return {}

        content = EIQApi.get_response_content(response)
        data = content.get(DATA)
        return data

    def fetch_entity_details(self, entity_id):
        """Get entity details by id.

        :param entity_id: Entity ID
        :type: str
        :return: response content
        :rtype: dict
        """
        endpoint = self.auth_config.version + EIQ_ENTITIES + SLASH + entity_id

        qpylib.log(ENDPOINT_CALLED.format(endpoint), level=LOG_LEVEL_INFO)
        request = self.auth_config.get_eiq_request()
        response = request.send(GET, endpoint=endpoint)
        if response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
            qpylib.log(
                RESPONSE_RECEIVED.format(response.status_code), level=LOG_LEVEL_INFO
            )
            return {}

        content = EIQApi.get_response_content(response)
        data = content.get(DATA)
        return data

    def fetch_outgoing_feeds(self):
        """Get outgoings feeds from EclecticIQ .

        :return: feeds data
        :rtype: dict
        """
        qpylib.log(FETCH_OUTGOING_FEEDS, level=LOG_LEVEL_INFO)
        request = self.auth_config.get_eiq_request()
        response = request.send(
            GET, endpoint=self.auth_config.version + EIQ_OUTGOING_FEEDS
        )

        content = EIQApi.get_response_content(response)
        data = content.get(DATA)
        feeds_data = EIQApi.get_outgoing_feeds_ids_names(data)
        return feeds_data

    @staticmethod
    def get_permssion_ids(permissions):
        """Get permission ids granted to user.

        :param feeds: permissions
            ["https://ic-playground.eclecticiq.com/api/beta/permissions/1",
            "https://ic-playground.eclecticiq.com/api/beta/permissions/2"....]

        :type response: list
        :return: List of permission ids
            [1,2,...]
        :rtype: list
        """
        permission_ids = []
        for permission in permissions:
            permission_ids.append(int(permission.split(SLASH)[-1]))
        return permission_ids

    @staticmethod
    def get_platform_permission_ids(permissions_data):
        """Get permission ids required for user to authenticate.

        :param feeds: permissions_data
        :type response: list
            [{"id": 1, "name": "read history-events"},{"id": 2,"name": "read discovery-rules"}...]
        :return: List of permission ids
            [33, 59, 66,78]
        :rtype: list
        """
        wanted_permissions = [
            READ_ENTITIES,
            MODIFY_EXTRACTS,
            READ_EXTRACTS,
            READ_OUTGOING_FEEDS,
        ]
        ids_required_for_user = []
        for value in permissions_data:
            if value[NAME] in wanted_permissions:
                ids_required_for_user.append(value[ID])

        return ids_required_for_user

    def get_platform_permissions(self):
        """Get all platform permissions .

        :return: List of permission data ids and name
            [{"id": 1, "name": "read history-events"},{"id": 2,"name": "read discovery-rules"}]
        :rtype: list
        """
        permissions_data = []
        qpylib.log(GETTING_PLATFORM_PERMISSIONS, level=LOG_LEVEL_INFO)
        request = self.auth_config.get_eiq_request()

        response = request.send(
            GET, endpoint=self.auth_config.version + EIQ_PERMISSIONS
        )
        if response.status_code == STATUS_CODE_401:
            qpylib.log(REQUEST_UNAUTHORIZED, level=LOG_LEVEL_INFO)
        elif response.status_code == STATUS_CODE_403:
            qpylib.log(USER_MISSING_PERMISSIONS, level=LOG_LEVEL_INFO)
        elif response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
            qpylib.log(
                ERROR_OCCURED_IN_PLATFORM_PERMISSIONS.format(
                    response.status_code, response.content
                ),
                level=LOG_LEVEL_INFO,
            )
        else:
            qpylib.log(SUCCESSFULLY_FETCHED_PLATFORM_PERMISSIONS, level=LOG_LEVEL_INFO)
            content = EIQApi.get_response_content(response)
            permissions_data = content.get(DATA)
        return permissions_data

    def get_user_granted_permissions(self):
        """Get all permissions granted to user.

        :return: List of permissions
        :rtype: list
        """
        permissions = []
        qpylib.log(GETTING_USER_PERMISSIONS, level=LOG_LEVEL_INFO)
        configs_user_permissions = configs
        configs_user_permissions[TIMEOUT]= DEFAULT_TIMEOUT_USER_PERMISSIONS
        configs_user_permissions[RETRY_INTERVAL] = DEFAULT_MAX_RETRY_USER_PERMISSIONS
        request = self.auth_config.get_eiq_request(configs=configs_user_permissions)
        endpoint = self.auth_config.version + EIQ_USER_PERMISSIONS + SLASH + SELF
        
        response = request.send(GET, endpoint=endpoint, verify=DEFAULT_VERIFY_SSL)

        if response.status_code == STATUS_CODE_401:
            qpylib.log(REQUEST_UNAUTHORIZED, level=LOG_LEVEL_INFO)
        elif response.status_code == STATUS_CODE_403:
            qpylib.log(MISSING_PERMISSIONS, level=LOG_LEVEL_INFO)
        elif response.status_code == STATUS_CODE_404:
            qpylib.log(REQUEST_DOES_NOT_EXIST, level=LOG_LEVEL_INFO)
        elif response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
            qpylib.log(
                ERROR_IN_USER_PERMISSIONS.format(
                    response.status_code, response.content
                ),
                level=LOG_LEVEL_INFO,
            )
        else:
            qpylib.log(SUCCESSFULLY_FETCHED_USER_PERMISSIONS, level=LOG_LEVEL_INFO)
            content = EIQApi.get_response_content(response)
            if content:
                permissions = content.get(DATA).get(PERMISSIONS)
            else:
                response.status_code = STATUS_CODE_401

        return permissions, response.status_code

    @staticmethod
    def get_permission_name_from_id(permission_data, permission_ids):
        """Get permission name from permission ids.

        :return: permission names
        :rtype: list of str
        """
        permissions_name = []
        for data in permission_data:
            for permission_id in permission_ids:
                if data[ID] == permission_id:
                    permissions_name.append(data[NAME])
        return permissions_name

    def validate_user_permissions(self):
        """Get permission ids granted to user.

        :return: missing_permissions
        :rtype: set
        """
        permissions_of_user, status_code = self.get_user_granted_permissions()
        missing_permissions = []
        if status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
            qpylib.log(USER_UNAUTHORIZED)
        elif not permissions_of_user and status_code in [
            STATUS_CODE_200,
            STATUS_CODE_201,
        ]:
            qpylib.log(MISSING_READ_PERMISSIONS)
            missing_permissions = READ_PERMSSIONS
        else:
            ids_of_user = EIQApi.get_permssion_ids(
                permissions_of_user
            )  # permission ids possesed by user
            permissions_data = self.get_platform_permissions()
            if permissions_data:
                ids_required_for_user = EIQApi.get_platform_permission_ids(
                    permissions_data
                )
                user_authenticated, permission_ids = EIQApi.authenticate_user(
                    ids_of_user, ids_required_for_user
                )

                if not user_authenticated:
                    # check for missing permissions
                    permissions_data = self.get_platform_permissions()
                    missing_permissions = EIQApi.get_permission_name_from_id(
                        permissions_data, permission_ids
                    )
        return missing_permissions, status_code

    @staticmethod
    def authenticate_user(ids_of_user, ids_required_for_user):
        """Get user authentication and missing permission ids .

        :param ids_of_user: permission ids user have
        :type ids_of_user: list
        :param ids_required_for_user: permission ids required for user to authenticate
        :type ids_required_for_user: list
        :return: is user authenticated , missing permissions ids
        :rtype: boolean,set
        """
        user_authenticated = False
        value = set(ids_required_for_user).difference(ids_of_user)

        if not value:
            qpylib.log(ALL_PERMISSIONS_GRANTED_TO_USER.format(value))
            user_authenticated = True
        return user_authenticated, value

    @staticmethod
    def get_outgoing_feeds_ids_names(feeds):
        """Get outgoing feed ids and names.

        :param feeds: outgoing feeds data
        :type response: list
        :return: List of outgoing ids and names
        :rtype: list
        """
        ids_and_names = []
        for data in feeds:
            value = {ID: data[ID], NAME: data[NAME]}
            ids_and_names.append(value)

        return ids_and_names

    @staticmethod
    def get_response_content(response):
        """Get the response content from the response.

        :param response: Response to retrieve content
        :type response: Response
        :return: Response content
        :rtype: dict / None
        """
        content = {}
        try:
            content = json.loads(response.content)
        except json.decoder.JSONDecodeError as error:
            qpylib.log(JSON_EXCEPTION.format(error), level=LOG_LEVEL_ERROR)

        return content

    @staticmethod
    def get_observable_ids(data):
        """Get the unique observable ids from list of observable ids url.

        :param data: list of url observable ids
        :type data: list
        :return: observable_ids
        :rtype: set
        """
        observable_ids = set()
        for item in data:
            observable_ids.add(str(item.split(SLASH)[-1]))
        return observable_ids

    @staticmethod
    def get_unique_observables(data):
        """Get the unique observable ids from list of observable ids url.

        :param data: list of url observable ids
        :type data: list
        :return: observable_ids
        :rtype: set
        """
        observables = set()
        for item in data:
            observable_list = item.get(OBSERVABLES)
            if observable_list:
                observables.update(set(observable_list))
        observables = EIQApi.get_observable_ids(observables)
        return observables

    @staticmethod
    def check_observable_type(observable_type):
        """Check observable type.

        :param observable_type: observable_type
        :type observable_type: str
        :return: observable type
        :rtype: str
        """
        if observable_type in ["ipv4", "ipv6"]:
            observable_type = "ip"
        elif observable_type in ["hash-md5", "hash-sha1", "hash-sha256", "hash-sha512"]:
            observable_type = "file_hash"
        elif observable_type == "uri":
            observable_type = "url"
        return observable_type

    def formatted_data_to_load(self, data):
        """Get the formatted data to load in Qradar Reference table.

        :param outgoing_feed_id: outgoing feed id
        :type outgoing_feed_id: int
        :param data: observable data
        :type data: dict
        :return: dict of observable types and data to load
        :rtype: dict
        """
        columns_keys = [CREATED_AT, ID, LAST_UPDATED_AT, MALICIOUSNESS, VALUE]
        data_to_load = {}

        qpylib.log(OBSERVABLE_TYPE_RECEIVED.format(data[TYPE]), level=LOG_LEVEL_INFO)
        obs_type = EIQApi.check_observable_type(data[TYPE])
        qpylib.log(OBSERVABLE_TYPE_MODIFIED.format(obs_type), level=LOG_LEVEL_INFO)
        if obs_type in self.setup_data.get(OBSERVABLE_TYPES):
            temp_dict = {}
            for column, val in data.items():
                if column == META:
                    temp_dict[MALICIOUSNESS] = val[MALICIOUSNESS]
                if column in columns_keys:
                    if column == VALUE:
                        observe_id = val
                    temp_dict[column] = val

            data_to_load[str(observe_id)] = temp_dict
        return obs_type, data_to_load

    def get_observable_data(self, observable_ids, outgoing_feed_id):
        """Get the observable data and  load in Qradar Reference table.

        :param outgoing_feed_id: outgoing feed id
        :type outgoing_feed_id: int
        :param observable_ids: set of observable ids
        :type observable_ids: set
        """
        qpylib.log(GET_OBSERVABLE, level=LOG_LEVEL_INFO)

        request = self.auth_config.get_eiq_request()
        counter = 1
        for observable_id in observable_ids:
            qpylib.log(
                PENDING_OBSERVABLES.format(len(observable_ids) - counter),
                level=LOG_LEVEL_INFO,
            )
            qpylib.log(COLLECTING_OBSERVABLE.format(counter), level=LOG_LEVEL_INFO)
            qpylib.log(
                GET_OBSERVABLE_DATA.format(observable_id, outgoing_feed_id),
                level=LOG_LEVEL_INFO,
            )
            endpoint = (
                self.auth_config.version + EIQ_OBSERVABLES_BY_ID + SLASH + observable_id
            )

            qpylib.log(ENDPOINT_CALLED.format(endpoint), level=LOG_LEVEL_INFO)

            response = request.send(GET, endpoint=endpoint)
            if response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
                qpylib.log(
                    RESPONSE_RECEIVED.format(response.status_code), level=LOG_LEVEL_INFO
                )
                return False

            content = EIQApi.get_response_content(response)
            data = content.get(DATA)

            obs_type, observable_type_data = self.formatted_data_to_load(data)
            if observable_type_data:
                qpylib.log(
                    DATA_FOUND_FOR_FEED_ID_AND_TYPE.format(outgoing_feed_id, obs_type),
                    level=LOG_LEVEL_INFO,
                )
                qpylib.log(OBSERVABLE_DATA_DICT, level=LOG_LEVEL_INFO)

                response = QradarApi().load_observables_to_reference_tables(
                    outgoing_feed_id, obs_type, observable_type_data
                )
                if not response:
                    return response
            else:
                qpylib.log(
                    f"Not loading this observable as it is of type {obs_type}",
                    level=LOG_LEVEL_INFO,
                )
            counter += 1

        return True

    def _get_entities(self, request, parameters):
        """Get the entities from eiq and make list of observables.

        :param request: request object for eiq apis
        :type request: request object
        :param parameters: params required in apis
        :type parameters: dict
        """
        observables = []
        new_checkpoint = None
        while True:
            qpylib.log(SEND_REQUEST.format(parameters), level=LOG_LEVEL_INFO)

            response = request.send(
                GET, endpoint=self.auth_config.version + EIQ_ENTITIES, params=parameters
            )

            if response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
                qpylib.log(
                    RESPONSE_RECEIVED.format(response.status_code), level=LOG_LEVEL_INFO
                )
                qpylib.log(f"Response content {str(response.content)}")
                return observables, new_checkpoint

            # from data get unique observables
            content = EIQApi.get_response_content(response)
            data = content.get(DATA)

            observable_ids = EIQApi.get_unique_observables(data)
            qpylib.log(
                OBSERVABLES_FOUND.format(len(observable_ids)), level=LOG_LEVEL_INFO
            )
            observables.extend(observable_ids)
            qpylib.log(ADD_OBSERVABLES.format(len(observables)), level=LOG_LEVEL_INFO)
            content = EIQApi.get_response_content(response)
            count = content.get(COUNT)

            if parameters.get(OFFSET):
                parameters[OFFSET] += parameters[LIMIT]
            else:
                parameters[OFFSET] = parameters[LIMIT]
            if count < parameters[LIMIT] or response == {}:
                qpylib.log(BREAK_LOOP, level=LOG_LEVEL_INFO)
                new_checkpoint = get_current_time()
                break
        return observables, new_checkpoint

    def get_observables(self):
        """Get unique observable ids from entities data on basis of outgoing_feed."""
        outgoing_feeds = self.setup_data.get(OUTGOING_FEEDS)
        outgoing_feeds_ids = []
        for outgoing_feed in outgoing_feeds:
            outgoing_feeds_ids.append(outgoing_feed.get(ID))

        request = self.auth_config.get_eiq_request()
        # create/check reference table eiq_feedname_feedid_type
        QradarApi().create_qradar_reference_tables()

        for outgoing_feed in outgoing_feeds_ids:
            qpylib.log(
                FETCH_OUTGOING_FEED_ID.format(outgoing_feed), level=LOG_LEVEL_INFO
            )
            checkpoint = read_checkpoint(str(outgoing_feed))
            start_date = get_formatted_date(int(self.setup_data.get(BACKFILL_TIME)))
            if checkpoint:
                qpylib.log(CHECKPOINT_FOUND, level=LOG_LEVEL_INFO)
                start_date = checkpoint

            parameters = {
                LIMIT: DEFAULT_LIMIT,
                FILTER_LAST_UPDATED_AT: start_date,
                FILTER_OUTGOING_FEEDS: outgoing_feed,
                SORT: DESC_BY_LAST_UPDATED_AT,
            }
            observables, new_checkpoint = self._get_entities(request, parameters)
            qpylib.log(
                OBSERVABLES_AND_CHECKPOINT_RECEIVED.format(
                    len(observables), new_checkpoint
                ),
                level=LOG_LEVEL_INFO,
            )

            # make call to get observables on the basis of id

            response = True

            if observables:
                response = self.get_observable_data(observables, outgoing_feed)
            if new_checkpoint and response:
                new_checkpoint = new_checkpoint.split(PLUS)
                new_checkpoint = new_checkpoint[0]
                qpylib.log(
                    WRITING_CHECKPOINT.format(new_checkpoint), level=LOG_LEVEL_INFO
                )
                write_checkpoint(str(outgoing_feed), new_checkpoint)
                qpylib.log(CHECKPOINT_SUCCESSFULLY_WRITTEN, level=LOG_LEVEL_INFO)

            time.sleep(0.2)


class QradarApi:
    """Use Qradrar APIs."""

    def __init__(self, config=None):
        if not config:
            config = get_credentials(True)
        self.auth_config = CustomAuth(config)
        self.setup_data = read_data_store(DATA_STORE_DIR, DATA_STORE_SETUP_FILE)

    def get_reference_tables(self):
        """Get the reference tables .

        :return: boolean value
        :rtype: boolean
        """
        qpylib.log(GET_REFERENCE_TABLE, level=LOG_LEVEL_INFO)
        headers = {HEADERS: {SEC_KEY: self.auth_config.sec_token}}
        console_address = qpylib.get_console_fqdn()

        url = HTTPS + str(console_address)
        request = CustomAuth.get_qradar_request(url)

        response = request.send(
            GET, endpoint=QRADAR_REFERENCE_TABLE, verify=DEFAULT_VERIFY_SSL, **headers
        )
        if response.status_code == STATUS_CODE_404:
            qpylib.log(GET_REFERENCE_TABLES_NOT_FOUND, level=LOG_LEVEL_ERROR)

        elif response.status_code == STATUS_CODE_422:
            qpylib.log(GET_REFERENCE_TABLES_PARAM_NOT_VALID, level=LOG_LEVEL_ERROR)

        elif response.status_code == STATUS_CODE_500:
            qpylib.log(GET_REFERENCE_TABLES_ERROR, level=LOG_LEVEL_ERROR)

        elif response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
            qpylib.log(
                GET_REFERENCE_TABLES_INTERNAL_ERROR.format(
                    response.status_code, str(response.content)
                ),
                level=LOG_LEVEL_ERROR,
            )

        else:
            qpylib.log(SUCCESSFULLY_FETCHED_REFERENCE_TABLES, level=LOG_LEVEL_INFO)
        return response.status_code

    @staticmethod
    def get_reference_table_name(outgoing_feed_id, outgoing_feed_name, observable_type):
        """Get the reference table name .

        :param outgoing_feed_id: outgoing feed id
        :type outgoing_feed_id: int
        :param outgoing_feed_name: outgoing feed name
        :type outgoing_feed_name: str
        :param observable_type: type of observable
        :type observable_type: str
        """
        table_name = (
            EIQ
            + UNDERSCORE
            + str(outgoing_feed_id)
            + UNDERSCORE
            + outgoing_feed_name.replace(SPACE_STRING, UNDERSCORE)
            + UNDERSCORE
            + observable_type
        )
        return table_name

    def get_outgoing_feed_name_from_id(self, outgoing_feed_id):
        """Get the outgoing feed name from outgoing feed id .

        :param outgoing_feed_id: outgoing feed id
        :type outgoing_feed_id: int
        """
        for feed in self.setup_data.get(OUTGOING_FEEDS):
            if feed[ID] == str(outgoing_feed_id):
                return feed[NAME]
        return None

    def create_qradar_reference_tables(self):
        """Create Qradar Reference table names ."""
        qpylib.log(CHECK_QRADAR_REFERENCE_TABLES, level=LOG_LEVEL_INFO)
        outgoing_feeds = self.setup_data.get(OUTGOING_FEEDS)
        observable_types = self.setup_data.get(OBSERVABLE_TYPES)

        headers = {HEADERS: {SEC_KEY: self.auth_config.sec_token}}

        console_address = qpylib.get_console_fqdn()

        for observable_type in observable_types:
            for outgoing_feed in outgoing_feeds:

                table_name = QradarApi.get_reference_table_name(
                    outgoing_feed[ID], outgoing_feed[NAME], observable_type
                )
                qpylib.log(TABLE_NAME.format(table_name), level=LOG_LEVEL_INFO)

                element_type = ALNIC
                table_fields = json.dumps(
                    [
                        {KEY_NAME: CREATED_AT, ELEMENT_TYPE: ALNIC},
                        {KEY_NAME: ID, ELEMENT_TYPE: ALNIC},
                        {KEY_NAME: LAST_UPDATED_AT, ELEMENT_TYPE: ALNIC},
                        {KEY_NAME: MALICIOUSNESS, ELEMENT_TYPE: ALNIC},
                        {KEY_NAME: VALUE, ELEMENT_TYPE: ALNIC},
                    ]
                )
                params = {
                    NAME: table_name,
                    ELEMENT_TYPE: element_type,
                    OUTER_KEY_LABEL: EIQ_VALUE,
                    KEY_NAME_TYPES: table_fields,
                }
                url = HTTPS + str(console_address)

                qpylib.log(
                    CHECK_QRADAR_REFERENCE_TABLE.format(table_name),
                    level=LOG_LEVEL_INFO,
                )
                qpylib.log(URL_MSG.format(url))

                request = CustomAuth.get_qradar_request(url)
                response = request.send(
                    POST,
                    endpoint=QRADAR_REFERENCE_TABLE,
                    params=params,
                    verify=DEFAULT_VERIFY_SSL,
                    **headers,
                )

                if response.status_code == STATUS_CODE_422:
                    qpylib.log(
                        REQUEST_PARAM_NOT_VALID.format(table_name),
                        level=LOG_LEVEL_ERROR,
                    )
                elif response.status_code == STATUS_CODE_409:
                    qpylib.log(
                        TABLE_ALREADY_EXISTS.format(table_name), level=LOG_LEVEL_INFO
                    )

                elif response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
                    qpylib.log(
                        INTERNAL_ERROR.format(
                            response.status_code, str(response.content)
                        ),
                        level=LOG_LEVEL_ERROR,
                    )
                else:
                    qpylib.log(
                        TABLE_CREATED.format(table_name, response.status_code),
                        level=LOG_LEVEL_INFO,
                    )

    def load_observables_to_reference_tables(
        self, outgoing_feed_id, observable_type, data_to_load
    ):
        """Get the outgoing feed name from outgoing feed id .

        :param outgoing_feed_id: outgoing feed id
        :type outgoing_feed_id: int
        :param observable_type: type of observable
        :type observable_type: str
        :param data_to_load: data to load
        :type data_to_load: dict
        :return: boolean value
        :rtype: boolean
        """
        return_value = True
        outgoing_feed_name = self.get_outgoing_feed_name_from_id(outgoing_feed_id)
        table_name = QradarApi.get_reference_table_name(
            outgoing_feed_id, outgoing_feed_name, observable_type
        )
        qpylib.log(TABLE_NAME.format(table_name), level=LOG_LEVEL_INFO)

        endpoint = QRADAR_BULK_LOAD + table_name
        headers = {HEADERS: {SEC_KEY: self.auth_config.sec_token}}

        qpylib.log(URL_MSG.format(endpoint), level=LOG_LEVEL_INFO)
        jsn_str = json.dumps(data_to_load)

        console_address = qpylib.get_console_fqdn()

        url = HTTPS + str(console_address)
        request = CustomAuth.get_qradar_request(url)
        response = request.send(POST, endpoint=endpoint, data=jsn_str, **headers)

        if response.status_code == STATUS_CODE_400:
            qpylib.log(
                BULK_LOAD_ERROR_PARSING.format(table_name), level=LOG_LEVEL_ERROR
            )
            return_value = False

        elif response.status_code == STATUS_CODE_404:
            qpylib.log(
                REFERENCE_TABLE_DOES_NOT_EXIST.format(table_name), level=LOG_LEVEL_ERROR
            )
            return_value = False
        elif response.status_code == STATUS_CODE_422:
            qpylib.log(
                BULK_LOAD_REQUEST_PARAM_NOT_VALID.format(table_name),
                level=LOG_LEVEL_ERROR,
            )
            return_value = False
        elif response.status_code == STATUS_CODE_500:
            qpylib.log(BULK_LOAD_UPDATE_ERROR.format(table_name), level=LOG_LEVEL_ERROR)
            return_value = False

        elif response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
            qpylib.log(
                BULK_LOAD_INTERNAL_ERROR.format(
                    table_name, response.status_code, str(response.content)
                ),
                level=LOG_LEVEL_ERROR,
            )
            return_value = False

        else:
            qpylib.log(BULK_LOAD_SUCCESSFULL.format(table_name), level=LOG_LEVEL_INFO)
        return return_value

    def tables_delete_tasks(self, task_id):
        """Retrieve the delete Reference Data Tables task status.

        :param task_id: task id for the table to be deleted.
        :type task_id: str
        :return: reference data deleted
        :rtype: boolean
        """
        reference_data_deleted = True
        qpylib.log(
            RETREIVE_TASK_STATUS.format(task_id),
            level=LOG_LEVEL_INFO,
        )
        headers = {HEADERS: {SEC_KEY: self.auth_config.sec_token}}
        console_address = qpylib.get_console_fqdn()

        url = HTTPS + str(console_address)

        request = CustomAuth.get_qradar_request(url)
        response = request.send(
            GET,
            endpoint=QRADRAR_REFERENCE_DELETE_TASKS + SLASH + task_id,
            verify=DEFAULT_VERIFY_SSL,
            **headers,
        )
        if response.status_code == STATUS_CODE_404:
            qpylib.log(TASK_DOES_NOT_EXIST.format(task_id), level=LOG_LEVEL_INFO)
            reference_data_deleted = False
        elif response.status_code not in [
            STATUS_CODE_200,
            STATUS_CODE_201,
            STATUS_CODE_202,
        ]:
            qpylib.log(
                ERROR_OCCURED_WHILE_RETREVING_TASK_STATUS.format(
                    response.status_code, str(response.content)
                ),
                level=LOG_LEVEL_ERROR,
            )
            reference_data_deleted = False
        else:
            qpylib.log(
                TASK_STATUS_RETREIVED.format(task_id, response.status_code),
                level=LOG_LEVEL_INFO,
            )

            reference_data_deleted = True
        return reference_data_deleted

    def delete_reference_tables(self, table_names):
        """Delete Qradar Reference tables  .

        :param table_names: list of table names to be deleted
        :type outgoing_feed: list
        :return: reference data deleted
        :rtype: boolean
        """
        reference_data_deleted = False
        qpylib.log(IN_DELETE, level=LOG_LEVEL_INFO)

        headers = {HEADERS: {SEC_KEY: self.auth_config.sec_token}}
        console_address = qpylib.get_console_fqdn()

        for table_name in table_names:
            qpylib.log(TABLE_NAME.format(table_name), level=LOG_LEVEL_INFO)
            url = HTTPS + str(console_address)

            qpylib.log(
                DELETING_TABLE.format(table_name),
                level=LOG_LEVEL_INFO,
            )

            request = CustomAuth.get_qradar_request(url)
            response = request.send(
                DELETE,
                endpoint=QRADAR_REFERENCE_TABLE + SLASH + table_name,
                verify=DEFAULT_VERIFY_SSL,
                **headers,
            )

            if response.status_code == STATUS_CODE_422:
                qpylib.log(
                    REQUEST_PARAM_INVALID_TO_DELETE.format(table_name),
                    level=LOG_LEVEL_ERROR,
                )
                reference_data_deleted = False
            elif response.status_code == STATUS_CODE_404:
                qpylib.log(
                    REFERENCE_TABLE_DOES_NOT_EXIST.format(table_name),
                    level=LOG_LEVEL_INFO,
                )
                reference_data_deleted = True
            elif response.status_code not in [
                STATUS_CODE_200,
                STATUS_CODE_201,
                STATUS_CODE_202,
            ]:
                qpylib.log(
                    ERROR_OCCURED_WHILE_DELETING_TABLE.format(
                        response.status_code, str(response.content)
                    ),
                    level=LOG_LEVEL_ERROR,
                )
                reference_data_deleted = False
            else:
                qpylib.log(
                    REFERENCE_TABLE_REQUEST_ACCEPTED.format(
                        table_name, response.status_code
                    ),
                    level=LOG_LEVEL_INFO,
                )

                content = EIQApi.get_response_content(response)
                task_id = content.get(ID)
                reference_data_deleted = self.tables_delete_tasks(str(task_id))

        if not table_names:
            qpylib.log(DATA_NOT_FOUND_FOR_SELECTED_OUTGOING_FEED, level=LOG_LEVEL_INFO)
        return reference_data_deleted

    @staticmethod
    def get_subname(outgoing_feed):
        """Get subname for the table name.

        :param outgoing_feed: outgoing feed id and name as str
        :type outgoing_feed: str
        :return: subname for reference table
        :rtype: str
        """
        feeds = outgoing_feed.split(GLUE_COLONS)
        return EIQ_ + feeds[1] + UNDERSCORE + feeds[0].replace(SPACE_STRING, UNDERSCORE)

    @staticmethod
    def get_table_names(content, outgoing_feed):
        """Get all reference data table names for an outgoing feed.

        :param content: response content
        :type content: dict
        :param outgoing_feed: outgoing feed
        :type outgoing_feed: dict
        :return: list of table_names
        :rtype: list
        """
        subname = QradarApi.get_subname(outgoing_feed)
        tables_name = []
        for data in content:
            if data[NAME].startswith(subname):
                tables_name.append(data[NAME])

        qpylib.log(f"Table names got: {tables_name}", level=LOG_LEVEL_INFO)
        return tables_name

    def get_reference_data_tables(self, outgoing_feed):
        """Get all reference data table names .

        :param outgoing_feed: outgoing feed id and name
        :type outgoing_feed: str
        :return: response
        :rtype: boolean
        """
        table_names = []
        qpylib.log(GET_TABLES, level=LOG_LEVEL_INFO)
        headers = {HEADERS: {SEC_KEY: self.auth_config.sec_token}}
        console_address = qpylib.get_console_fqdn()
        url = HTTPS + str(console_address)
        request = CustomAuth.get_qradar_request(url)
        response = request.send(
            GET, endpoint=QRADAR_REFERENCE_TABLE, verify=DEFAULT_VERIFY_SSL, **headers
        )
        if response.status_code == STATUS_CODE_422:
            qpylib.log(
                REQUEST_PARAM_INVALID,
                level=LOG_LEVEL_ERROR,
            )

        elif response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
            qpylib.log(
                ERROR_IN_FETCHING_TABLES.format(
                    response.status_code, str(response.content)
                ),
                level=LOG_LEVEL_ERROR,
            )
        else:
            qpylib.log(
                SUCCESSFULLY_FETCHED_REFERENCE_TABLES,
                level=LOG_LEVEL_INFO,
            )
            content = EIQApi.get_response_content(response)
            table_names = QradarApi.get_table_names(content, outgoing_feed)
            response = self.delete_reference_tables(table_names)

        return response
