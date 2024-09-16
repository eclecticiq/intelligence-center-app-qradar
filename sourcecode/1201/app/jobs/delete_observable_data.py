"""Jobs to delete observables."""


import time
import requests
from app.collector.eiq_data import CustomAuth, EIQApi
from app.configs.datastore import DATA_STORE_DIR, DATA_STORE_SETUP_FILE
from app.configs.eiq_api import QRADAR_REFERENCE_TABLE
from app.constants.defaults import (
    DEFAULT_LOWER_LIMIT,
    DEFAULT_UPPER_LIMIT,
    DEFAULT_VERIFY_SSL,
)
from app.constants.general import (
    DATA,
    DELETE,
    DOMAIN,
    EIQ_,
    GET,
    HEADERS,
    HTTPS,
    LAST_UPDATED_AT,
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_INFO,
    NAME,
    OBSERVABLE_TIME_TO_LIVE,
    PLUS,
    RANGE,
    SEC_KEY,
    SLASH,
    STATUS_CODE_200,
    STATUS_CODE_201,
    STATUS_CODE_404,
    STATUS_CODE_422,
    URL,
    VALUE,
)
from app.constants.messages import (
    DELETE_DATA_FOUND,
    DELETE_ERROR_IN_FETCHING_TABLES,
    DELETE_EVENTS,
    DELETE_FETCH_DATA,
    DELETE_OBSERVABLE_DATA_IS_OLDER,
    DELETE_REFERENCE_TABLE_DOES_NOT_EXIST,
    DELETE_REQUEST_PARAM_INVALID,
    DELETE_SUCCESSFULLY_FETCHED_REFERENCE_TABLES,
    ERROR_IN_DELETE_OBSERVABLES,
    FETCH_DATA_FOR_TABLE,
    LAST_UPDATED_VALUE_NOT_FOUND,
    NO_DATA_TO_DELETE,
    OBSERVABLE_DELETED,
    RECEIVED_TABLES,
    RECORD_DOES_NOT_EXIST,
    REFERENCE_DATA_TABLES,
    REQUEST_PARAM_INVALID,
    SUCCESSFULLY_REMOVED_OBSERVABLE,
    URL_MSG,
    VALUE_REMOVED,
)
from app.datastore import read_data_store
from app.decipher import get_credentials
from app.utils.converters import get_formatted_date
from qpylib import qpylib


def delete_data():
    """Delete observables from the Qradar reference tables after retention period."""
    qpylib.log(DELETE_EVENTS, level=LOG_LEVEL_INFO)
    config = get_credentials(True)
    auth_config = CustomAuth(config)
    sec_token = auth_config.sec_token

    setup_data = read_data_store(DATA_STORE_DIR, DATA_STORE_SETUP_FILE)
    observable_ttl = get_formatted_date(int(setup_data[OBSERVABLE_TIME_TO_LIVE]))

    table_names = get_reference_data_tables(sec_token)
    qpylib.log(RECEIVED_TABLES.format(table_names), level=LOG_LEVEL_DEBUG)
    fetch_observable_data_table(table_names, sec_token, observable_ttl)


def get_table_names(content):
    """Get all reference data table names .

    :param content: response content
    :type content: dict
    :return: list of table_names
    :rtype: list
    """
    tables_name = []
    for data in content:
        if data[NAME].startswith(EIQ_):
            tables_name.append(data[NAME])
    return tables_name


