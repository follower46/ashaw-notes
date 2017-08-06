#!/usr/bin/python3

""" Search Helper Module
"""
import re
import time
from dateutil.parser import parse


def is_date(string):
    try: 
        parse(string)
        return True
    except ValueError:
        return False


def is_hashtag(string):
    if re.match(r'^#\w+$', string):
        return True
    return False


def datestring_to_timestamp(string):
    return int(time.mktime(time.strptime(timestamp)))


def timestamp_to_datestring(timestamp):
    return time.asctime(time.localtime(timestamp))


def get_search_request(terms=[]):
    return SearchRequest(terms)


class SearchRequest:
    inclusion_terms = []
    exclusion_terms = []
    date_range = [] # not implemented
    page_limit = 0 # not implemented
    page_index = 1 # not implemented
    def __init__(self, search_terms):
        for term in search_terms:
            if term.find("!") == 0:
                self.exclusion_terms.append(term[1:].lower())
            else:
                self.inclusion_terms.append(term.lower())
