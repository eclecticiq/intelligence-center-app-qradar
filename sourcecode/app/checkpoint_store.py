"""Store checkpoint in data store and perform read and write operations ."""

import os
import json
from app.configs.checkpoint_store import CHECKPOINT_STORE_DIR, CHECKPOINT_STORE_FILE

def get_checkpoint():
    """Get Checkpointfile path.

    :return: Path of the checkpoint file which stores all the configurations related to checkpoint data.
    :rtype: str
    """
    return os.path.join(CHECKPOINT_STORE_DIR, CHECKPOINT_STORE_FILE)

def read_checkpoint(outgoing_feed):
    """Return all data in data file.

    Reads all the data from the file.
    If data file is not present, an empty string will be returned

    :return: dict
    """
    outgoing_feed = str(outgoing_feed)
    filename = get_checkpoint()
    checkpoint = None
    try:
        with open(filename) as file:
            json_object = json.load(file)

        checkpoint = json_object.get(outgoing_feed)

        if checkpoint is None:
            checkpoint = {'created_at': None, "feed_name": None, "update_strategy": None}
    except FileNotFoundError:
        with open(filename, "w") as file:
            file.write("{}")
    return checkpoint

def write_checkpoint(outgoing_feed, checkpoint):
    """Overwrite current data file if exists otherwise creates new file and writes data.

    :param data: dict
    :return: None
    """
    outgoing_feed = str(outgoing_feed)
    filename = get_checkpoint()
    json_object = {}
    with open(filename) as file:
        json_object = json.load(file)

    with open(filename, "w") as file:
        json_object[outgoing_feed] = checkpoint
        file.write(json.dumps(json_object))

def remove_checkpoint():
    """Remove current checkpoint data."""
    filename = get_checkpoint()
    with open(filename, "w") as file:
        file.write(json.dumps({}))

def read_full_checkpoint():
    filename = get_checkpoint()
    checkpoint = None

    try:
        with open(filename) as file:
            json_object = json.load(file)

        checkpoint = json_object
    except FileNotFoundError:
        with open(filename, "w") as file:
            file.write("{}")
    return checkpoint

