"""API views."""

import datetime
import os
import json
import re
from app.checkpoint_store import remove_checkpoint
from app.constants.defaults import (
    DEFAULT_CONFIDENCE_LEVEL,
    DEFAULT_INDICATOR_TYPE,
    DEFAULT_TIME,
)
from app.database.handler import insert_data_to_table, query_operations
from app.queries.sqllite.select import SELECT_TABLE_QUERIES
from app.routes.charts import (
    get_bar_graph_data,
    get_bar_graph_data_by_observable_type,
    get_pie_chart_data,
)
from app.routes.utils import get_entity_data, get_filters,get_unverified_cert
from app.cipher import Cipher
from app.collector.eiq_data import EIQApi, QradarApi
from app.configs.datastore import DATA_STORE_DIR, DATA_STORE_FILE, DATA_STORE_SETUP_FILE
from app.constants.general import (
    API_KEY,
    APP_ID,
    AUTH_USER,
    BACKFILL_TIME,
    BAR_CHART1,
    BAR_CHART2,
    COMMA_STRING,
    CONFIDENCE_KEY,
    CONFIDENCE_LEVEL,
    CONTEXT,
    COUNT,
    DATA,
    DESC_KEY,
    DOMAIN,
    EIQ_SIGHTING,
    EMAIL,
    END_TIME,
    GLUE_COLONS,
    HELLO_TEMPLATE,
    HOST,
    HTTPS,
    ID,
    INDICATOR_TYPE,
    INTERVAL,
    IPV4,
    LOG_LEVEL_INFO,
    MD5_HASH,
    META,
    NAME,
    OBSERVABLE_TIME_TO_LIVE,
    OBSERVABLE_TYPES,
    OUTGOING_FEEDS,
    PIE_DATA,
    QRADAR_SECURITY_TOKEN,
    SEARCH_SIGHTING_COUNT_BY_CONFIDENCE,
    SEARCH_SIGHTING_COUNT_BY_OBSERVABLE_TYPE,
    SEARCH_SIGHTING_COUNT_BY_TIME,
    SECURITY_TOKEN,
    SELECT_LEVEL,
    SELECT_TYPE,
    SETUP_TEMPLATE,
    SHARED,
    SIGHTING_DESC,
    SIGHTING_TAGS,
    SIGHTING_TITLE,
    SIGHTING_TYPE,
    SIGHTING_VALUE,
    SLASH,
    START_TIME,
    STATUS_CODE_200,
    STATUS_STRING,
    STR_TWO,
    TAGS_KEY,
    TIME_KEY,
    TITLE,
    TYPE,
    URI,
    VALUE,
    VERSION,
)
from app.constants.messages import (
    CHECKPOINT_REMOVED,
    CONFIGURATION_SAVED_SUCCESSFULLY,
    DATA_OF_OUTGOING_FEED_DELETED_SUCCESSFULLY,
    DELETE_REFERNCE_TABLES,
    GET_CONFIGURATION,
    GET_OUTGOING_FEEDS,
    HOST_NAME_SHOULD_START_WITH,
    MISSING_PERMISSIONS,
    LOOKUP_OBS_CALLED,
    REMOVING_CHECKPOINT,
    SAVE_CONFIGURATION,
    SETUP_CALLED,
    SIGHTING_NOT_CREATED,
    TABLE_DELETED_SUCCESSFULLY,
    TEST_CONNECTION,
    TEST_CONNECTION_SUCCESSFULL,
    URL_INVALID,
    USER_UNAUTHORIZED,
    VIEW_CREATED_SIGHTING,
    REQUEST_UNAUTHORIZED,
    MISSING_PERMISSIONS,
    REQUEST_DOES_NOT_EXIST,
    INTERNAL_SERVER_ERROR,
    BAD_REQUEST,
    BAD_REQUEST_CHECK_LOGS,
    INCORRECT_QRADAR_SEC_TOKEN


)
from app.constants.scheduler import SCHEDULER_INTERVAL
from app.datastore import (
    overwrite_data_store,
    overwrite_setup_data_store,
    read_data_store,
)
from app.jobs.eiq import send_pull_event
from app.utils.formatters import convert_formatted_data, formatted_setup_data
from flask import Blueprint, jsonify, request
from flask.templating import render_template
from qpylib import qpylib

