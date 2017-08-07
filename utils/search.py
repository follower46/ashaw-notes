#!/usr/bin/python3

""" Search Helper Module
"""
import re
import time
from dateutil.parser import parse


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
    return int(time.mktime(time.strptime(string)))


def timestamp_to_datestring(timestamp):
    """Converts timestamp to date string"""
    return time.asctime(time.localtime(timestamp))


def get_search_request(terms=None):
    """Builds search request object"""
    return SearchRequest(terms)


class SearchRequest:
    """Search request object"""
    inclusion_terms = []
    exclusion_terms = []
    date_range = [] # not implemented
    page_limit = 0 # not implemented
    page_index = 1 # not implemented
    def __init__(self, search_terms):
        if search_terms is None:
            search_terms = []
        
        for term in search_terms:
            if term.find("!") == 0:
                self.exclusion_terms.append(term[1:].lower())
            else:
                self.inclusion_terms.append(term.lower())
