__author__ = 'EclecticIQ'

import io
import csv
import sys
import re
#import importlib
#import web_pdb

from qpylib import qpylib

from app.apilib.ibm_api import QRadar_api
from app.apilib.eiq_api import EclecticIQ_api as EIQ_api
from app.apilib.ibm_api import logs
from app.checkpoint_store import *

#importlib.reload(sys)
#sys.setdefaultencoding('utf8')

EXPORT_FIELDS_LIST = [
    'value', 'type', 'entity.type', 'entity.title', 'meta.relevancy', 'meta.tags', 'meta.taxonomy', 'meta.classification', 'meta.confidence'
]

QRADAR_RT_LIST = ["url", "email", "ip", "file_hash", "domain"]

def ingest_feed(params):
    func_name = sys._getframe().f_code.co_name
    tip = EIQ_api(baseurl = params["eiq_url"],
                  eiq_api_version = params["eiq_version"],
                  username = "",
                  password = params["eiq_password"]
                  )

    qradar = QRadar_api(token = params["qradar_sec_token"])

    feeds_info = tip.get_feed_info(params["feed_data"])

    for item in feeds_info:
        reset = False
        state = read_checkpoint(item["id"])

        if not state['created_at'] or item['created_at'] != state['created_at']:
            # check created_at field between platform and IBM
            # if they are different
            # delete all from this feed and ingest again
            write_checkpoint(item["id"], {'created_at': item["created_at"], "feed_name": item["name"], "update_strategy": item["update_strategy"], "last_ingested": None})
            reset = True

        if item['update_strategy'] == "REPLACE":
            reset = True

        if reset is True:
            state = read_checkpoint(item["id"])
            write_checkpoint(item["id"], state)
            blocks = tip.get_feed_content_blocks(item, state)
        else:
            state = read_checkpoint(item["id"])
            blocks = tip.get_feed_content_blocks(item, state)

        qpylib.log('ingest_feed_api.{0}: Checking for availability of necessary RT in Qradar.'.format(func_name), level='info')

        for k in QRADAR_RT_LIST:
            rt_title = "eiq_" + str(item["id"]) + "_" + item["name"] + "_" + k

            if not qradar.get_reference_table(rt_title):
                qradar.set_reference_table(rt_title)

        # Loop through all received blocks
        # download data from link
        # export it to IBM
        # update last_ingested field in meta conf
        qpylib.log('ingest_feed_api.{0}: Starting Ingestion of feed #{1}'.format(func_name, str(item['id'])), level='info')

        flag = reset

        for block in blocks:
            qpylib.log('ingest_feed_api.{0}: Feed id={1} preparing data to ingest block {2}.'.format(func_name, str(item['id']), block),level='info')
            data_from_block = tip.download_block_list(block)
            export_csv_to_rs(str(item['id']), data_from_block, qradar, flag)
            flag = False
            state = read_checkpoint(item["id"])
            state["last_ingested"] = block
            write_checkpoint(item["id"], state)

        qpylib.log('ingest_feed_api.{0}: Feed id={1} was fully ingested/updated.'.format(func_name, str(item['id'])),
                   level='info')

