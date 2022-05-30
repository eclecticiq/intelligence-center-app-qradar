"""Create Sighting from rules."""
# pylint: skip-file
import datetime
import json
import requests
import sys
import logging


conent_type = "application/json"
API_RESPONSE_ERROR = "API responded with error {code}: {error}"
CONNECTION_ERROR = "Connection Error: {err}"
logging.basicConfig(filename="eiq_sighting_custom_action.log")

LOG = logging.getLogger("eclecticiqapp.send_sightings")
LOG.setLevel(logging.DEBUG)

VERIFY = True


def format_ts(dt):
    """Format datetime.

    :param dt: Datetime obj
    :type: Datetime
    """
    return dt.replace(microsecond=0).isoformat() + "Z"


def send_request(method, url, headers, params, data):
    """Send an API request to the URL provided with headers and parameters.

    :param method: method get/post
    :type method: str
    :param url: API URL to send request
    :type url: str
    :param headers: Headers to be included in the request
    :type headers: dict
    :param params: Parameters to be sent to API
    :type params: dict
    :param data: payload details to be included in the request
    :type data: dict
    :return: API response
    :rtype: dict
    """
    response = {}

    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            data=json.dumps(data),
            params=params,
            verify=VERIFY,
            timeout=10,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if str(response.status_code).startswith("5"):
            LOG.critical(
                API_RESPONSE_ERROR.format(
                    code=response.status_code, error=str(response.content)
                )
            )
        else:
            LOG.error(
                API_RESPONSE_ERROR.format(
                    code=response.status_code, error=str(response.content)
                )
            )
        raise err

    except requests.exceptions.SSLError as err:
        LOG.error("SSL Error: certificate verify failed.")
        raise err
    except requests.exceptions.ConnectionError as err:
        LOG.error(CONNECTION_ERROR.format(err=err))
        raise err
    except requests.exceptions.Timeout as err:
        LOG.error(CONNECTION_ERROR.format(err=err))
        raise err
    except requests.exceptions.RequestException as err:
        LOG.error(CONNECTION_ERROR.format(err=err))
        LOG.error(
            API_RESPONSE_ERROR.format(
                code=response.status_code, error=str(response.content)
            )
        )
        raise err
    except Exception as err:
        LOG.error(
            API_RESPONSE_ERROR.format(
                code=response.status_code, error=str(response.content)
            )
        )
        raise err
    return response


