#!/usr/bin/python3

""" Search Helper Module
"""
import re
import time
import calendar
from dateutil.parser import parse
from ashaw_notes.utils.plugin_manager import PluginManager
import ashaw_notes.utils.configuration

def is_date(string):
    """Verifies string is a type of date"""
    try:
        parse(string)
        return True
    except ValueError:
        return False


def is_hashtag(string):
    """Verifies string is a type of hashtag"""
    if re.match(r'^#[\w-]+$', string):
        return True
    return False


def datestring_to_timestamp(string):
    """Converts string to timestamp"""
    return int(calendar.timegm(time.strptime(string)))


def timestamp_to_datestring(timestamp, with_time=True):
    """Converts timestamp to date string"""
    time_struct = time.gmtime(timestamp)
    if with_time:
        return time.asctime(time_struct)
    return time.strftime('%Y-%m-%d', time_struct)


def get_search_request(terms=None, allow_plugins=True):
    """Builds search request object"""
    request = SearchRequest(terms)
    if allow_plugins:
        return PluginManager().process_search_request(request)
    return request


class SearchRequest:
    """Search request object"""

    def __init__(self, search_terms):
        self.inclusion_terms = []
        self.exclusion_terms = []
        self.date = None
        self.page_limit = 0  # not implemented
        self.page_index = 0  # not implemented

        if search_terms is None:
            search_terms = []

        for term in search_terms:
            if term.find("!") == 0:
                self.exclusion_terms.append(term[1:].lower())
            else:
                self.inclusion_terms.append(term.lower())