eiq = Blueprint("eiq", __name__, url_prefix="/")


@eiq.route("/")
@eiq.route("/index")
def home_page():
    """Render home page.

    :return: home template
    :rtype: html
    """
    config = {
        AUTH_USER: "",
        HOST: "",
        VERSION: "",
        API_KEY: "",
        QRADAR_SECURITY_TOKEN: "",
        SCHEDULER_INTERVAL: "",
        STATUS_STRING: "",
    }
    return render_template(HELLO_TEMPLATE, context=config)


@eiq.route("/outgoing_feeds", methods=["GET"])
def get_feeds():
    """Get outgoing feeds from EclecticIQ platform.

    :return: List of objects comprising name and id data"
            [{"id": 1,
              "name": "Poll TAXII Stand"},
             {"id": 2,
              "name": "Download STIX TAXII Stand"}]
    :rtype: response json and status_cde
    """
    qpylib.log(GET_OUTGOING_FEEDS, level=LOG_LEVEL_INFO)
    eiq_api = EIQApi()
    feeds_data = eiq_api.fetch_outgoing_feeds()
    return jsonify({DATA: feeds_data}), STATUS_CODE_200


@eiq.route("/save", methods=["POST"])
def save_configuration():
    """Save the configuration in data store for authorized users.

    :return: response message and status code
    :rtype: json response , status_code
    """
    qpylib.log(SAVE_CONFIGURATION, level=LOG_LEVEL_INFO)
    form = request.form

    auth_user = str(form.get(NAME)).strip()
    host = str(form.get(HOST)).strip()
    api_key = str(form.get(API_KEY)).strip()
    qradar_security_token = str(form.get(SECURITY_TOKEN)).strip()
    

    config = {
        AUTH_USER: auth_user,
        HOST: host,
        VERSION: "",
        API_KEY: api_key,
        QRADAR_SECURITY_TOKEN: qradar_security_token,
    }

    if not host.startswith(HTTPS):
        qpylib.log(HOST_NAME_SHOULD_START_WITH)
        config[STATUS_STRING] = HOST_NAME_SHOULD_START_WITH
        return render_template(HELLO_TEMPLATE, context=config) 

    url_split = host.split(HTTPS)
    url_split = url_split[1]
    if len(url_split.split(SLASH)) > 1:
        host_name = url_split.split(SLASH)[0]
        version_split = "/".join(url_split.split(SLASH)[1:])
    else:
        qpylib.log(URL_INVALID)
        config[STATUS_STRING] = URL_INVALID
        return render_template(HELLO_TEMPLATE, context=config) 
        
    config[HOST]= HTTPS +host_name
    config[VERSION]= version_split

    qpylib.log(type(config[HOST]))
    is_self_signed_cert = True if str(form.get("is_self_signed_cert")).strip() == "on" else False
    config["is_self_signed_cert"]= is_self_signed_cert
    if is_self_signed_cert: # this param should be read only in save
        # get the certificate and save it in certs.
        save_path = os.getcwd() + "/" + "store" + "/" + "certs"
        if os.path.exists(save_path + "/"+"certfile.pem"):
            verify_ssl = save_path + "/"+"certfile.pem"
        else:
            qpylib.log("Certificate not found in backend")
            config[STATUS_STRING] = "Certificate not found in backend"
            return render_template(HELLO_TEMPLATE, context=config)
    else:
        verify_ssl = True

    config["verify_ssl"]= verify_ssl

    # Call to  api to check for authentication
    eiq_api = EIQApi(config)
    missing_permissions, eiq_api_status_code = eiq_api.validate_user_permissions()

    qradar_api = QradarApi(config)
    qradar_api_response = qradar_api.get_reference_tables()

    if eiq_api_status_code == 401:
        qpylib.log(REQUEST_UNAUTHORIZED, level=LOG_LEVEL_INFO)
        config[STATUS_STRING] = REQUEST_UNAUTHORIZED
    elif eiq_api_status_code == 403:
        qpylib.log(MISSING_PERMISSIONS, level=LOG_LEVEL_INFO)
        config[STATUS_STRING] = MISSING_PERMISSIONS
    elif eiq_api_status_code == 404:
        qpylib.log(REQUEST_DOES_NOT_EXIST, level=LOG_LEVEL_INFO)
        config[STATUS_STRING] = REQUEST_DOES_NOT_EXIST
    elif eiq_api_status_code == 500:
        qpylib.log(INTERNAL_SERVER_ERROR, level=LOG_LEVEL_INFO)
        config[STATUS_STRING] = INTERNAL_SERVER_ERROR
    elif eiq_api_status_code == 400:
        qpylib.log(BAD_REQUEST, level=LOG_LEVEL_INFO)
        config[STATUS_STRING] =  BAD_REQUEST_CHECK_LOGS
        
    elif qradar_api_response not in [200,201]:
        qpylib.log(INCORRECT_QRADAR_SEC_TOKEN, level=LOG_LEVEL_INFO)
        config[STATUS_STRING] = INCORRECT_QRADAR_SEC_TOKEN

    elif not missing_permissions and qradar_api_response == STATUS_CODE_200 and eiq_api_status_code== STATUS_CODE_200:
        config[API_KEY] = Cipher(API_KEY, SHARED).encrypt(api_key)
        config[QRADAR_SECURITY_TOKEN] = Cipher(QRADAR_SECURITY_TOKEN, SHARED).encrypt(
            qradar_security_token
        )
        qpylib.log(config)
        overwrite_data_store(config)
        config[API_KEY] = api_key
        config[QRADAR_SECURITY_TOKEN] = qradar_security_token
        config[HOST] = host

        config[STATUS_STRING] = CONFIGURATION_SAVED_SUCCESSFULLY
        return render_template(SETUP_TEMPLATE, context=config)

    config[STATUS_STRING] = MISSING_PERMISSIONS.format(missing_permissions)
    qpylib.log(MISSING_PERMISSIONS.format(missing_permissions))

    return render_template(HELLO_TEMPLATE, context=config)