def export_csv_to_rs(feed_id, text, qrdar_obj, flag=False):

    func_name = sys._getframe().f_code.co_name
    qpylib.log('ingest_feed_api.{0}: Exporting to RT feed #{1}'.format(func_name, feed_id), level='info')
    text = io.StringIO(text)
    csvreader = csv.DictReader(text, delimiter=',')

    data_to_add = {'domain': {},
                   'ip': {},
                   'file_hash': {},
                   'email': {},
                   'url': {}}

    data_to_del = []
    state = read_checkpoint(feed_id)

    if flag:
        # this is the first block so delete everything there
        # already is in the RS before we proceed
        for k in QRADAR_RT_LIST:
            rt_title = "eiq_" + str(feed_id) + "_" + state["feed_name"] + "_" + k
            qpylib.log('ingest_feed_api.{0}: Purging content of RT {1}.'.format(func_name, rt_title), level='info')
            qrdar_obj.purge_reference_table(rt_title)

    if 'diff' not in csvreader.fieldnames:
        qpylib.log("ingest_feed_api.{0}: Update method is 'replace' so check for changes and update .".format(func_name), level='info')
        # If there is no "diff" column in the CSV
        # So the update method is set to "replace", this means we
        # delete everything from this feed and then recreate it.
        for row in csvreader:
            if row['type'] in ["email", "domain"]:
                subname = row['type']
            elif row['type'] == "uri":
                subname = "url"
            elif row['type'] == "ipv4":
                subname = "ip"
            elif row['type'] in ["hash-md5", "hash-sha1", "hash-sha256", "hash-sha512"]:
                subname = "file_hash"
            else:
                continue

            data_to_add[subname][row['value']] = {'feed_id': str(feed_id)}

            for field_name in EXPORT_FIELDS_LIST:
                if re.match(r'\w+\.', field_name):
                    new_name = re.sub(r"\w+\.", "", field_name) + "_eiq"
                    data_to_add[subname][row['value']][new_name] = row[field_name]
                elif field_name == 'type':
                    new_name = "value_" + field_name
                    data_to_add[subname][row['value']][new_name] = row[field_name]  

        for k in QRADAR_RT_LIST:
            rt_title = "eiq_" + str(feed_id) + "_" + state["feed_name"] + "_" + k
            qpylib.log("ingest_feed_api.{0}: Feed id {1}, add {2} observables into RT {3}.".format(func_name,str(feed_id),len(data_to_add[k]), rt_title), level='info')            
            # put data from each dict from data_to_add
            # to right table in QRadar
            if len(data_to_add[k]) > 0:
                qrdar_obj.bulk_upload(rt_title, data_to_add[k])

    else:
        # There is a diff column so we need
        # to change existing rows (delete/add)
        qpylib.log("ingest_feed_api.{0}: Update method is 'diff', so check for changes and update .".format(func_name), level='info')
        for row in csvreader:
            # Loop through the rows and see what must be done
            if row['type'] in ["email", "domain"]:
                subname = row['type']
            elif row['type'] == "uri":
                subname = "url"
            elif row['type'] == "ipv4":
                subname = "ip"
            elif row['type'] in ["hash-md5", "hash-sha1", "hash-sha256", "hash-sha512"]:
                subname = "file_hash"
            else:
                continue

            if row['diff'] == 'add':
                data_to_add[subname][row['value']] = {'feed_id': str(feed_id)}

                for field_name in EXPORT_FIELDS_LIST:
                    if re.match(r'\w+\.', field_name):
                        new_name = re.sub(r"\w+\.", "", field_name) + "_eiq"
                        data_to_add[subname][row['value']][new_name] = row[field_name]
                    elif field_name == 'type':
                        new_name = "value_" + field_name
                        data_to_add[subname][row['value']][new_name] = row[field_name]      
            elif row['diff'] == 'del':
                data_to_del.append({'table_name': "eiq_" + str(feed_id) + "_" + state["feed_name"] + "_" + subname,
                                    'outer_key': row['value']})

        for k in QRADAR_RT_LIST:
            rt_title = "eiq_" + str(feed_id) + "_" + state["feed_name"] + "_" + k
            qpylib.log("ingest_feed_api.{0}: Feed id {1}, add {2} observables into RT {3}.".format(func_name,str(feed_id),len(data_to_add[k]), rt_title), level='info')            
            # put data from each dict from data_to_add
            # to right table in QRadar
            if len(data_to_add[k]) > 0:
                qrdar_obj.bulk_upload(rt_title, data_to_add[k])

        for k in QRADAR_RT_LIST:
            qpylib.log("ingest_feed_api.{0}: Feed id {1}, remove {2} observables from RT {3}.".format(func_name, str(feed_id), len(data_to_del), rt_title), level='info')
            rt_title = "eiq_" + str(feed_id) + "_" + state["feed_name"] + "_" + k
         
            for observable in data_to_del:
                qrdar_obj.observable_delete(observable['table_name'], observable['outer_key'])
                qpylib.log("ingest_feed_api.{0}: observable {1} deleted.".format(func_name, observable['outer_key']), level='info')
