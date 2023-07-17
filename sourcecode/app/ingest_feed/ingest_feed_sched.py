__author__ = 'EclecticIQ'

import sys
import time
import re

import app.ingest_feed.ingest_feed_api as ingest_api

from qpylib import qpylib
from app.cipher import Cipher
from app.configs.datastore import DATA_STORE_DIR, DATA_STORE_FILE, DATA_STORE_SETUP_FILE
from app.datastore import (
    overwrite_data_store,
    overwrite_setup_data_store,
    read_data_store,
)

sleep_time = 120
time.sleep(sleep_time)
qpylib.create_log()

while True:
    try:
        config_data = read_data_store("/opt/app-root/" + DATA_STORE_DIR, DATA_STORE_FILE)
        setup_data = read_data_store("/opt/app-root/" + DATA_STORE_DIR, DATA_STORE_SETUP_FILE)

    except Exception as e:
        qpylib.log("ingest_feed_sched.__main__: Ingest feed script stopped because of exception. details: " + str(e), level='info')

    try:

        if setup_data.get('outgoing_feeds', False):

            '''
            TD. comparison of config and checkpoint 
            full_checkpoint = read_full_checkpoint()
            feed_ids = (params.get('feed_data', []).replace(" ", "")).split(',')
            for config in full_checkpoint:
            print("1")

            '''
            dict_of_params = {'eiq_url': config_data['host'],
                              'eiq_version': config_data['version'][-2:],
                              'eiq_password': Cipher('api_key', "shared").decrypt(),
                              'qradar_sec_token': Cipher('qradar_security_token', "shared").decrypt(),
                              'feed_data': None,
                              'proxy_url': None,
                              'proxy_user': None,
                              'proxy_password': None}

            feeds_list = setup_data.get('outgoing_feeds', [])
            feed_ids = ""

            for feed in feeds_list:
                feed_ids = feed_ids + feed["id"] + ","

            feed_ids = feed_ids.rstrip(',')

            sleep_time = int(setup_data.get('interval', 120))
            dict_of_params["feed_data"] = feed_ids

            qpylib.log('ingest_feed_sched.__main__: Executing scheduled feeds pull content now', level='info')
            ingest_api.ingest_feed(dict_of_params)
            qpylib.log('ingest_feed_sched.__main__: All feeds were ingested.', level='info')
        else:
            qpylib.log("ingest_feed_sched.__main__: Feeds are not configured for ingestion. Wait 120s and read config again.", level='info')

    except Exception as e:
        qpylib.log("ingest_feed_sched.__main__: Ingest feed script stopped because of exception. details: " + str(e), level='info')

    time.sleep(sleep_time)