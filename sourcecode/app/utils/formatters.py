"""Format data ."""

from app.constants.general import (
    GLUE_COLONS,
    ID,
    OBSERVABLE_TYPES,
    OUTGOING_FEEDS,
    NAME,
)


def formatted_setup_data(data):
    """Get the formatted setup data from the data received in request .

    :param data: setup data
    :type data: dict
    :return: formatted setup data
    :rtype: dict
    """
    setup_data = {}
    for key, value in data.items():
        if key == OUTGOING_FEEDS:
            feeds = []
            for val in value:
                val_list = val.split(GLUE_COLONS)
                feeds_id_name = {NAME: val_list[0], ID: val_list[1]}
                feeds.append(feeds_id_name)
            setup_data[key] = feeds
        elif key == OBSERVABLE_TYPES:
            setup_data[key] = value
        else:
            setup_data[key] = value[0]
    return setup_data


def convert_formatted_data(outgoing_feeds):
    """Get the outgoing feeds data  to list of string .

    :param data: list of outgoing feeds dict
                [{"name":"feed1","id":6},{"name":"feed2","id":2}]
    :type data: list
    :return: list of outgoing feeds string
            ['feed1:::1', 'feed2:::2']
    :rtype: list
    """
    feeds_list = []
    for outgoing_feed in outgoing_feeds:
        feed_name = outgoing_feed[NAME]
        feed_id = outgoing_feed[ID]
        data = feed_name + GLUE_COLONS + str(feed_id)
        feeds_list.append(data)

    return feeds_list
