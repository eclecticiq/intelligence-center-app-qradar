"""Data store module.

Contains helper functions to access data store file.
"""

import json
import os
from app.configs.datastore import DATA_STORE_DIR, DATA_STORE_FILE, DATA_STORE_SETUP_FILE


def get_data_store_path(directory, file_name):
    """Get Datastore file path.

    :return: Path of the datastore file which stores all the configurations for user authentication
    :rtype: str
    """
    return os.path.join(directory, file_name)


def overwrite_setup_data_store(data):
    """Overwrite current data file if exists otherwise creates new file and writes data.

    :param data: dict
    :return: None
    """
    filename = get_data_store_path(DATA_STORE_DIR, DATA_STORE_SETUP_FILE)
    with open(filename, "w") as file:
        json.dump(data, file)


def overwrite_data_store(data):
    """Overwrite current data file if exists otherwise creates new file and writes data.

    :param data: dict
    :return: None
    """
    filename = get_data_store_path(DATA_STORE_DIR, DATA_STORE_FILE)
    with open(filename, "w") as file:
        json.dump(data, file)


def update_data_store(data):
    """Update current data file if available otherwise creates new file and writes data.

    Uses standard dictionary update logic. ie if the key is already present, updates its value,
    Otherwise creates a new key value pair
    :param data: dict
    :return: None
    """
    filename = get_data_store_path(DATA_STORE_DIR, DATA_STORE_FILE)
    try:
        with open(filename) as file:
            current_data = json.load(file)
    except OSError:
        current_data = {}

    current_data.update(data)
    overwrite_data_store(current_data)


def read_data_store(directory, file_name):
    """Return all data in data file.

    Reads all the data from the file and converts it into a dictionary.
    If dat file is not present, an empty dictionary will be returned
    :return: dict
    """
    filename = get_data_store_path(directory, file_name)
    try:
        with open(filename) as file:
            return json.load(file)
    except OSError:
        return {}
