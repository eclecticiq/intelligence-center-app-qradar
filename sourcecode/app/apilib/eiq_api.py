#!/usr/bin/env python
"""
Copyright EclecticIQ B.V.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import json
import requests
import re
import logging
import datetime
import time
import urllib3
import math
import decimal

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from qpylib import qpylib

__version__ = '1.0.0'
__license__ = 'Apache License 2.0'

API_PATHS = {
    'v1': {
        'group_id_search': '/api/v1/sources/',
        'feeds_list': '/private/outgoing-feed-download/',
        'outgoing_feeds': '/private/outgoing-feeds/',
        'feed_content_blocks': '/private/outgoing-feed-download/',
        'groups': '/private/groups/',
        'entities': '/private/entities/',
        'observable_search': '/api/v1/observables',
        'observable_search_raw': '/private/search-history/search-observable',
        'entity_search': '/api/v1/entities',
        'taxonomy_get': '/api/v1/taxonomies',
        'observables': '/private/search-all',
        'tasks': '/private/tasks/',
        'dataset': '/private/intel-sets/',
        'relationships': '/api/v1/relationships',
        'task_status': '/private/task-runs/',
        'incoming_feeds': '/private/incoming-feeds/',
        'observables_batch_delete': '/private/extracts/batch-delete/',
        'status': '/private/status',
        'enrichers': '/private/enricher-tasks/',
        'enrichers-run': '/private/enricher-tasks/batch-run'
    },
    'v2': {
        'group_id_search': '/api/v2/sources/',
        'feeds_list': '/private/outgoing-feed-download/',
        'outgoing_feeds': '/private/outgoing-feeds/',
        'feed_content_blocks': '/private/outgoing-feed-download/',
        'groups': '/private/groups/',
        'entities': '/private/entities/',
        'observable_search': '/api/v2/observables',
        'observable_search_raw': '/private/search-history/search-observable',
        'entity_search': '/api/v2/entities',
        'taxonomy_get': '/api/v2/taxonomies',
        'observables': '/private/search-all',
        'tasks': '/private/tasks/',
        'dataset': '/private/intel-sets/',
        'relationships': '/api/v2/relationships',
        'task_status': '/private/task-runs/',
        'incoming_feeds': '/private/incoming-feeds/',
        'observables_batch_delete': '/private/extracts/batch-delete/',
        'status': '/private/status',
        'enrichers': '/private/enricher-tasks/',
        'enrichers-run': '/private/enricher-tasks/batch-run'
    }
}

USER_AGENT = "script"

def extract_uuid_from_url(url):
    match = re.search('[\da-z\-]{36}', url)

    if match:
        return match.group()
    else:
        return None
    
def observable_id_from_url(url):
    match = re.search('(observables\/)([\d]+)', url)

    if match:
        return match.group(2)
    else:
        return None

def taxonomie_id_from_url(url):
    match = re.search('(taxonomies\/)([\d]+)', url)

    if match:
        return match.group(2)
    else:
        return None

def format_ts(dt):
    return dt.replace(microsecond=0).isoformat() + 'Z'


def format_ts_human(dt):
    return dt.replace(microsecond=0).isoformat() + 'Z'

class qradar_logger(object):
    def __init__(self):
        qpylib.create_log()

    def info(self, message):
        qpylib.log("eiq_api.py: " + message, level="info")

    def error(self, message):
        qpylib.log("eiq_api.py: " + message, level="error")

    def exception(self, message):
        qpylib.log("eiq_api.py: " + message, level="critical")

    def debug(self, message):
        qpylib.log("eiq_api.py: " + message, level="debug")

    def warning(self, message):
        qpylib.log("eiq_api.py: " + message, level="warning")

class EclecticIQ_api(object):
    def __init__(self,
                 baseurl,
                 eiq_api_version,
                 username,
                 password,
                 verify_ssl=True,
                 proxy_ip=None,
                 proxy_username=None,
                 proxy_password=None,
                 logger=None,
                 init_cred_test=True
                 ):
        self.eiq_logging = qradar_logger()
        self.eiq_username = username
        self.eiq_password = password
        self.baseurl = baseurl
        self.verify_ssl = self.set_verify_ssl(verify_ssl)
        self.proxy_ip = proxy_ip
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.proxies = self.set_eiq_proxy()
        self.eiq_api_version = eiq_api_version
        self.taxonomie_dict = {}
        self.headers = {
            'user-agent': USER_AGENT,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.get_outh_token(test_credentials=init_cred_test)

    def set_verify_ssl(self, ssl_status):
        if ssl_status in ["1", "True", "true", True]:
            return True
        elif ssl_status in ["0", "False", "false", False]:
            return False
        else:
            return True

    def sanitize_eiq_url(self, eiq_url):
        # TD
        return

    def set_eiq_proxy(self):
        if self.proxy_ip and self.proxy_username and self.proxy_password:
            return {
                'http': 'http://' + self.proxy_username + ':' + self.proxy_password + '@' + self.proxy_ip + '/',
                'https': 'http://' + self.proxy_username + ':' + self.proxy_password + '@' + self.proxy_ip + '/',
            }
        elif self.proxy_ip:
            return {
                'http': 'http://' + self.proxy_ip + '/',
                'https': 'http://' + self.proxy_ip + '/',
            }
        else:
            return None

    def get_outh_token(self, test_credentials = True):
        self.eiq_logging.info('Authenticating using username: ' + str(self.eiq_username))

        try:
            self.headers['Authorization'] = 'Bearer ' + self.eiq_password

            if test_credentials:
                r = requests.get(
                    self.baseurl + '/private',
                    headers=self.headers,
                    verify=self.verify_ssl,
                    proxies=self.proxies,
                    timeout=30
                )

                if r and r.status_code in [100, 200, 201, 202]:
                    self.eiq_logging.info('Authentication successful')
                else:
                    if not r:
                        msg = 'Could not perform auth request to EclecticIQ'
                        self.eiq_logging.exception(msg)
                        raise Exception(msg)
                    try:
                        err = r.json()
                        detail = err['errors'][0]['detail']
                        msg = ('EclecticIQ VA returned an error, code:[{0}], reason:[{1}], URL: [{2}], details:[{3}]'
                            .format(r.status_code, r.reason, r.url, detail))
                    except Exception:
                        msg = ('EclecticIQ VA returned an error, code:[{0}], reason:[{1}], URL: [{2}]'
                            .format(r.status_code, r.reason, r.url))
                    raise Exception(msg)
                
        except Exception:
            self.eiq_logging.error("Authentication failed")
            raise

    def send_api_request(self, method, path, params=None, data=None):
        url = self.baseurl + path

        r = None
        try:
            if method == 'post':
                r = requests.post(
                    url,
                    headers=self.headers,
                    params=params,
                    data=json.dumps(data),
                    verify=self.verify_ssl,
                    proxies=self.proxies,
                    timeout=30
                )
            elif method == 'put':
                r = requests.put(
                    url,
                    headers=self.headers,
                    params=params,
                    data=json.dumps(data),
                    verify=self.verify_ssl,
                    proxies=self.proxies,
                    timeout=30
                )
            elif method == 'get':
                r = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    data=json.dumps(data),
                    verify=self.verify_ssl,
                    proxies=self.proxies,
                    timeout=30
                )
            elif method == 'delete':
                r = requests.delete(
                    url,
                    headers=self.headers,
                    params=params,
                    data=json.dumps(data),
                    verify=self.verify_ssl,
                    proxies=self.proxies,
                    timeout=30
                )
            else:
                self.eiq_logging.error("Unknown method: " + str(method))
                raise Exception
        except Exception as e:
            self.eiq_logging.exception('Could not perform request to EclecticIQ VA: {0}: {1}. Exception: {2}'.format(method, url, e))

        if r and r.status_code in [100, 200, 201, 202, 204]:
            return r
        else:
            if r == None:
                msg = ('Could not perform request to EclecticIQ VA: {0}: {1}. Check network connectivity.'.format(method, url))
                self.eiq_logging.exception(msg)
                raise Exception(msg)
            elif r.status_code in [401]:
                msg = ('Wrong credentials. Status code:{0}'.format(r.status_code))
                self.eiq_logging.exception(msg)
                raise Exception(msg)            
            elif not r:
                msg = ('Could not perform request to EclecticIQ VA: {0}: {1}. Status code:{2}'.format(method, url, r.status_code))
                self.eiq_logging.exception(msg)
                raise Exception(msg)

            try:
                err = r.json()
                detail = err['errors'][0]['detail']
                msg = ('EclecticIQ VA returned an error, code:{0}, reason:[{1}], URL: [{2}], details:[{3}]'
                    .format(
                    r.status_code,
                    r.reason,
                    r.url,
                    detail))
            except Exception:
                msg = ('EclecticIQ VA returned an error, code:{0}, reason:[{1}], URL: [{2}]').format(
                    r.status_code,
                    r.reason,
                    r.url)
            raise Exception(msg)

    def get_source_group_uid(self, group_name):
        # get source group UID. 
        self.eiq_logging.debug("Requesting source id for specified group, name=[" + str(group_name) + "]")
        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['groups'],
            params='filter[name]=' + str(group_name))

        if not r.json()['data']:
            self.eiq_logging.error(
                'Something went wrong fetching the group id. '
                'Please note the source group name is case sensitive! '
                'Received response:' + str(r.json()))
            return "error_in_fetching_group_id"
        else:
            self.eiq_logging.debug('Source group id received')
            self.eiq_logging.debug('Source group id is: ' + str(r.json()['data'][0]['source']))
            return r.json()['data'][0]['source']

    def get_source_group_order_id(self, group_name):
        # get source group UID. 
        self.eiq_logging.debug("Requesting source id for specified group, name=[" + str(group_name) + "]")
        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['groups'],
            params='filter[name]=' + str(group_name))

        return r.json()['data'][0]['id']

    def get_enrichers_list(self):
        # get enrichers list
        self.eiq_logging.debug("Requesting availble Enrichers list from platform.")
        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['enrichers'])

        return r.json()['data']

    def get_active_enrichers_list(self):
        enrichers_list = []
        enrichers_list = self.get_enrichers_list()
        active_list = []

        for enricher in enrichers_list:
            if enricher["is_active"]:
                active_list.append(enricher)

        return active_list

    def enrich_observable(self, enricher_id, observable_id):
        # To enrich Observable
        self.eiq_logging.debug("Enriching observable.{0}".format(observable_id))
        run_dict = {
            "data":
                {
                    "enricher_tasks": [enricher_id],
                    "extracts": [observable_id]
                 }
        }

        r = self.send_api_request(
            'post',
            path=API_PATHS[self.eiq_api_version]['enrichers-run'],
            data=run_dict)

        return r.json()['data']

    def get_status(self):
        # get platform status
        self.eiq_logging.info("Requesting Platform status")

        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['status'])

        return r.json()['data']

    def get_status_red_component(self):
        status = self.get_status()

        result = {"health": status["health"], "components": []}

        for celery_component in status["celery_states"]:
            if celery_component["health"] == "RED":
                result["components"].append(celery_component)

        for service_component in status["service_states"]:
            if service_component["health"] == "RED":
                result["components"].append(service_component)

        return result

    def create_incoming_feed(self, feed_title, content_type, password, username, collection_name="null", polling_service_url="null",
                             taxii_version="null", transport_type="null", basic_auth="false"):
        self.eiq_logging.info("Creating Incoming Feed {0}".format(feed_title))
        # To create Incoming feed

        # TD "null" doesnt work, if lines are not commented it leads to 500 error
        create_feed_dict = {
            "data": {
#                "archive_password": "null",
                "content_type": content_type,
#                "execution_schedule": "null",
                "half_life": {},
                "is_public": "false",
                "name": feed_title,
#                "organisation": "null",
                "require_link_types": "false",
                "require_valid_signature": "false",
#                "source_reliability": "null",
#                "tlp_color_override": "null",
                "transport_configuration": {
                    "basic_authentication_mode": basic_auth,
                    "password": password,
                    "username": username,
                    "collection_name": collection_name,
                    "polling_service_url": polling_service_url,
                    "ssl_authentication_mode": "false",
                    "taxii_version": taxii_version,
                    "verify_ssl": "false"
                },
                "transport_type": transport_type
            }
        }

        r = self.send_api_request(
            'post',
            path=API_PATHS[self.eiq_api_version]['incoming_feeds'],
            data=create_feed_dict)

        result = (json.loads(r.text))['data']

        return result

    def download_incoming_feed(self, feed_id, feed_provider_task):
        # To download incmoing feed
        self.eiq_logging.info("Downloading Incoming Feed {0}".format(feed_id))

        run_task_download_feed = {
            "data": {
                "id": feed_provider_task,
                "is_active": True,
                # "parameters": {
                #     "basic_authentication_mode": False,
                #     "collection_name": "multi-binding-fixed",
                #     "polling_service_url": "https://test.taxiistand.com/read-only/services/poll",
                #     "ssl_authentication_mode": False,
                #     "taxii_version": "1.1",
                #     "verify_ssl": False
                # },
                #"task_name": "eiq.incoming-transports.taxii",
                "task_type": "provider_task",
                "trigger": "null"
            }
        }

        r = self.send_api_request(
            'post',
            path=API_PATHS[self.eiq_api_version]['tasks'] + str(feed_provider_task) + "/run",
            data=run_task_download_feed)

        result = (json.loads(r.text))['data']
        return result

    def delete_outgoing_feed(self, feed_id):
        # To delete Outgoing feed
        self.eiq_logging.info("Delete Outgoing Feed {0}".format(feed_id))

        r = self.send_api_request(
            'delete',
            path=API_PATHS[self.eiq_api_version]['outgoing_feeds'] + str(feed_id))

        result = "Outgoing Feed deleted"
        return result

    def delete_incoming_feed(self, feed_id):
        # To delete Incoming feed
        self.eiq_logging.info("Delete Incoming Feed {0}".format(feed_id))

        r = self.send_api_request(
            'delete',
            params="with_linked_data=true",
            path=API_PATHS[self.eiq_api_version]['incoming_feeds'] + str(feed_id))

        result = "Incoming Feed deleted"
        return result

    def delete_data_set(self, data_set_id):
        # To delete dataset
        self.eiq_logging.info("Delete Dataset {0}".format(data_set_id))

        r = self.send_api_request(
            'delete',
            path=API_PATHS[self.eiq_api_version]['dataset'] + str(data_set_id))

        result = "Dataset deleted"
        return result

    def create_dataset(self, title, search_query):
        # To create Dataset

        self.eiq_logging.info("Creating Dataset {0}".format(title))

        create_dataset = {
            "data": {
                "is_dynamic": True,
                "name": title,
                "search_query": search_query,
                "workspaces": [
                    1
                ]
            }
        }

        r = self.send_api_request(
            'post',
            path=API_PATHS[self.eiq_api_version]['dataset'],
            data=create_dataset)

        result = (json.loads(r.text))['data']

        return result

    def create_outgoing_feed(self, content_type, intel_set_id, feed_title, transport_type, update_strategy, access_group_name):
        # create Outgoing feed

        self.eiq_logging.info("Creating Outgoing Feed {0}".format(feed_title))

        authorized_group_order_id = str(self.get_source_group_order_id(access_group_name))

        create_outgoing_feed = {
            "data": {
                "allowed_extract_states": [
                    {
                        "classification": "bad",
                        "confidence": "high"
                    },
                    {
                        "classification": "bad",
                        "confidence": "medium"
                    },
                    {
                        "classification": "bad",
                        "confidence": "low"
                    },
                    {
                        "classification": "good"
                    },
                    {
                        "classification": "unknown"
                    }
                ],
                "allowed_link_types": [
                    "parameter",
                    "affected",
                    "configuration",
                    "vulnerability",
                    "weakness",
                    "affected-asset",
                    "related",
                    "observed",
                    "sighted",
                    "test-mechanism",
                    "identity",
                    "malicious-infrastructure",
                    "targeted-victim"
                ],
                "anonymize_replace_actions": [],
                "anonymize_skip_paths": [],
                "content_configuration": {
                    "producer_override_enabled": False
                },
                "content_type": content_type,
                "deselected_enrichers": [],
                "do_sign_content": False,
                "enrichment_extract_types": [
                    "company",
                    "geo-lat",
                    "registrar",
                    "city",
                    "forum-name",
                    "file",
                    "netname",
                    "street",
                    "host",
                    "person",
                    "uri-hash-sha256",
                    "product",
                    "postcode",
                    "domain",
                    "cce",
                    "name",
                    "card",
                    "actor-id",
                    "winregistry",
                    "geo",
                    "fox-it-portal-uri",
                    "mac-48",
                    "email",
                    "inetnum",
                    "eui-64",
                    "forum-thread",
                    "address",
                    "card-owner",
                    "email-subject",
                    "uri",
                    "country-code",
                    "ipv6",
                    "telephone",
                    "rule",
                    "nationality",
                    "forum-room",
                    "mutex",
                    "asn",
                    "hash-md5",
                    "ipv4",
                    "organization",
                    "country",
                    "bank-account",
                    "snort",
                    "handle",
                    "hash-sha256",
                    "industry",
                    "port",
                    "cve",
                    "geo-long",
                    "hash-sha1",
                    "yara",
                    "malware",
                    "hash-sha512",
                    "cwe",
                    "process"
                ],
                # "execution_schedule": "null",
                "extract_types": [
                    "actor-id",
                    "address",
                    "asn",
                    "bank-account",
                    "card",
                    "card-owner",
                    "cce",
                    "city",
                    "company",
                    "country",
                    "country-code",
                    "cve",
                    "cwe",
                    "domain",
                    "email",
                    "email-subject",
                    "eui-64",
                    "file",
                    "forum-name",
                    "forum-room",
                    "forum-thread",
                    "fox-it-portal-uri",
                    "geo",
                    "geo-lat",
                    "geo-long",
                    "handle",
                    "hash-md5",
                    "hash-sha1",
                    "hash-sha256",
                    "hash-sha512",
                    "host",
                    "industry",
                    "inetnum",
                    "ipv4",
                    "ipv6",
                    "mac-48",
                    "malware",
                    "mutex",
                    "name",
                    "nationality",
                    "netname",
                    "organization",
                    "person",
                    "port",
                    "postcode",
                    "process",
                    "product",
                    "registrar",
                    "rule",
                    "snort",
                    "street",
                    "telephone",
                    "uri",
                    "uri-hash-sha256",
                    "winregistry",
                    "yara"
                ],
                # "half_life_filter": "null",
                "include_without_link_type": True,
                "intel_sets": [
                    str(intel_set_id)
                ],
                "is_active": False,
                "name": feed_title,
                "require_valid_data": False,
                # "source_reliability_filter": "null",
                # "tlp_color_filter": "null",
                # "tlp_color_override": "null",
                "transport_configuration": {
                    "authorized_groups": [
                        authorized_group_order_id
                    ],
                    "is_public": False
                },
                "transport_type": transport_type,
                "update_strategy": update_strategy,
                "whitelist_sources": [],
                "whitelist_tags": [],
                "whitelist_taxonomy_nodes": []
            }
        }

        r = self.send_api_request(
            'post',
            path=API_PATHS[self.eiq_api_version]['outgoing_feeds'],
            data=create_outgoing_feed)

        result = (json.loads(r.text))['data']

        return result

    def enable_outgoing_feed(self, outgoing_feed_full_info):
        # enable outgoing feed

        self.eiq_logging.info("Enable Outgoing Feed id={0}".format(outgoing_feed_full_info["id"]))

        enable_outgoing_feed_payload = {
            "data": outgoing_feed_full_info
        }

        enable_outgoing_feed_payload["data"]["is_active"] = True

        r = self.send_api_request(
            'put',
            path=API_PATHS[self.eiq_api_version]['outgoing_feeds'] + str(outgoing_feed_full_info["id"]),
            data=enable_outgoing_feed_payload)

        result = (json.loads(r.text))['data']

        return result

    def run_outgoing_feed(self, feed_id):
        # run outgoing feed

        self.eiq_logging.info("Run Outgoing Feed {0}".format(feed_id))

        outgoing_feed_full_info = self.get_full_feed_info(feed_id=feed_id)

        self.enable_outgoing_feed(outgoing_feed_full_info)

        # couldn find way to detect that feed is fully created and enabled, without wait feed doesnt run oftenly
        #time.sleep(0.5)

        run_task_outgoing_feed = {
            "data": {
                "id": outgoing_feed_full_info["update_task"],
                "is_active": True,
                # "parameters": {
                #     "basic_authentication_mode": False,
                #     "collection_name": "multi-binding-fixed",
                #     "polling_service_url": "https://test.taxiistand.com/read-only/services/poll",
                #     "ssl_authentication_mode": False,
                #     "taxii_version": "1.1",
                #     "verify_ssl": False
                # },
                "task_name": "eiq.outgoing-feeds.feed_update",
                "task_type": "utility_task",
                "trigger": "null"
            }
        }

        r = self.send_api_request(
            'post',
            path=API_PATHS[self.eiq_api_version]['tasks'] + str(outgoing_feed_full_info["update_task"]) + "/run",
            data=run_task_outgoing_feed)

        result = (json.loads(r.text))['data']
        return result

    def get_task_status(self, task_id):
        # get task status

        self.eiq_logging.info("Requesting status of task: {0}".format(task_id))

        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['task_status'] + task_id)

        result = (json.loads(r.text))['data']

        return result

    def get_incoming_feed_blobs_pending(self, feed_id):
        # to get incmoing feed blobs 
        self.eiq_logging.info("Requesting Incoming feed run status: {0}".format(feed_id))

        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['incoming_feeds'])

        result = None

        for feed in (json.loads(r.text))['data']:
            if feed["id"] == feed_id:
                result = feed["n_blobs_pending"]

        return result

    def get_full_feed_info(self, feed_id):
        # to get outgoing feed full info

        self.eiq_logging.info("Requesting full feed info for feed id={0}".format(feed_id))

        if feed_id == "*": feed_id = ""

        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['outgoing_feeds'] + str(feed_id))

        result = (json.loads(r.text))['data']

        return result

    def get_incoming_feed_full_info(self, feed_id):
        # to get incmoing feed full info

        self.eiq_logging.info("Requesting full feed info for incoming feed id={0}".format(feed_id))

        if feed_id == "*": feed_id = ""

        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['incoming_feeds'] + str(feed_id))

        result = (json.loads(r.text))['data']

        return result

    def get_feed_info(self, feed_ids):
        self.eiq_logging.info("Requesting feed info for feed id={0}".format(feed_ids))
        feed_ids = (feed_ids.replace(" ", "")).split(',')
        result = []

        if self.eiq_api_version == "FC":
            for k in feed_ids:
                feed_result = {'id': k, 'created_at': '', 'update_strategy': 'REPLACE', 'packaging_status': 'SUCCESS'}
                result.append(feed_result)
            self.feeds_info = result
            return result

        for k in feed_ids:
            feed_result = {}
            try:
                r = self.send_api_request(
                    'get',
                    path=API_PATHS[self.eiq_api_version]['outgoing_feeds'] + k)
            except Exception:
                self.eiq_logging.error('Feed id={0} information cannot be requested.'.format(k))
                continue

            if not r.json()['data']:
                self.eiq_logging.error(
                    'Feed id={0} information cannot be requested. Received response:' + str(r.json())).format(k)
                return "error_in_fetching_feed_info"
            else:
                self.eiq_logging.debug('Feed id={0} information requested'.format(k))
                feed_result['id'] = r.json()['data']['id']
                feed_result['created_at'] = r.json()['data']['created_at']
                feed_result['update_strategy'] = r.json()['data']['update_strategy']
                feed_result['packaging_status'] = r.json()['data']['packaging_status']
                feed_result['name'] = r.json()['data']['name']
                result.append(feed_result)
                self.eiq_logging.debug(
                    'Feed id={0} information retrieved successfully. Received response:'.format(k) + str(
                        json.dumps(feed_result)) + ''.format(k))

        return result

    def download_block_list(self, block):
        self.eiq_logging.debug("Downloading block url{0}".format(block))

        if self.eiq_api_version == "FC":
            block = (str(block)).replace(self.baseurl, '')

        r = self.send_api_request('get', path=str(block))
        data = r.text

        return data

    def get_feed_content_blocks(self, feed, feed_last_run=None):
        self.eiq_logging.debug("Requesting block list for feed id={0}".format(feed['id']))

        if feed_last_run is None:
            feed_last_run = {}
            feed_last_run['last_ingested'] = None
            feed_last_run['created_at'] = None

        if feed['packaging_status'] == 'SUCCESS' and feed['update_strategy'] == 'REPLACE':
            self.eiq_logging.debug("Requesting block list for REPLACE feed.")

            r = self.send_api_request(
                'get',
                path=API_PATHS[self.eiq_api_version]['feed_content_blocks'] + "{0}/runs/latest".format(feed['id']))

            data = r.json()['data']['content_blocks']
            if feed_last_run['last_ingested'] == data[-1]:
                self.eiq_logging.info(
                    "Received list contains {0} blocks for feed id={1}.".format(len(data), feed['id']))
                return []
            self.eiq_logging.info("Received list contains {0} blocks for feed id={1}.".format(len(data), feed['id']))
            return data

        elif feed['packaging_status'] == 'SUCCESS' and (feed['update_strategy'] in ['APPEND', 'DIFF']):
            self.eiq_logging.debug("Requesting block list for {0} feed.".format(feed['update_strategy']))

            r = self.send_api_request(
                'get',
                path=API_PATHS[self.eiq_api_version]['feed_content_blocks'] + "{0}".format(feed['id']) + "/")

            data = r.json()['data']['content_blocks']

            if (feed['created_at'] != feed_last_run['created_at']) or feed_last_run['last_ingested'] is None:
                self.eiq_logging.info(
                    "Received list contains {0} blocks for {1} feed:{2}. Feed created time changed or first run, "
                    "reingestion of all the feed content.".format(len(data), feed['update_strategy'], feed['id']))
                return data
            else:
                try:
                    last_ingested_index = data.index(feed_last_run['last_ingested'])
                    diff_data = data[last_ingested_index + 1:]
                    self.eiq_logging.info("Received list contains {0} blocks for {1} feed:{2}."
                                          .format(len(diff_data), feed['update_strategy'], feed['id']))
                    return diff_data
                except ValueError:
                    self.eiq_logging.error("Value of last ingested block not available in Feed {0}.".format(feed['id']))
                    return None

        elif feed['packaging_status'] == 'RUNNING':
            self.eiq_logging.info("Feed id={0} is running now. Collecting data is not possible.".format(feed['id']))
        else:
            self.eiq_logging.info(
                "Feed id={0} update strategy is not supported. Use Replace or Diff".format(feed['id']))

    def get_group_name(self, group_id):
        self.eiq_logging.info("Getting group name by id:{0}".format(group_id))
        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['group_id_search'] + str(group_id))

        response = json.loads(r.text)
        result = {}

        result['name'] = response['data'].get('name', 'N/A')
        result['type'] = response['data'].get('source_type', 'N/A')

        return result

    def get_observable_by_id(self, id):
        self.eiq_logging.info("Searching Observable with ID:{0}".format(id))

        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['observable_search'] + "/" + str(id))

        observable_response = json.loads(r.text)

        return observable_response

    def lookup_observable(self, value, type=None):
        """Method lookups specific observable by value and type.

        Args:
            value: value of Observable
            type: type of observable, e.g. ipv4, hash-md5 etc

        Returns:
            Return dictionary with Observable details:
             {created: date and time of creation,
             last_updated: last update time,
             maliciousness: value of maliciousness,
             type: type of Observable from args ,
             value: value of Observable from args,
             source_name: who produced Observable,
             platform_link: direct link o the platform
             }

            Otherwise returns None.

        """
        self.eiq_logging.info("Searching Observable:{0}, type:{1}".format(value, type))

        params = {}
        params['filter[value]'] = value
        
        if type is not None:
            params['filter[type]'] = type

        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['observable_search'],
            params=params)

        observable_response = json.loads(r.text)

        if observable_response['count'] == 1:
            result = {}
            result['created'] = str(observable_response['data'][0]['created_at'])[:16]
            result['last_updated'] = str(observable_response['data'][0]['last_updated_at'])[:16]
            result['maliciousness'] = observable_response['data'][0]['meta']['maliciousness']
            result['type'] = observable_response['data'][0]['type']
            result['value'] = observable_response['data'][0]['value']
            result['id'] = str(observable_response['data'][0]['id'])
            result['source_name'] = ""

            for k in observable_response['data'][0]['sources']:
                source_lookup_data = self.get_group_name(extract_uuid_from_url(k))
                result['source_name'] += str(source_lookup_data['type']) + ': ' + str(source_lookup_data['name']) + '; '

            result['platform_link'] = self.baseurl + "/main/intel/all/browse/observable?tab=overview&id=" + result['id']

            return result

        elif observable_response['count'] > 1:
            self.eiq_logging.info("Finding duplicates for observable:{0}, type:{1}, return first one".format(value, type))
            result = {}
            result['created'] = str(observable_response['data'][0]['created_at'])[:16]
            result['last_updated'] = str(observable_response['data'][0]['last_updated_at'])[:16]
            result['maliciousness'] = observable_response['data'][0]['meta']['maliciousness']
            result['type'] = observable_response['data'][0]['type']
            result['value'] = observable_response['data'][0]['value']
            result['id'] = str(observable_response['data'][0]['id'])
            result['source_name'] = ""

            for k in observable_response['data'][0]['sources']:
                source_lookup_data = self.get_group_name(extract_uuid_from_url(k))
                result['source_name'] += str(source_lookup_data['type']) + ': ' + str(source_lookup_data['name']) + '; '

            result['platform_link'] = self.baseurl + "/main/intel/all/browse/observable?tab=overview&id=" + result['id']

            return result

        else:

            return None

    def get_all_observables(self):
        self.eiq_logging.info("Searching all Observable.")

        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['observable_search'])

        return json.loads(r.text)

    def batch_delete_observables(self, observables_list):
        self.eiq_logging.info("Searching all Observable.")

        observables_to_delete = {
            "data": {
                "observables": observables_list
            }
        }

        r = self.send_api_request(
            'delete',
            path=API_PATHS[self.eiq_api_version]['observables_batch_delete'],
            data=observables_to_delete)

        return json.loads(r.text)

    def delete_entity(self, entity_id):
        self.eiq_logging.info("Deleteing entity. id: {0}".format(entity_id))

        r = self.send_api_request(
            'delete',
            path=API_PATHS[self.eiq_api_version]['entities'] + str(entity_id))

        return "deleted"


    def get_taxonomy_dict(self):
        """Method returns dictionary with all the available taxonomy in Platform.

        Returns:
            Return dictionary with {taxonomy ids:taxonomy title}. Otherwise returns False.

        """
        self.eiq_logging.info("Get all the taxonomy titles from Platform.")

        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['taxonomy_get'],
            params={"limit":500})

        taxonomy = json.loads(r.text)
        taxonomy_dict = {}

        for i in taxonomy['data']:
            try:
                id = str(i['id'])
                name = i['name']

                taxonomy_dict[id] = name
            except KeyError:
                continue

        if len(taxonomy_dict) > 0:
            return taxonomy_dict
        else:
            return False
        
    def get_entity_realtionships(self, source_id = None, target_id = None):
        self.eiq_logging.info("Get realtionshsip for entity. Source id: {0}, Destination id: {1}".format(source_id, target_id))
        params = {}

        if source_id:
            params["filter[data.source]"] = source_id
            direction = "source"
        elif target_id:
            params["filter[data.target]"] = target_id
            direction = "target"

        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['relationships'],
            params=params)
        
        parsed_response = json.loads(r.text)
        result = []

        if len(parsed_response['data']) > 0:
            for i in parsed_response['data']:
                relation = {}
                if direction == "source":                    
                    r = self.send_api_request(
                        'get',
                        path=API_PATHS[self.eiq_api_version]['entity_search'] + "/" + str(extract_uuid_from_url(i["data"]["target"])))
                elif direction == "target":
                    r = self.send_api_request(
                        'get',
                        path=API_PATHS[self.eiq_api_version]['entity_search'] + "/" + str(extract_uuid_from_url(i["data"]["source"])))
                    
                related_entity_parsed_response = json.loads(r.text)
                    
                if self.eiq_api_version == "v1":
                    relation["relation_title"] = i["meta"]["title"]
                    relation["entity_type"] = related_entity_parsed_response["data"]["type"]
                elif self.eiq_api_version == "v2":
                    relation["relation_title"] = i["data"]["key"]
                    relation["entity_type"] = related_entity_parsed_response["data"]["data"]["type"]
                                
                relation["entity_title"] = related_entity_parsed_response["data"]["data"]["title"]                
                relation["entity_id"] = related_entity_parsed_response["data"]["id"]
                relation["observables_count"] = len(related_entity_parsed_response["data"]["observables"])
                result.append(relation)
        return result


    def get_entity_by_id(self, entity_id, observables_lookup = True, relationships_lookup = True):
        """Method lookups specific entity by Id.

        Args:
            entity_id: Requested entity Id.

        Returns:
            Return dictionary with entity details:
             {entity_title: value,
             entity_type: value,
             created_at: value,
             source_name: value,
             tags_list: [
                tag and taxonomy list ...
                ],
             relationships_list: [
                    {relationship_type: incoming/outgoing,
                    connected_node: id,
                    connected_node_type: value,
                    connected_node_type: value
                    }
                relationship list ...
                ],
             observables_list: [
                    {value: obs_value,
                    type: obs_type
                    },
                    ...
                ]
             }

            Otherwise returns False.

        """
        self.eiq_logging.info("Looking up Entity {0}.".format(entity_id))
        
        try:
            r = self.send_api_request(
                'get',
                path=API_PATHS[self.eiq_api_version]['entity_search'] + "/" + str(entity_id))
            parsed_response = json.loads(r.text)

            if len(self.taxonomie_dict) == 0:
                self.taxonomie_dict = self.get_taxonomy_dict()

            result = dict()

            result['entity_title'] = parsed_response['data']['data'].get('title', 'N/A')
            result['created_at'] = str(parsed_response['data'].get('created_at', 'N/A'))[:16]
            source = self.get_group_name(extract_uuid_from_url(parsed_response['data']['sources'][0]))
            result['source_name'] = source['type'] + ': ' + source['name']
            result['tags_list'] = []
            result['confidence'] = parsed_response['data']['data'].get('confidence', 'N/A')
            result['description'] = parsed_response['data']['data'].get('description', 'N/A')
            result['impact'] = parsed_response['data']['data'].get('impact', 'N/A')

            if self.eiq_api_version == "v1":
                result['entity_type'] = parsed_response['data'].get('type', 'N/A')
            elif self.eiq_api_version == "v2":
                result['entity_type'] = parsed_response['data']['data'].get('type', 'N/A')            

            try:
                for i in parsed_response['data']['meta']['tags']:
                    result['tags_list'].append(i)
            except KeyError:
                pass

            try:
                for i in parsed_response['data']['meta']['taxonomies']:
                    result['tags_list'].append(self.taxonomie_dict.get(taxonomie_id_from_url(i)))
            except KeyError:
                pass

            if observables_lookup:
                result['observables_list'] = []
                try:
                    for i in parsed_response['data']["observables"]:
                        observable_data = self.get_observable_by_id(observable_id_from_url(i))
                        result['observables_list'].append({'value': observable_data['data']['value'], 
                                                        'type': observable_data['data']['type'],
                                                        'maliciousness': observable_data['data']['meta']['maliciousness']})                
                except (KeyError, TypeError):
                    pass

            if relationships_lookup:
                entity_is_source_relationships = self.get_entity_realtionships(source_id=entity_id)
                entity_is_target_relationships = self.get_entity_realtionships(target_id=entity_id)
                result['relationships_list'] = []

                for i in entity_is_source_relationships:
                    result['relationships_list'].append({"source_entity_title":result['entity_title'],
                                                         "source_entity_type":result['entity_type'],
                                                         "target_entity_title":i['entity_title'],
                                                         "target_entity_type":i['entity_type'],
                                                         "target_entity_id":i['entity_id'],
                                                         "target_entity_observables_count":i['observables_count'],
                                                         "relationship_title":i['relation_title']})
                
                for i in entity_is_target_relationships:
                    result['relationships_list'].append({"source_entity_title":i['entity_title'],
                                                         "source_entity_type":i['entity_type'],
                                                         "target_entity_title":result['entity_title'],
                                                         "target_entity_type":result['entity_type'],
                                                         "source_entity_id":i['entity_id'],
                                                         "source_entity_observables_count":i['observables_count'],
                                                         "relationship_title":i['relation_title']})                

        except Exception as e:
            if "Status code: 404" in str(e):
                return False
            else:
                return e

        return result

    def search_entity(self, entity_value=None, entity_type=None, observable_value=None):
        """Method search specific entity by specific search conditions.

        Note: search works with wildcards for entity value and with strict conditions for everything else.
            Also, it's recommended to use this method to lookup entity name based on the entity ID, because it doesnt
            return all the relationships.

            if you need to find specific entity - search by entity id
            if you need to find all the entities with specific observables extracted - search with observable values

        Args:
            entity_value: entity value to search. add " or * to make search wildcard or strict
            entity_type: value to search
            entity_id: entity id to search
            observable_value: observable value to search inside entity

        Returns:
            Return dictionary with all the entity details.
            Otherwise returns False.

        """
        self.eiq_logging.info("Searching Entity:{0} with extracted observable:{1}, type:{2}"
                              .format(entity_value, observable_value, entity_type))

        params = {}

        if entity_value is not None:
            if entity_value[0] == '"' and entity_value[-1] == '"':
                entity_value = entity_value[1:-1]
                entity_value = entity_value.replace('"', '\\"')
                entity_value = '"' + entity_value + '"'
            else:
                entity_value = entity_value.replace('"', '\\"')

            params['filter[data.title]'] = entity_value

        if observable_value is not None:
            observable_data = self.lookup_observable(value=observable_value)
            try:
                params['filter[observables]'] = observable_data["id"]
            except:
                return False

        if entity_type is not None:
            params['filter[type]'] = entity_type

        r = self.send_api_request(
            'get',
            path=API_PATHS[self.eiq_api_version]['entity_search'],
            params=params)

        search_response = json.loads(r.text)

        if len(search_response['data']) > 0:
            parsed_result = []
            for entity in search_response['data']:
                parsed_entity = self.get_entity_by_id(entity["id"])
                parsed_result.append(parsed_entity)

            return parsed_result
        else:
            return False

    def elastic_search(self, search_payload=None, latency_check=False, page_size=10):
        self.eiq_logging.info("Searching in elastic")

        r = self.send_api_request(
            'post',
            path=API_PATHS[self.eiq_api_version]['entity_search'] + "?size=" + str(page_size),
            data=search_payload)

        search_response = json.loads(r.text)

        if len(search_response['hits']['hits']) > 0:
            if latency_check:
                search_response["latency"] = r.elapsed.total_seconds()
                return search_response

            else:
                return search_response['hits']['hits']
        else:
            return False

    def create_entity(self, observable_dict, source_group_name, entity_title, entity_description,
                      entity_confidence='Medium', entity_tags=[], entity_type='eclecticiq-sighting',
                      entity_impact_value="None"):

        """Method creates entity in Platform.

        Args:
            observable_dict: list of dictionaries with observables to create. Format:
                [{
                observable_type: "value",
                observable_value: value,
                observable_maliciousness: high/medium/low,
                observable_classification: good/bad
                }]
            source_group_name: group name in Platform for Source. Case sensitive.
            entity_title: value
            entity_description: value
            entity_confidence: Low/Medium/High
            entity_tags: list of strings
            entity_type: type of entity. e.g. indicator, ttp, eclecticiq-sighting etc
            entity_impact_value: "None", "Unknown", "Low", "Medium", "High"

        Returns:
            Return created entity id if successful otherwise returns False.

        """
        self.eiq_logging.info("Creating Entity in EclecticIQ Platform. Type:{0}, title:{1}"
                              .format(entity_type, entity_title))

        group_id = self.get_source_group_uid(source_group_name)

        today = datetime.datetime.utcnow().date()

        today_begin = format_ts(datetime.datetime(today.year, today.month, today.day, 0, 0, 0))
        threat_start = format_ts(datetime.datetime.utcnow())

        observable_dict_to_add = []
        record = {}

        for i in observable_dict:
            record = {}

            if entity_type == 'eclecticiq-sighting':
                record['link_type'] = "sighted"
            else:
                record['link_type'] = "observed"

            if i.get('observable_maliciousness', "") in ["low", "medium", "high"]:
                record['confidence'] = i['observable_maliciousness']

            if i.get('observable_classification', "") in ["bad", "good", "unknown"]:
                record['classification'] = i['observable_classification']

            if i.get('observable_value', ""):
                record['value'] = i['observable_value']
            else:
                continue

            if i.get('observable_type', "") in ["asn", "country", "cve", "domain", "email", "email-subject", "file",
                                                "handle",
                                                "hash-md5", "hash-sha1", "hash-sha256", "hash-sha512", "industry",
                                                "ipv4",
                                                "ipv6", "malware", "name", "organization", "port", "snort", "uri",
                                                "yara"]:
                record['kind'] = i['observable_type']
            else:
                continue

            observable_dict_to_add.append(record)


        entity = {"data": {
            "data": {
                "confidence": {
                    "type": "confidence",
                    "value": entity_confidence
                },
                "description": entity_description,
                "description_structuring_format": "html",
                "impact": {
                    "type": "statement",
                    "value": entity_impact_value,
                    "value_vocab": "{http://stix.mitre.org/default_vocabularies-1}HighMediumLowVocab-1.0",
                },
                "type": entity_type,
                "title": entity_title,
                "security_control": {
                    "type": "information-source",
                    "time": {
                        "type": "time",
                        "start_time": today_begin,
                        "start_time_precision": "second"
                    }
                },
            },
            "meta": {
                "manual_extracts": observable_dict_to_add,
                "taxonomy": [],
                "estimated_threat_start_time": threat_start,
                "tags": entity_tags,
                "ingest_time": threat_start
            },
            "sources": [{
                "source_id": group_id
            }]
        }}


        r = self.send_api_request(
            'post',
            path=API_PATHS[self.eiq_api_version]['entities'],
            data=entity)

        entity_response = json.loads(r.text)

        try:
            return entity_response['data']['id']
        except KeyError:
            return False

    def get_observable(self, observable):
        self.eiq_logging.info('EclecticIQ_api: Searching for Observable: {0}'.format(observable))
        path = API_PATHS[self.eiq_api_version]['observables'] + '?q=extracts.value:' + observable
        r = self.send_api_request(
            'get',
            path=path)
        return r.json()

