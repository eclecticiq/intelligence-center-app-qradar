import sys
import json
import urllib

from qpylib import qpylib
from requests.utils import requote_uri

QR_PATHS = {
    "rt_endpoint": "api/reference_data/tables",
    "rt_bulk_load_endpoint": "api/reference_data/tables/bulk_load",
}

FIELDS_LIST = [
    "value_type",
    "type_eiq",
    "title_eiq",
    "relevancy_eiq",
    "tags_eiq",
    "taxonomy_eiq",
    "classification_eiq",
    "confidence_eiq",
    "feed_id",
]


class logs:
    def error(self, message):
        qpylib.log(message, level="error")

    def info(self, message):
        qpylib.log(message, level="info")

    def debug(self, message):
        qpylib.log(message, level="debug")

    def exception(self, message):
        qpylib.log(message, level="exception")


class QRadar_api(object):
    def __init__(self, token):

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.version = "13.0"
        self.headers["SEC"] = token

    def get_reference_table(self, rt_name):
        func_name = sys._getframe().f_code.co_name
        qpylib.log(
            "QRadar_api.{0}: Getting Reference table {1} info.".format(
                func_name, rt_name
            ),
            level="info",
        )
        url = QR_PATHS["rt_endpoint"] + "/" + rt_name

        r = qpylib.REST("GET", url, headers=self.headers, version=self.version)

        if r.status_code == 404:
            qpylib.log(
                "QRadar_api.{0}: The reference table {1} does not exist.".format(
                    func_name, rt_name
                ),
                level="error",
            )
            return False
        elif r.status_code == 422:
            qpylib.log(
                "QRadar_api.{0}: A request parameter is not valid. Requested Reference Table: {1}.".format(
                    func_name, rt_name
                ),
                level="error",
            )
            return "Error"
        elif r.status_code == 500:
            qpylib.log(
                "QRadar_api.{0}: An error occurred while attempting to retrieve the reference table: {1}.".format(
                    func_name, rt_name
                ),
                level="error",
            )
            return "Error"
        elif r.status_code not in [200, 201]:
            qpylib.log(
                "QRadar_api.{0}: Error. Code: {1} Text: {2}.".format(
                    func_name, r.status_code, r.text
                ),
                level="error",
            )
            return "Error"
        else:
            qpylib.log(
                "QRadar_api.{0}: Reference Table {1} retrieved.".format(
                    func_name, rt_name
                ),
                level="info",
            )
            return r.status_code

    def set_reference_table(self, rt_name):
        func_name = sys._getframe().f_code.co_name

        element_type = "ALNIC"
        rt_fields = json.dumps(
            [
                {"key_name": "type_eiq", "element_type": "ALNIC"},
                {"key_name": "classification_eiq", "element_type": "ALNIC"},
                {"key_name": "tags_eiq", "element_type": "ALNIC"},
                {"key_name": "title_eiq", "element_type": "ALNIC"},
                {"key_name": "taxonomy_eiq", "element_type": "ALNIC"},
                {"key_name": "confidence_eiq", "element_type": "ALNIC"},
                {"key_name": "relevancy_eiq", "element_type": "ALNIC"},
                {"key_name": "value_type", "element_type": "ALNIC"},
            ]
        )
        params = {}
        params = {
            "name": rt_name,
            "element_type": element_type,
            "outer_key_label": "eiq_value",
            "key_name_types": rt_fields,
        }

        qpylib.log(
            "QRadar_api.{0}: Creating Reference table {1}.".format(func_name, rt_name),
            level="info",
        )

        r = qpylib.REST(
            "POST",
            QR_PATHS["rt_endpoint"],
            headers=self.headers,
            params=params,
            version=self.version,
        )

        if r.status_code == 422:
            qpylib.log(
                "QRadar_api.{0}: A request parameter is not valid for table creation: {1}.".format(
                    func_name, rt_name
                ),
                level="error",
            )
        elif r.status_code == 409:
            qpylib.log(
                "QRadar_api.{0}: The reference table could not be created, the name provided is already in use {1}.".format(
                    func_name, rt_name
                ),
                level="info",
            )
        elif r.status_code not in [200, 201]:
            qpylib.log(
                "QRadar_api.{0}: Error. Code: {1} Text: {2}.".format(
                    func_name, r.status_code, r.text
                ),
                level="error",
            )
        else:
            qpylib.log(
                "QRadar_api.{0}: Reference Table {1} created.".format(
                    func_name, rt_name
                ),
                level="info",
            )

    def purge_reference_table(self, rt_name):
        func_name = sys._getframe().f_code.co_name
        params = {"name": rt_name, "purge_only": "true"}
        qpylib.log(
            "QRadar_api.{0}: Purging Reference Table: {1}.".format(func_name, rt_name),
            level="info",
        )

        url = QR_PATHS["rt_endpoint"] + "/" + rt_name

        r = qpylib.REST(
            "DELETE", url, headers=self.headers, params=params, version=self.version
        )

        if r.status_code == 422:
            qpylib.log(
                "QRadar_api.{0}: A request parameter is not valid to purge table: {1}.".format(
                    func_name, rt_name
                ),
                level="error",
            )
        elif r.status_code == 404:
            qpylib.log(
                "QRadar_api.{0}: The reference table {1} doesnt exist for purging.".format(
                    func_name, rt_name
                ),
                level="info",
            )
        elif r.status_code not in [200, 201, 202]:
            qpylib.log(
                "QRadar_api.{0}: Error. Code: {1} Text: {2}.".format(
                    func_name, r.status_code, r.text
                ),
                level="error",
            )
        else:
            qpylib.log(
                "QRadar_api.{0}: Reference Table {1} purged.".format(
                    func_name, rt_name
                ),
                level="info",
            )

    def observable_delete(self, rt_name, outer_key):
        func_name = sys._getframe().f_code.co_name
        qpylib.log(
            "QRadar_api.{0}: Delete observable {1} from reference table {2}.".format(
                func_name, outer_key, rt_name
            ),
            level="info",
        )

        del_data = {}

        for i in FIELDS_LIST:
            del_data[outer_key] = {}
            del_data[outer_key][i] = "del"
            self.bulk_upload(rt_name, del_data)

        outer_key = requote_uri(requote_uri(outer_key))

        for i in FIELDS_LIST:
            url = (
                QR_PATHS["rt_endpoint"]
                + "/"
                + rt_name
                + "/"
                + outer_key
                + "/"
                + i
                + "?value=del"
            )
            r = qpylib.REST("DELETE", url, headers=self.headers, version=self.version)

        if r.status_code == 500:
            qpylib.log(
                "QRadar_api.{0}: An error occurred while attempting to remove the reference table value: {1}.".format(
                    func_name, rt_name
                ),
                level="error",
            )
        elif r.status_code == 422:
            qpylib.log(
                "QRadar_api.{0}: A request parameter is not valid: {1}.".format(
                    func_name, rt_name
                ),
                level="error",
            )
        elif r.status_code == 404:
            qpylib.log(
                "QRadar_api.{0}: The record does not exist in the reference table {1}.".format(
                    func_name, rt_name
                ),
                level="error",
            )
        else:
            qpylib.log(
                "QRadar_api.{0}: The reference table {1} had had a value removed.".format(
                    func_name, rt_name
                ),
                level="info",
            )

    def observable_upload(self, rt_name, data):
        func_name = sys._getframe().f_code.co_name

        qpylib.log(
            "QRadar_api.{0}: Upload observable to Reference Table {1}.".format(
                func_name, rt_name
            ),
            level="info",
        )

        data = json.dumps(data)
        url = QR_PATHS["rt_bulk_load_endpoint"] + "/" + rt_name
        params = {"name": rt_name, "value": data}

        r = qpylib.REST(
            "POST",
            url,
            headers=self.headers,
            params=params,
            data=data,
            version=self.version,
        )

        if r.status_code == 404:
            qpylib.log(
                "QRadar_api.{0}: The reference table {1} does not exist.".format(
                    func_name, rt_name
                ),
                level="error",
            )
        elif r.status_code == 422:
            qpylib.log(
                "QRadar_api.{0}: A request parameter is not valid. Upload observable to Table: {1}.".format(
                    func_name, rt_name
                ),
                level="error",
            )
        elif r.status_code == 500:
            qpylib.log(
                "QRadar_api.{0}: An error occurred while attempting to add or update data in the reference table {1}.".format(
                    func_name, rt_name
                ),
                level="error",
            )
        elif r.status_code not in [200, 201]:
            qpylib.log(
                "QRadar_api.{0}: Error. Code: {1} Text: {2}.".format(
                    func_name, r.status_code, r.text
                ),
                level="error",
            )
        else:
            qpylib.log(
                "QRadar_api.{0}: Bulk upload to Reference Table {1} was successful.".format(
                    func_name, rt_name
                ),
                level="info",
            )

    def bulk_upload(self, rt_name, data):
        func_name = sys._getframe().f_code.co_name
        qpylib.log(
            "QRadar_api.{0}: Bulk upload to Reference Table {1}.".format(
                func_name, rt_name
            ),
            level="info",
        )

        data = json.dumps(data)
        url = QR_PATHS["rt_bulk_load_endpoint"] + "/" + rt_name
        params = {"name": rt_name}

        r = qpylib.REST(
            "POST",
            url,
            headers=self.headers,
            params=params,
            data=data,
            version=self.version,
        )

        if r.status_code == 400:
            qpylib.log(
                "QRadar_api.{0}: An error occurred parsing the JSON-formatted message body. Bulk upload to Table: {1}.".format(
                    func_name, rt_name
                ),
                level="error",
            )
        elif r.status_code == 404:
            qpylib.log(
                "QRadar_api.{0}: The reference table {1} does not exist.".format(
                    func_name, rt_name
                ),
                level="error",
            )
        elif r.status_code == 422:
            qpylib.log(
                "QRadar_api.{0}: A request parameter is not valid. Bulk upload to Table: {1}.".format(
                    func_name, rt_name
                ),
                level="error",
            )
        elif r.status_code == 500:
            qpylib.log(
                "QRadar_api.{0}: An error occurred during the attempt to add or update data in the reference table {1}.".format(
                    func_name, rt_name
                ),
                level="error",
            )
        elif r.status_code not in [200, 201]:
            qpylib.log(
                "QRadar_api.{0}: Error. Code: {1} Text: {2}.".format(
                    func_name, r.status_code, r.text
                ),
                level="error",
            )
        else:
            qpylib.log(
                "QRadar_api.{0}: Bulk upload to Reference Table {1} was successful.".format(
                    func_name, rt_name
                ),
                level="info",
            )

    def check_py_interpeter(self):
        func_name = sys._getframe().f_code.co_name
        qpylib.log(
            "QRadar_api.{0}: Checking python interpreter ID.".format(func_name),
            level="debug",
        )

        params = {"filter": "name=Python"}

        r = qpylib.REST(
            "GET",
            QR_PATHS["ca_interp"],
            headers=self.headers,
            params=params,
            version=self.version,
        )

        if r.status_code == 500:
            qpylib.log(
                "QRadar_api.{0}: An internal server error occurred while retrieving available custom action interpreters.".format(
                    func_name
                ),
                level="error",
            )
            return "Error"
        elif r.status_code not in [200, 201]:
            qpylib.log(
                "QRadar_api.{0}: Error. Code: {1} Text: {2}.".format(
                    func_name, r.status_code, r.text
                ),
                level="error",
            )
            return "Error"
        else:
            if len(r.json()) == 1:
                qpylib.log(
                    "QRadar_api.{0}: Python interpreter ID checked.".format(func_name),
                    level="debug",
                )
                return r.json()[0]["id"]
            elif len(r.json()) == 0:
                qpylib.log(
                    "QRadar_api.{0}: Python interpreter ID not found.".format(
                        func_name
                    ),
                    level="error",
                )
                return 0
            else:
                qpylib.log(
                    "QRadar_api.{0}: Found more than one Python interpreter.".format(
                        func_name
                    ),
                    level="error",
                )
                return "Multi results"

    def check_action_script(self):
        func_name = sys._getframe().f_code.co_name
        qpylib.log(
            "QRadar_api.{0}: Checking Custom Action script.".format(func_name),
            level="info",
        )

        params = {"filter": 'file_name="eiq_sighting.py"'}

        r = qpylib.REST(
            "GET",
            QR_PATHS["ca_scripts"],
            headers=self.headers,
            params=params,
            version=self.version,
        )

        if r.status_code == 500:
            qpylib.log(
                "QRadar_api.{0}: An internal server error occurred while retrieving custom action script.".format(
                    func_name
                ),
                level="error",
            )
            return "Error"
        elif r.status_code not in [200, 201]:
            qpylib.log(
                "QRadar_api.{0}: Error. Code: {1} Text: {2}.".format(
                    func_name, r.status_code, r.text
                ),
                level="error",
            )
            return "Error"
        else:
            if len(r.json()) == 1:
                qpylib.log(
                    "QRadar_api.{0}: Custom Action Script ID retrieved.".format(
                        func_name
                    ),
                    level="debug",
                )
                return r.json()
            elif len(r.json()) == 0:
                qpylib.log(
                    "QRadar_api.{0}: Custom Action Script ID not found.".format(
                        func_name
                    ),
                    level="debug",
                )
                return r.json()
            else:
                qpylib.log(
                    "QRadar_api.{0}: Found more than one Custom Action Script ID.".format(
                        func_name
                    ),
                    level="debug",
                )
                return r.json()

    def set_action_script(self):
        func_name = sys._getframe().f_code.co_name
        qpylib.log(
            "QRadar_api.{0}: Creating Custom Action script.".format(func_name),
            level="debug",
        )

        headers = self.headers.copy()
        headers["file_name"] = "eiq_sighting.py"
        headers["Content-Type"] = "application/octet-stream"

        script_path = qpylib.get_root_path() + "/app/apilib/eiq_sighting.py"
        data = open(script_path, "rb").read()

        r = qpylib.REST(
            "POST",
            QR_PATHS["ca_scripts"],
            headers=headers,
            version=self.version,
            data=data,
        )

        if r.status_code == 500:
            qpylib.log(
                "QRadar_api.{0}: An internal server error occurred while posting custom action script file..".format(
                    func_name
                ),
                level="error",
            )
            return "Error"
        elif r.status_code not in [200, 201]:
            qpylib.log(
                "QRadar_api.{0}: Error. Code: {1} Text: {2}.".format(
                    func_name, r.status_code, r.text
                ),
                level="error",
            )
            return "Error"
        else:
            qpylib.log(
                "QRadar_api.{0}: Custom Action Script created.".format(func_name),
                level="info",
            )

    def delete_action_script(self, script_nu):
        func_name = sys._getframe().f_code.co_name
        qpylib.log(
            "QRadar_api.{0}: Deleteing Custom Action script #{1}.".format(
                func_name, script_nu
            ),
            level="info",
        )

        params = {"script_id": str(script_nu)}
        headers = self.headers.copy()
        headers["Content-Type"] = "text/plain"
        headers["Accept"] = "text/plain"

        url = QR_PATHS["ca_scripts"] + "/" + str(script_nu)
        r = qpylib.REST(
            "DELETE", url, headers=headers, params=params, version=self.version
        )

        if r.status_code == 500:
            qpylib.log(
                "QRadar_api.{0}: An internal server error occurred while deleting custom action script file with script #{1}.".format(
                    func_name, script_nu
                ),
                level="error",
            )
            return "Error"
        elif r.status_code not in [200, 201, 204]:
            qpylib.log(
                "QRadar_api.{0}: Error. Code: {1} Text: {2}.".format(
                    func_name, r.status_code, r.text
                ),
                level="error",
            )
            return "Error"
        else:
            qpylib.log(
                "QRadar_api.{0}: Custom Action Script #{1} deleted.".format(
                    func_name, script_nu
                ),
                level="info",
            )

    def check_action(self, action_name):
        func_name = sys._getframe().f_code.co_name
        qpylib.log(
            "QRadar_api.{0}: Checking Custom Action: {1}.".format(
                func_name, action_name
            ),
            level="debug",
        )

        params = {"filter": "name=" + action_name}

        r = qpylib.REST(
            "GET",
            QR_PATHS["ca_actions"],
            headers=self.headers,
            params=params,
            version=self.version,
        )

        if r.status_code == 500:
            qpylib.log(
                "QRadar_api.{0}: An internal server error occurred while retrieving custom actions.".format(
                    func_name
                ),
                level="error",
            )
            return "Error"
        elif r.status_code not in [200, 201]:
            qpylib.log(
                "QRadar_api.{0}: Error. Code: {1} Text: {2}.".format(
                    func_name, r.status_code, r.text
                ),
                level="error",
            )
            return "Error"
        else:
            if len(r.json()) == 1:
                qpylib.log(
                    "QRadar_api.{0}: Custom Action {1} ID retrieved.".format(
                        func_name, action_name
                    ),
                    level="debug",
                )
                return r.json()
            elif len(r.json()) == 0:
                qpylib.log(
                    "QRadar_api.{0}: Custom Action ID not found.".format(func_name),
                    level="debug",
                )
                return "0"
            else:
                qpylib.log(
                    "QRadar_api.{0}: Found more than one Custom Action ID.".format(
                        func_name
                    ),
                    level="debug",
                )
                return "Multi results"

    def set_action(
        self,
        action_name,
        py_interpreter_id,
        script_id,
        p1_eiq_url,
        p2_eiq_ver,
        p3_eiq_user,
        p4_eiq_pass,
        p5_eiq_group_name,
        p6_eiq_type,
        p7_eiq_value,
    ):
        func_name = sys._getframe().f_code.co_name
        qpylib.log(
            "QRadar_api.{0}: Creating Custom Action: {1}.".format(
                func_name, action_name
            ),
            level="info",
        )

        params = {
            "description": "EcelectiqIQ custom action for creating Sightings.",
            "interpreter": py_interpreter_id,
            "name": action_name,
            "parameters": [
                {
                    "encrypted": False,
                    "name": "p1_eiq_url",
                    "parameter_type": "fixed",
                    "value": p1_eiq_url,
                },
                {
                    "encrypted": False,
                    "name": "p2_eiq_ver",
                    "parameter_type": "fixed",
                    "value": p2_eiq_ver,
                },
                {
                    "encrypted": False,
                    "name": "p3_eiq_user",
                    "parameter_type": "fixed",
                    "value": p3_eiq_user,
                },
                {
                    "encrypted": True,
                    "name": "p4_eiq_pass",
                    "parameter_type": "fixed",
                    "value": p4_eiq_pass,
                },
                {
                    "encrypted": False,
                    "name": "p5_eiq_group_name",
                    "parameter_type": "fixed",
                    "value": p5_eiq_group_name,
                },
                {
                    "encrypted": False,
                    "name": "p6_eiq_type",
                    "parameter_type": "fixed",
                    "value": p6_eiq_type,
                },
                {
                    "encrypted": False,
                    "name": "p7_eiq_value",
                    "parameter_type": "dynamic",
                    "value": p7_eiq_value,
                },
            ],
            "script": script_id,
        }

        data = json.dumps(params)

        r = qpylib.REST(
            "POST",
            QR_PATHS["ca_actions"],
            headers=self.headers,
            data=data,
            version=self.version,
        )

        if r.status_code == 500:
            qpylib.log(
                "QRadar_api.{0}: An internal server error occurred while creating Custom Action {1}.".format(
                    func_name, action_name
                ),
                level="error",
            )
            return "Error"
        elif r.status_code not in [200, 201]:
            qpylib.log(
                "QRadar_api.{0}: Error. Code: {1} Text: {2}.".format(
                    func_name, r.status_code, r.text
                ),
                level="error",
            )
            return "Error"
        else:
            qpylib.log(
                "QRadar_api.{0}: Custom Action {1} created.".format(
                    func_name, action_name
                ),
                level="info",
            )

    def delete_action(self, action_id):
        func_name = sys._getframe().f_code.co_name
        qpylib.log(
            "QRadar_api.{0}: Deleting Custom Action: {1}.".format(func_name, action_id),
            level="info",
        )

        url = QR_PATHS["ca_actions"] + "/" + str(action_id)

        local_headers = {}
        local_headers["Content-Type"] = "text/plain"
        local_headers["Accept"] = "text/plain"

        r = qpylib.REST("DELETE", url, headers=local_headers, version=self.version)

        if r.status_code == 500:
            qpylib.log(
                "QRadar_api.{0}: An internal server error occurred while creating Custom Action {1}.".format(
                    func_name, action_id
                ),
                level="error",
            )
            return "Error"
        elif r.status_code not in [200, 201, 204]:
            qpylib.log(
                "QRadar_api.{0}: Error. Code: {1} Text: {2}.".format(
                    func_name, r.status_code, r.text
                ),
                level="error",
            )
            return "Error"
        else:
            qpylib.log(
                "QRadar_api.{0}: Custom Action {1} created.".format(
                    func_name, action_id
                ),
                level="info",
            )
