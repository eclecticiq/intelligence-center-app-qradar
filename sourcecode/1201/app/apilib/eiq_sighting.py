#!/usr/bin/env python
__author__ = "EclecticIQ"

import datetime
import json
import requests
import re
import sys
import logging

logging.basicConfig()

LOG = logging.getLogger("eclecticiqapp.send_sightings")

PATHS = {
    "2.1": {
        "auth": "/api/auth",
        "feeds_list": "/private/outgoing-feed-download/",
        "feed_content_blocks": "/private/outgoing-feed-download/{0}/runs/latest",
        "groups": "/private/groups/",
        "entities": "/private/entities/",
    },
    "2.0": {
        "auth": "/api/auth",
        "feeds_list": "/api/outgoing-feed-download/",
        "feed_content_blocks": "/api/outgoing-feed-download/{0}/runs/latest",
        "groups": "/api/groups/",
        "entities": "/api/entities/",
    },
}


def format_ts(dt):
    return dt.replace(microsecond=0).isoformat() + "Z"


class EclecticIQ_api(object):
    def __init__(
        self,
        baseurl,
        eiq_version,
        username,
        password,
        verify_ssl=True,
        proxy_ip=None,
        proxy_username=None,
        proxy_password=None,
    ):
        self.verify_ssl = verify_ssl
        self.proxy_ip = proxy_ip
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.baseurl = baseurl
        self.eiq_version = eiq_version
        if eiq_version < "2.1":
            self.eiq_version_path = "2.0"
        elif eiq_version == "FC":
            self.eiq_version_path = "FC"
        else:
            self.eiq_version_path = "2.1"
        self.headers = {
            "user-agent": "qradar-integration",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.proxies = None
        if self.proxy_ip:
            if self.proxy_username and self.proxy_password:
                self.proxies = {
                    "http": "http://"
                    + self.proxy_username
                    + ":"
                    + self.proxy_password
                    + "@"
                    + self.proxy_ip
                    + "/",
                    "https": "http://"
                    + self.proxy_username
                    + ":"
                    + self.proxy_password
                    + "@"
                    + self.proxy_ip
                    + "/",
                }
            else:
                self.proxies = {
                    "http": "http://" + self.proxy_ip + "/",
                    "https": "http://" + self.proxy_ip + "/",
                }
        self.get_outh_token(username, password)

    def send_api_request(self, method, path, params=None, data=None, timeout=30):
        func_name = sys._getframe().f_code.co_name

        if bool(re.search("^http.", path)):
            url = path
        else:
            url = self.baseurl + path

        r = None
        try:
            if method == "post":
                r = requests.post(
                    url,
                    headers=self.headers,
                    params=params,
                    data=json.dumps(data),
                    verify=self.verify_ssl,
                    proxies=self.proxies,
                    timeout=timeout,
                )
            elif method == "get":
                r = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    verify=self.verify_ssl,
                    proxies=self.proxies,
                    timeout=timeout,
                )
            else:
                LOG.error(
                    "EclecticIQ_api.{0}: Unknown method:{1}".format(func_name, method)
                )
                raise Exception
        except Exception:

            LOG.error(
                "EclecticIQ_api.{0}: Could not perform request to EclecticIQ VA: {1}:{2}".format(
                    func_name, method, url
                )
            )
            return "Could not perform request to EclecticIQ"

        if r and r.status_code in [100, 200, 201]:
            return r
        else:
            if not r:
                msg = "Could not perform request to EclecticIQ VA: {}: {}".format(
                    method, url
                )
                LOG.error(
                    "EclecticIQ_api.{0}: Could not perform request to EclecticIQ VA: {1}: {2}".format(
                        func_name, method, url
                    )
                )
                raise Exception(msg)
            try:
                err = r.json()
                detail = err["errors"][0]["detail"]
                LOG.error(
                    "EclecticIQ_api.{0}: EclecticIQ VA returned an error, code:[{1}], reason:[{2}], URL: [{3}], details:[{4}]".format(
                        func_name, r.status_code, r.reason, r.url, detail
                    )
                )
            except Exception:
                err = r.json()
                detail = err["errors"][0]["detail"]
                msg = "Could not perform request to EclecticIQ VA: {}".format(detail)
                LOG.error(
                    "EclecticIQ_api.{0}: EclecticIQ VA returned an error, code:[{1}], reason:[{2}], URL: [{3}], details:[{4}]".format(
                        func_name, r.status_code, r.reason, r.url, detail
                    )
                )
            raise Exception(msg)

    def get_outh_token(self, username, password):
        func_name = sys._getframe().f_code.co_name
        LOG.info("%s: Authenticating using username: %s", func_name, username)

        if (re.match("^[\dabcdef]{64}$", password)) == None:
            try:
                r = self.send_api_request(
                    "post",
                    path=PATHS[self.eiq_version_path]["auth"],
                    data={"username": username, "password": password},
                )
                self.headers["Authorization"] = "Bearer " + r.json()["token"]
                LOG.debug("%s: Authentication was successful.", func_name)
            except Exception:
                LOG.error("%s: Authentication failed.", func_name)
                raise
        else:
            try:
                self.headers["Authorization"] = "Bearer " + password

                r = self.send_api_request(
                    "get",
                    path="/api",
                    headers=self.headers,
                )

                LOG.debug("%s: Authentication was successful.", func_name)
            except Exception:
                LOG.error("%s: Authentication failed.", func_name)
                raise

    def get_source_group_uid(self, group_name):
        func_name = sys._getframe().f_code.co_name
        LOG.info(
            '%s: Requesting source id for specified group, name=["%s"]',
            func_name,
            group_name,
        )
        r = self.send_api_request(
            "get",
            path=PATHS[self.eiq_version_path]["groups"],
            params="filter[name]=" + str(group_name),
        )

        if not r.json()["data"]:
            LOG.error(
                "%s: Something went wrong fetching the group id. Please note the source group name is case sensitive! Received response: %s",
                func_name,
                str(r.json()),
            )
            return "error_in_fetching_group_id"
        else:
            LOG.info("%s: Source group id received %s", func_name, str(r.json()))
            LOG.debug(
                "%s: Source group id is: %s",
                func_name,
                str(r.json()["data"][0]["source"]),
            )
            return r.json()["data"][0]["source"]

    def create_sighting(self, source, record):
        func_name = sys._getframe().f_code.co_name
        LOG.debug("%s: Starting create_sighting from eiq_api.", func_name)
        extract_kind = record["type_eiq"]
        extract_value = record["value_eiq"]

        today = datetime.datetime.utcnow().date()
        today_begin = format_ts(
            datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
        )

        ts = format_ts(datetime.datetime.utcnow())

        description = "Automatically generated sighting of {0} {1}".format(
            extract_kind, extract_value
        )
        title = "Qradar detected {0} {1}".format(extract_kind, extract_value)

        LOG.debug(
            "%s: Creating sighting for record %s:%s",
            func_name,
            extract_kind,
            extract_value,
        )

        if float(self.eiq_version) >= 2.2:
            sighting = {
                "data": {
                    "data": {
                        "confidence": {"type": "confidence", "value": "Medium"},
                        "description": description,
                        "description_structuring_format": "html",
                        "type": "eclecticiq-sighting",
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
                        "manual_extracts": [
                            {
                                "link_type": "sighted",
                                "kind": extract_kind,
                                "value": extract_value,
                            }
                        ],
                        "taxonomy": [],
                        "tags": ["Qradar Alert"],
                        "ingest_time": ts,
                    },
                    "sources": [{"source_id": source}],
                }
            }
        else:
            sighting = {
                "data": {
                    "data": {
                        "confidence": {"type": "confidence", "value": "Low"},
                        "description": description,
                        "related_extracts": [
                            {
                                "type": "eclecticiq-extract",
                                "kind": extract_kind,
                                "value": extract_value,
                            }
                        ],
                        "description_structuring_format": "html",
                        "type": "eclecticiq-sighting",
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
                        "source": source,
                        "taxonomy": [],
                        "tags": ["Qradar Alert"],
                        "ingest_time": ts,
                    },
                }
            }

        r = self.send_api_request(
            "post", path=PATHS[self.eiq_version_path]["entities"], data=sighting
        )

        if r.status_code in [100, 200, 201]:
            LOG.info(
                "%s: Sighting for record %s:%s has been created.",
                func_name,
                extract_kind,
                extract_value,
            )
        else:
            LOG.info(
                "%s: Sighting for record %s:%s has not been created.",
                func_name,
                extract_kind,
                extract_value,
            )


eiq_url = sys.argv[1]
eiq_version = sys.argv[2]
eiq_user = sys.argv[3]
eiq_password = sys.argv[4]
eiq_group_name = sys.argv[5]
record = {}
record["type_eiq"] = sys.argv[6]
record["value_eiq"] = sys.argv[7]

eiq_tip = EclecticIQ_api(
    baseurl=eiq_url, eiq_version=eiq_version, username=eiq_user, password=eiq_password
)
source_group_uid = eiq_tip.get_source_group_uid(eiq_group_name)

eiq_tip.create_sighting(source_group_uid, record)
