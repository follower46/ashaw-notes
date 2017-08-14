#!/usr/bin/python3

""" Configuration Helper Module
"""
import configparser
import importlib
from os import path
import logzero

__local_config__ = None
PATH_OPTIONS = ['notes-local.config', 'notes.config']


def load_config():
    """Loads application configuration"""
    global __local_config__
    if not __local_config__:
        __local_config__ = configparser.ConfigParser()
        __local_config__.read(get_config_location())
    return __local_config__


def reload_config():
    """Reloads application configuration"""
    global __local_config__
    __local_config__ = None
    return load_config()


def get_config_location():
    """Returns best configuration for application"""
    for path_option in PATH_OPTIONS:
        if path.isfile(path_option):
            return path_option
    raise Exception("Config not found. Please verify configuration deployment")


def get_logger():
    """Configures and returns a logzero client"""
    config = load_config()
    logzero.logfile(
        config.get('logging', 'location'),
        maxBytes=float(config.get('logging', 'max_bytes')),
        backupCount=int(config.get('logging', 'backup_count'))
    )
    return logzero.logger