@eiq.route("/get", methods=["GET"])
def get_configuration():
    """Fetch configurations from the store .

    :return: json response consisting of name,host,version and status code
    :rtype: response
    """
    qpylib.log(GET_CONFIGURATION, level=LOG_LEVEL_INFO)
    config_data = read_data_store(DATA_STORE_DIR, DATA_STORE_FILE)
    setup_data = read_data_store(DATA_STORE_DIR, DATA_STORE_SETUP_FILE)

    response = {}
    if config_data:
        response = {
            AUTH_USER: config_data.get(AUTH_USER),
            HOST: config_data.get(HOST),
            VERSION: config_data.get(VERSION),
            "is_self_signed_cert": config_data.get("is_self_signed_cert")
        }
    if setup_data:
        response.update(
            {
                OUTGOING_FEEDS: convert_formatted_data(setup_data.get(OUTGOING_FEEDS)),
                OBSERVABLE_TIME_TO_LIVE: setup_data.get(OBSERVABLE_TIME_TO_LIVE),
                BACKFILL_TIME: setup_data.get(BACKFILL_TIME),
                OBSERVABLE_TYPES: setup_data.get(OBSERVABLE_TYPES),
                INTERVAL: setup_data.get(INTERVAL),
            }
        )

    return jsonify(response), STATUS_CODE_200