class EclecticIQAPI:
    """EclecticIQ API."""

    def __init__(self, baseurl, eiq_version, api_key):
        self.verify_ssl = VERIFY
        self.baseurl = baseurl
        self.eiq_version = eiq_version
        self.headers = {
            "Authorization": "Bearer " + api_key,
            "Content-Type": conent_type,
            "Accept": conent_type,
        }

    def get_response_content(self, response):
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
            LOG.info("Response is not a valid json. Error: {}".format(error))
        return content

    def get_observables(self, obs_type, value):
        """Get the observalbes related to given entity.

        :param obs_type: observable type
        :type obs_type: str
        :param value: observable value
        :type value: str
        :return: List of observable ids
        :rtype: list
        """
        func_name = sys._getframe().f_code.co_name
        params = {"filter[type]": obs_type, "filter[value]": value}
        try:
            response = send_request(
                "get",
                url=self.baseurl + "/observables",
                headers=self.headers,
                params=params,
                data={},
            )

        except Exception:
            LOG.info(
                "{}: Can not find observables related to {}:{}.".format(
                    func_name, obs_type, value
                )
            )
            return []

        content = self.get_response_content(response)
        observables_list = []
        if content:
            for item in content["data"]:
                obs_id = item.get("id")
                observables_list.append(obs_id)
        return observables_list

    def create_sighting(self, record):
        """Create sighting for given record.

        :param record: configurations and recored values
        :type record: dict
        """
        func_name = sys._getframe().f_code.co_name
        LOG.debug("%s: Starting create_sighting from eiq_api.", func_name)
        extract_kind = record["type_eiq"]
        extract_value = record["value_eiq"]

        today = datetime.datetime.utcnow().date()
        today_begin = format_ts(
            datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
        )

        ts = format_ts(datetime.datetime.utcnow())

        description = "Automatically generated sighting of {} {}".format(
            extract_kind, extract_value
        )
        title = "Qradar detected {} {}".format(extract_kind, extract_value)

        LOG.debug(
            "%s: Creating sighting for record %s:%s",
            func_name,
            extract_kind,
            extract_value,
        )
        sighting = {
            "data": {
                "data": {
                    "confidence": "medium",
                    "description": description,
                    "type": "eclecticiq-sighting",
                    "timestamp": ts,
                    "title": title,
                    "security_control": {
                        "type": "information-source",
                        "identity": {
                            "name": "EclecticIQ Platform App for Qradar",
                            "type": "identity",
                        },
                        "time": {
                            "type": "time",
                            "start_time": today_begin,
                            "start_time_precision": "second",
                        },
                    },
                },
                "meta": {
                    "tags": ["Qradar Alert"],
                    "ingest_time": ts,
                },
            }
        }
        try:
            send_request(
                "post",
                url=self.baseurl + "/entities",
                headers=self.headers,
                params={},
                data=sighting,
            )
        except Exception:
            LOG.info(
                "{}: Sighting for record {}:{} has not been created.".format(
                    func_name, extract_kind, extract_value
                )
            )
            return
        LOG.info(
            "{}: Sighting for record {}:{} has been created.".format(
                func_name, extract_kind, extract_value
            )
        )
        return sighting


class QradarAPI:
    """Qradar APIs."""

    def __init__(self, baseurl, sec_token, app_id):
        self.verify_ssl = VERIFY
        self.baseurl = baseurl
        self.app_id = app_id
        self.headers = {
            "SEC": sec_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def store_sighting(self, data, obs_type, value):
        """Store the sighting created for showing in dashboards.

        :param data: data of sighting
        :type data: dict
        :param type: type of entity
        :type type: str
        :param value: value of entity
        :type value: str
        """
        func_name = sys._getframe().f_code.co_name
        url = self.baseurl + "/console/plugins/{}/app_proxy/store_sighting".format(
            self.app_id
        )
        data["value"] = value
        data["data"]["data"]["type"] = obs_type
        params = json.dumps(data)
        try:
            response = send_request(
                "get", url, headers=self.headers, params=params, data=None
            )
            return response.status_code
        except Exception:
            LOG.exception(
                "%s: Sighting record %s:%s has not been stored.",
                func_name,
                obs_type,
                value,
            )
            return 400


if __name__ == "__main__":
    eiq_url = sys.argv[1]
    eiq_version = sys.argv[2]
    eiq_api_key = sys.argv[3]
    qradar_url = sys.argv[4]
    sec_token = sys.argv[5]
    app_id = sys.argv[6]
    record = {}
    record["type_eiq"] = sys.argv[7]
    record["value_eiq"] = sys.argv[8]

    eiq_obj = EclecticIQAPI(
        baseurl=eiq_url, eiq_version=eiq_version, api_key=eiq_api_key
    )
    obsrvables = eiq_obj.get_observables(record["type_eiq"], record["value_eiq"])
    ret_value = eiq_obj.create_sighting(record)
    if ret_value:
        qradar_obj = QradarAPI(qradar_url, sec_token, app_id)
        return_val = qradar_obj.store_sighting(
            ret_value, record["type_eiq"], record["value_eiq"]
        )
        LOG.info("sighting is stored")
        if str(return_val).startswith("2"):
            LOG.info(
                "sighting for type:{} value:{} is stored".format(
                    record["type_eiq"], record["value_eiq"]
                )
            )
        else:
            LOG.info(
                "sighting for type:{} value:{} is not stored".format(
                    record["type_eiq"], record["value_eiq"]
                )
            )
