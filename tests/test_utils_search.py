""" Testing Search Module
"""

import unittest
from utils import search
from mock import patch
from ddt import ddt, data


@ddt
class SearchTests(unittest.TestCase):
    """Unit Testing Search"""

    @data(
        ('05/24/2017', True),
        ('06/33/2017', False),
        ('04-23-1969', True),
        ('Adam Shaw ', False),
        ('1234567890', False),
    )
    def test_is_date(self, data_set):
        """Verifies is_date is properly functioning"""
        string, expectation = data_set
        self.assertEqual(search.is_date(string), expectation)

    @data(
        ('#hashtag', True),
        ('!hashtag', False),
        ('#0123456', True),
        ('!0123456', False),
        ('#hashtag-with-dashes', True),
        ('#hashtag with spaces', False),
        ('#hashtag_underscored', True),
    )
    def test_is_hashtag(self, data_set):
        """Verifies is_hashtag is properly functioning"""
        string, expectation = data_set
        self.assertEqual(search.is_hashtag(string), expectation)

    @data(
        ('Thu Jul 11 00:00:00 2013', 1373518800),
        ('Tue Dec 22 14:23:08 2015', 1450815788),
        ('Mon May  1 17:06:30 2017', 1493676390),
    )
    def test_datestring_to_timestamp(self, data_set):
        """Verifies string can be converted into a timstamp"""
        string, expectation = data_set
        self.assertEqual(search.datestring_to_timestamp(string), expectation)

    @data(
        (1373518800, 'Thu Jul 11 00:00:00 2013'),
        (1450815788, 'Tue Dec 22 14:23:08 2015'),
        (1493676390, 'Mon May  1 17:06:30 2017'),
    )
    def test_timestamp_to_datestring(self, data_set):
        """Verifies string can be converted into a timstamp"""
        timestamp, expectation = data_set
        self.assertEqual(search.timestamp_to_datestring(timestamp), expectation)


    def test_get_search_request(self):
        """Verifies Search Object works as intended"""
        request = search.get_search_request()
        self.assertListEqual([], request.inclusion_terms)
        self.assertListEqual([], request.exclusion_terms)

        search_terms = ['include', '!exclude', 'include!']
        request = search.get_search_request(search_terms)

        self.assertListEqual(['include', 'include!'], request.inclusion_terms)
        self.assertListEqual(['exclude'], request.exclusion_terms)