@eiq.route("/test_connection", methods=["POST"])
def test_connection():
    """Test the connection to EIQ platform for  authorized users.

    :return: response message and status code
    :rtype: json response , status_code
    """
    qpylib.log(TEST_CONNECTION, level=LOG_LEVEL_INFO)
    form = request.form
    qpylib.log(request.form)
    auth_user = str(form.get(NAME)).strip()
    host = str(form.get(HOST)).strip()
    api_key = str(form.get(API_KEY)).strip()
    qradar_security_token = str(form.get(SECURITY_TOKEN)).strip()

    is_self_signed_cert = True if str(form.get("is_self_signed_cert")).strip() == "on" else False  # if the user selects self signed cert upload the certificate in the backend manually
    # is_self_signed_cert = False # for testing , will be rempoved later
    
    config = {
        AUTH_USER: auth_user,
        HOST: host,
        VERSION: "",
        API_KEY: api_key,
        QRADAR_SECURITY_TOKEN: qradar_security_token,
        "is_self_signed_cert": is_self_signed_cert
    }
    
    

    if not host.startswith(HTTPS):
        qpylib.log(HOST_NAME_SHOULD_START_WITH)
        config[STATUS_STRING] = HOST_NAME_SHOULD_START_WITH
        return render_template(HELLO_TEMPLATE, context=config) 

    url_split = host.split(HTTPS)
    url_split = url_split[1]
    if len(url_split.split(SLASH)) > 1:
        host_name = url_split.split(SLASH)[0]
        version_split = "/".join(url_split.split(SLASH)[1:])
    else:
        qpylib.log(URL_INVALID)
        config[STATUS_STRING] = URL_INVALID
        return render_template(HELLO_TEMPLATE, context=config) 
        
    config[HOST]= HTTPS+host_name
    config[VERSION]= version_split

    if is_self_signed_cert:
        # get the certificate and save it in certs.
        cwd = os.getcwd() # /opt/app-root
        save_path = cwd + "/" + "store" + "/" + "certs"
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        get_unverified_cert(host_name,443,save_path)
        if os.path.exists(save_path + "/"+"certfile.pem"):
            verify_ssl = save_path + "/"+"certfile.pem"
        else:
            qpylib.log("Failed to download the certificate")
            config[STATUS_STRING] = "Failed to fetch the certificate"
            return render_template(HELLO_TEMPLATE, context=config)
    else:
        verify_ssl = True

    config["verify_ssl"]= verify_ssl
    
    eiq_api = EIQApi(config)
    missing_permissions, eiq_api_status_code = eiq_api.validate_user_permissions()
    qpylib.log(eiq_api_status_code)
    qpylib.log(type(eiq_api_status_code))
    
    qradar_api = QradarApi(config)
    qradar_api_response = qradar_api.get_reference_tables()

    if eiq_api_status_code == 401:
        qpylib.log(REQUEST_UNAUTHORIZED, level=LOG_LEVEL_INFO)
        config[STATUS_STRING] = REQUEST_UNAUTHORIZED
    elif eiq_api_status_code == 403:
        qpylib.log(MISSING_PERMISSIONS, level=LOG_LEVEL_INFO)
        config[STATUS_STRING] = MISSING_PERMISSIONS
    elif eiq_api_status_code == 404:
        qpylib.log(REQUEST_DOES_NOT_EXIST, level=LOG_LEVEL_INFO)
        config[STATUS_STRING] = REQUEST_DOES_NOT_EXIST
        qpylib.log(INTERNAL_SERVER_ERROR, level=LOG_LEVEL_INFO)
        config[STATUS_STRING] = INTERNAL_SERVER_ERROR
    elif eiq_api_status_code == 400:
        qpylib.log(BAD_REQUEST, level=LOG_LEVEL_INFO)
        config[STATUS_STRING] =  BAD_REQUEST_CHECK_LOGS
        
    elif qradar_api_response not in [200,201]:
        qpylib.log(INCORRECT_QRADAR_SEC_TOKEN, level=LOG_LEVEL_INFO)
        config[STATUS_STRING] = INCORRECT_QRADAR_SEC_TOKEN
        

    #  eiq_api_status_code not in [200, 201] or qradar_api_response not in [200, 201]:
    #     config[STATUS_STRING] = USER_UNAUTHORIZED
    elif not missing_permissions and qradar_api_response== STATUS_CODE_200 and eiq_api_status_code== STATUS_CODE_200:
        config[STATUS_STRING] = TEST_CONNECTION_SUCCESSFULL
    else:
        qpylib.log(MISSING_PERMISSIONS.format(missing_permissions))
        config[STATUS_STRING] = MISSING_PERMISSIONS.format(missing_permissions)
    config[HOST] = host
    return render_template(HELLO_TEMPLATE, context=config)