def get_reference_data_tables(sec_token):
    """Get all reference data table names .

    :param sec_token: security token
    :type sec_token: str
    :return: list of table_names
    :rtype: list
    """
    table_names = []

    qpylib.log(REFERENCE_DATA_TABLES, level=LOG_LEVEL_INFO)

    headers = {HEADERS: {SEC_KEY: sec_token}}
    console_address = qpylib.get_console_fqdn()
    url = HTTPS + str(console_address)

    qpylib.log(URL_MSG.format(url))

    request = CustomAuth.get_qradar_request(url)
    response = request.send(
        GET, endpoint=QRADAR_REFERENCE_TABLE, verify=DEFAULT_VERIFY_SSL, **headers
    )
    if response.status_code == STATUS_CODE_422:
        qpylib.log(
            DELETE_REQUEST_PARAM_INVALID,
            level=LOG_LEVEL_ERROR,
        )

    elif response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
        qpylib.log(
            DELETE_ERROR_IN_FETCHING_TABLES.format(
                response.status_code, str(response.content)
            ),
            level=LOG_LEVEL_ERROR,
        )
    else:
        qpylib.log(
            DELETE_SUCCESSFULLY_FETCHED_REFERENCE_TABLES,
            level=LOG_LEVEL_INFO,
        )
        content = EIQApi.get_response_content(response)
        table_names = get_table_names(content)
    return table_names


def delete_observable(table_name, observable_outer_key, observable_data, sec_token):
    """Delete observable in table.

    :param table_name: table name
    :type table_name: str
    :param sec_token: security token
    :type sec_token: str
    :param observable_ttl: observable TTL
    :type observable_ttl: str
    :return: is observable removed
    :rtype: boolean
    """
    return_value = True
    headers = {HEADERS: {SEC_KEY: sec_token}}
    console_address = qpylib.get_console_fqdn()
    url = HTTPS + str(console_address)

    request = CustomAuth.get_qradar_request(url)

    if table_name.endswith(URL) or table_name.endswith(DOMAIN):
        observable_outer_key = requests.compat.quote_plus(observable_outer_key)
        observable_outer_key = requests.compat.quote_plus(observable_outer_key)

    for obs_key, obs_value in observable_data.items():
        params = {VALUE: obs_value[VALUE]}
        response = request.send(
            DELETE,
            endpoint=QRADAR_REFERENCE_TABLE
            + SLASH
            + table_name
            + SLASH
            + observable_outer_key
            + SLASH
            + obs_key,
            params=params,
            verify=DEFAULT_VERIFY_SSL,
            **headers,
        )
        if response.status_code == STATUS_CODE_422:
            qpylib.log(
                REQUEST_PARAM_INVALID,
                level=LOG_LEVEL_ERROR,
            )
            return_value = False
        elif response.status_code == STATUS_CODE_404:
            qpylib.log(
                RECORD_DOES_NOT_EXIST.format(table_name),
                level=LOG_LEVEL_ERROR,
            )
            return_value = False
        elif response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
            qpylib.log(
                ERROR_IN_DELETE_OBSERVABLES.format(
                    response.status_code, str(response.content)
                ),
                level=LOG_LEVEL_ERROR,
            )
            return_value = False
        else:
            qpylib.log(
                VALUE_REMOVED,
                level=LOG_LEVEL_INFO,
            )
    qpylib.log(
        SUCCESSFULLY_REMOVED_OBSERVABLE,
        level=LOG_LEVEL_INFO,
    )
    return return_value


def check_last_updated_at_and_delete(
    table_name, sec_token, observable_data, observable_ttl
):
    """Check for last updated date of observable and delete if older than obsrvable TTL.

    :param table_name: table name
    :type table_name: str
    :param sec_token: security token
    :type sec_token: str
    :param observable_data: observable data to be deleted if older than observable TTL
    :type observable_data: dict
    :param observable_ttl: observable TTL
    :type observable_ttl: str
    :return: observable_removed
    :rtype: boolean
    """
    for observable_key, data in observable_data.items():

        observable_removed = False

        last_updated_at_value = (
            data.get(LAST_UPDATED_AT).get(VALUE) if data.get(LAST_UPDATED_AT) else None
        )

        if not last_updated_at_value:
            qpylib.log(LAST_UPDATED_VALUE_NOT_FOUND.format(observable_key))
            continue
        last_updated_at = last_updated_at_value.split(PLUS)[0]
        qpylib.log(
            DELETE_DATA_FOUND.format(observable_key, last_updated_at, table_name),
            level=LOG_LEVEL_INFO,
        )
        if last_updated_at <= observable_ttl:
            qpylib.log(
                DELETE_OBSERVABLE_DATA_IS_OLDER.format(last_updated_at, observable_ttl),
                level=LOG_LEVEL_INFO,
            )

            observable_removed = delete_observable(
                table_name, observable_key, data, sec_token
            )
            time.sleep(0.5)
    return observable_removed


