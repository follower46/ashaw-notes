#!/usr/bin/python3

""" Configuration Helper Module
"""
import configparser
import importlib
from os import path

__local_config__ = None
PATH_OPTIONS = ['notes-local.config', 'notes.config']


def load_config():
    """Loads application configuration"""
    global __local_config__
    if not __local_config__:
        __local_config__ = configparser.ConfigParser()
        __local_config__.read(get_notes_file_location())
    return __local_config__


def reload_config():
    """Reloads application configuration"""
    global __local_config__
    __local_config__ = None
    return load_config()


def get_notes_file_location():
    """Returns best configuration for application"""
    for path_option in PATH_OPTIONS:
        if path.isfile(path_option):
            return path_option
    raise Exception("Config not found. Please verify configuration deployment")


def get_connection_modules():
    """Returns all enabled backend modules"""
    modules = []
    module_names = load_config().get('base_config', 'data_backends')
    for module_name in [name.strip() for name in module_names.split(',')]:
        modules.append(importlib.import_module("ashaw_notes.connectors.%s" % module_name))
    return modules


def get_primary_connection_module():
    """Returns primary backend modules"""
    return get_connection_modules()[0]