@eiq.route("/setup", methods=["POST"])
def setup():
    """Start job to fetch observable data.

    :return: json response and status code
    :rtype: json response and status code
    """
    qpylib.log(SETUP_CALLED, level=LOG_LEVEL_INFO)
    data = request.form.to_dict(flat=False)
    formatted_data = formatted_setup_data(data)
    overwrite_setup_data_store(formatted_data)
    qpylib.log(REMOVING_CHECKPOINT)
    remove_checkpoint()
    qpylib.log(CHECKPOINT_REMOVED)
    send_pull_event()

    config_data = read_data_store(DATA_STORE_DIR, DATA_STORE_FILE)
    setup_data = read_data_store(DATA_STORE_DIR, DATA_STORE_SETUP_FILE)
    config = {}
    if config_data and setup_data:
        config = {
            AUTH_USER: config_data.get(AUTH_USER),
            HOST: config_data.get(HOST),
            VERSION: config_data.get(VERSION),
            OUTGOING_FEEDS: convert_formatted_data(setup_data.get(OUTGOING_FEEDS)),
            OBSERVABLE_TIME_TO_LIVE: setup_data.get(OBSERVABLE_TIME_TO_LIVE),
            BACKFILL_TIME: setup_data.get(BACKFILL_TIME),
            OBSERVABLE_TYPES: setup_data.get(OBSERVABLE_TYPES),
            INTERVAL: setup_data.get(INTERVAL),
        }
    config[STATUS_STRING] = "Configuration saved successfully."
    return render_template(HELLO_TEMPLATE, context=config)


@eiq.route("/delete_tables", methods=["POST"])
def delete_reference_tables():
    """Fetch configurations from the store .

    :return: json response consisting of name,host,version and status code
    :rtype: response
    """
    qpylib.log(DELETE_REFERNCE_TABLES, level=LOG_LEVEL_INFO)
    data = request.form.to_dict(flat=True)
    outgoing_feed = list(data.keys())[1]
    qradar_api = QradarApi()
    qradar_api_response = qradar_api.get_reference_data_tables(outgoing_feed)
    qpylib.log(TABLE_DELETED_SUCCESSFULLY.format(qradar_api_response))
    name = outgoing_feed.split(GLUE_COLONS)[0]

    config_data = read_data_store(DATA_STORE_DIR, DATA_STORE_FILE)
    setup_data = read_data_store(DATA_STORE_DIR, DATA_STORE_SETUP_FILE)
    config = {}
    if config_data:
        config = {
            AUTH_USER: config_data.get(AUTH_USER),
            HOST: config_data.get(HOST),
            VERSION: config_data.get(VERSION),
        }
    if setup_data:
        config.update(
            {
                OUTGOING_FEEDS: convert_formatted_data(setup_data.get(OUTGOING_FEEDS)),
                OBSERVABLE_TIME_TO_LIVE: setup_data.get(OBSERVABLE_TIME_TO_LIVE),
                BACKFILL_TIME: setup_data.get(BACKFILL_TIME),
                OBSERVABLE_TYPES: setup_data.get(OBSERVABLE_TYPES),
                INTERVAL: setup_data.get(INTERVAL),
            }
        )
    config[STATUS_STRING] = DATA_OF_OUTGOING_FEED_DELETED_SUCCESSFULLY.format(name)
    return render_template("setup.html", context=config)


