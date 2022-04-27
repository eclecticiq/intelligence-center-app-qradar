"""Utility methods for files ."""

import yaml  # type: ignore


def get_yaml_content(filename):
    """Read the yaml configuration file.

    :param filename: YAML configurations file path
    :type filename: str
    :return: List of YAML configurations
    :rtype: dict
    """
    with open(filename) as file:
        schedule_list = yaml.safe_load(file)
    return schedule_list


def read_yaml_configurations(filename):
    """Read YAML file configuration and create dictionary.

    :param filename: YAML configurations file path
    :type filename: str
    :return: YAML configuration dictionary
    :rtype: dict
    """
    schedule_list = get_yaml_content(filename)
    configurations = {}
    for func_name, docs in schedule_list.items():
        config = {}
        for item in docs:
            for key, value in item.items():
                config[key] = value
        configurations[func_name] = config
    return configurations