def get_observable_deleted(
    response, upper_limit, table_name, sec_token, observable_ttl
):
    """Get response data , check for retention period.

    If older than ttl it is removed.
    :param response: response content
    :type response: dict
    :param table_name: table_name
    :type table_name: str
    :param sec_token: sec_token
    :type sec_token: str
    :param observable_ttl: observable time to live
    :type observable_ttl: int

    :return: lower limit,upper limit for pagination and response observable deleted
    :rtype: int,int,boolean
    """
    content = EIQApi.get_response_content(response)
    observable_data = None
    if content:
        observable_data = content.get(DATA)

    response_observable_deleted = False
    lower_limit = 0
    if observable_data:
        lower_limit = upper_limit + 1
        upper_limit += DEFAULT_UPPER_LIMIT
        observable_delete = check_last_updated_at_and_delete(
            table_name, sec_token, observable_data, observable_ttl
        )

        if observable_delete:
            qpylib.log(
                OBSERVABLE_DELETED.format(table_name),
                level=LOG_LEVEL_INFO,
            )
            response_observable_deleted = True
        else:
            qpylib.log(
                NO_DATA_TO_DELETE.format(table_name),
                level=LOG_LEVEL_INFO,
            )
            response_observable_deleted = False
    return lower_limit, upper_limit, response_observable_deleted


def fetch_observable_data_table(table_names, sec_token, observable_ttl):
    """Fetch observable data for each table and check for updated date .

    If older than ttl it is removed.
    :param content: response content
    :type content: dict

    """
    qpylib.log(DELETE_FETCH_DATA, level=LOG_LEVEL_INFO)

    console_address = qpylib.get_console_fqdn()
    url = HTTPS + str(console_address)

    qpylib.log(URL_MSG.format(url))
    request = CustomAuth.get_qradar_request(url)

    for table_name in table_names:

        lower_limit = DEFAULT_LOWER_LIMIT
        upper_limit = DEFAULT_UPPER_LIMIT
        response = True
        while True:
            headers = {
                HEADERS: {
                    SEC_KEY: sec_token,
                    RANGE: f"items={lower_limit}-{upper_limit}",
                }
            }
            response = request.send(
                GET,
                endpoint=QRADAR_REFERENCE_TABLE + SLASH + table_name,
                verify=DEFAULT_VERIFY_SSL,
                **headers,
            )
            qpylib.log(FETCH_DATA_FOR_TABLE.format(table_name), level=LOG_LEVEL_INFO)
            if response.status_code == STATUS_CODE_422:
                qpylib.log(
                    DELETE_REQUEST_PARAM_INVALID,
                    level=LOG_LEVEL_ERROR,
                )
                response = False
            elif response.status_code == STATUS_CODE_404:
                qpylib.log(
                    DELETE_REFERENCE_TABLE_DOES_NOT_EXIST.format(table_name),
                    level=LOG_LEVEL_ERROR,
                )
                response = False
            elif response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
                qpylib.log(
                    DELETE_ERROR_IN_FETCHING_TABLES.format(
                        response.status_code, str(response.content)
                    ),
                    level=LOG_LEVEL_ERROR,
                )
                response = False
            else:
                qpylib.log(
                    DELETE_SUCCESSFULLY_FETCHED_REFERENCE_TABLES,
                    level=LOG_LEVEL_INFO,
                )
                lower_limit, upper_limit, response = get_observable_deleted(
                    response, upper_limit, table_name, sec_token, observable_ttl
                )

            if not response:
                break