@eiq.route("/lookup_observables", methods=["GET"])
def lookup_observables():
    """Start job to fetch observable data.

    :return: json response and status code
    :rtype: json response and status code
    """
    value = request.args.get("search_value")
    if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", value):
        sighting_type = IPV4
    elif re.match(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+", value):
        sighting_type = EMAIL
    elif re.match(r"[^\:]+\:\/\/[\S]+", value):
        sighting_type = URI
    elif re.match(r"[\S]+\.[\S]+", value):
        sighting_type = DOMAIN
    elif re.match(r"^[a-f0-9A-F]{32}$", value):
        sighting_type = MD5_HASH
    qpylib.log(LOOKUP_OBS_CALLED, level=LOG_LEVEL_INFO)
    eiq_api = EIQApi()
    response = eiq_api.lookup_observables(sighting_type, value)
    qpylib.log(response.content)
    final_data = []
    data = []
    if str(response.status_code).startswith(STR_TWO):
        data = json.loads(response.content)
        data = data.get("data")
        for data_item in data:
            if data_item.get("entities"):
                entity_data = get_entity_data(data_item, eiq_api)
                # final_data.append(entity_data)
    qpylib.log(entity_data)
    final_data.append(value)
    return render_template("lookup_observables.html", context=entity_data)


@eiq.route("/create_sighting", methods=["POST", "GET"])
def create_sighting():
    """Start job to fetch observable data.

    :return: json response and status code
    :rtype: json response and status code
    """
    if request.method == "GET":
        value = request.args.get("sighting_value")
        qpylib.log(f"value: {value}, type:{type(value)}")
        if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", value):
            sighting_type = IPV4
        elif re.match(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+", value):
            sighting_type = EMAIL
        elif re.match(r"[^\:]+\:\/\/[\S]+", value):
            sighting_type = EMAIL
        elif re.match(r"[\S]+\.[\S]+", value):
            sighting_type = DOMAIN
        elif re.match(r"^[a-f0-9A-F]{32}$", value):
            sighting_type = MD5_HASH
        else:
            sighting_type = "unknown"
        context = {}
        context[TYPE] = sighting_type
        context[VALUE] = value
        context[STATUS_STRING] = ""
    else:
        form_data = request.form.to_dict(flat=True)
        response = EIQApi().create_sighting(
            form_data[SIGHTING_VALUE],
            form_data[SIGHTING_DESC],
            form_data[SIGHTING_TITLE],
            form_data[SIGHTING_TAGS].split(COMMA_STRING),
            form_data[SIGHTING_TYPE],
            form_data[CONFIDENCE_LEVEL],
        )
        context = {}
        context[TYPE] = form_data[SIGHTING_TYPE]
        context[VALUE] = form_data[SIGHTING_VALUE]
        qpylib.log(str(response.status_code))
        if str(response.status_code).startswith(STR_TWO):        
            content = EIQApi.get_response_content(response)
            context[STATUS_STRING] = VIEW_CREATED_SIGHTING.format(content.get(DATA).get(ID))
        else:
            context[STATUS_STRING] = SIGHTING_NOT_CREATED.format(response.content)

    return render_template("sighting.html", context=context)


@eiq.route("/store_sighting", methods=["GET"])
def store_sighting():
    """Store sightings created by custom scripts in database.

    :return:
    :rtype:
    """
    form = request.args.to_dict(flat=True)
    form = next(iter(form))

    sighting_data = json.loads(form)

    results = [
        {
            VALUE: sighting_data[VALUE],
            TYPE: sighting_data[DATA][DATA][TYPE],
            TITLE: sighting_data[DATA][DATA][TITLE],
            DESC_KEY: sighting_data[DATA][DATA][DESC_KEY],
            CONFIDENCE_KEY: sighting_data[DATA][DATA][CONFIDENCE_KEY],
            TAGS_KEY: str(sighting_data[DATA][META][TAGS_KEY]),
            TIME_KEY: int(datetime.datetime.now().timestamp()),
        }
    ]
    insert_data_to_table(results, EIQ_SIGHTING, list(results[0].keys()))
    return jsonify({"status": "Stored"}), STATUS_CODE_200


@eiq.route("/eiqLookupObs_func", methods=["GET"])
def eiq_lookup_obs_func():
    """Send App ID and value to template."""
    context = request.args.get(CONTEXT)
    return jsonify({APP_ID: qpylib.get_app_id(), "search_value": context})


@eiq.route("/eiqCreateSighting_func", methods=["GET"])
def eiq_create_sighting_func():
    """Send App ID and value to template."""
    context = request.args.get(CONTEXT)
    return jsonify({APP_ID: qpylib.get_app_id(), "sightings_value": context})


@eiq.route("/dashboard", methods=["GET"])
def get_dashboard():
    """Start job to fetch observable data.

    :return: json response and status code
    :rtype: json response and status code
    """
    filters = get_filters(
        DEFAULT_INDICATOR_TYPE, DEFAULT_CONFIDENCE_LEVEL, DEFAULT_TIME
    )
    pie_query = SELECT_TABLE_QUERIES[SEARCH_SIGHTING_COUNT_BY_CONFIDENCE].format(
        filters[SELECT_LEVEL],
        filters[SELECT_TYPE],
        filters[START_TIME],
        filters[END_TIME],
    )

    results = query_operations(pie_query)
    pie_data = []
    chart_data = {}
    if results:
        pie_data = get_pie_chart_data(results, COUNT, CONFIDENCE_KEY)

    chart_data[PIE_DATA] = pie_data

    bar_query_1 = SELECT_TABLE_QUERIES[SEARCH_SIGHTING_COUNT_BY_TIME].format(
        filters[SELECT_LEVEL],
        filters[SELECT_TYPE],
        filters[START_TIME],
        filters[END_TIME],
    )

    results = query_operations(bar_query_1)
    bar_chart1 = []
    if results:
        bar_chart1 = get_bar_graph_data(results, COUNT, TIME_KEY)

    chart_data[BAR_CHART1] = bar_chart1

    bar_query_2 = SELECT_TABLE_QUERIES[SEARCH_SIGHTING_COUNT_BY_OBSERVABLE_TYPE].format(
        filters[SELECT_LEVEL],
        filters[SELECT_TYPE],
        filters[START_TIME],
        filters[END_TIME],
    )

    results = query_operations(bar_query_2)

    bar_chart2 = []
    if results:
        bar_chart2 = get_bar_graph_data_by_observable_type(results, COUNT, TYPE)

    chart_data[BAR_CHART2] = bar_chart2

    return render_template("dashboard.html", context=chart_data)


@eiq.route("/get_chart_data", methods=["POST"])
def get_chart_data():
    """Send chart data."""
    form_data = request.form.to_dict(flat=True)

    filters = get_filters(
        form_data[INDICATOR_TYPE], form_data[CONFIDENCE_LEVEL], form_data[TIME_KEY]
    )
    pie_query = SELECT_TABLE_QUERIES[SEARCH_SIGHTING_COUNT_BY_CONFIDENCE].format(
        filters[SELECT_LEVEL],
        filters[SELECT_TYPE],
        filters[START_TIME],
        filters[END_TIME],
    )

    results = query_operations(pie_query)
    pie_data = []
    chart_data = {}
    if results:
        pie_data = get_pie_chart_data(results, COUNT, CONFIDENCE_KEY)

    chart_data[PIE_DATA] = pie_data

    bar_query_1 = SELECT_TABLE_QUERIES[SEARCH_SIGHTING_COUNT_BY_TIME].format(
        filters[SELECT_LEVEL],
        filters[SELECT_TYPE],
        filters[START_TIME],
        filters[END_TIME],
    )

    results = query_operations(bar_query_1)
    bar_chart1 = []
    if results:
        bar_chart1 = get_bar_graph_data(results, COUNT, TIME_KEY)

    chart_data[BAR_CHART1] = bar_chart1

    bar_query_2 = SELECT_TABLE_QUERIES[SEARCH_SIGHTING_COUNT_BY_OBSERVABLE_TYPE].format(
        filters[SELECT_LEVEL],
        filters[SELECT_TYPE],
        filters[START_TIME],
        filters[END_TIME],
    )

    results = query_operations(bar_query_2)
    bar_chart2 = []
    if results:
        bar_chart2 = get_bar_graph_data_by_observable_type(results, COUNT, TYPE)

    chart_data[BAR_CHART2] = bar_chart2

    return render_template("dashboard.html", context=chart_data)
    
