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
    def test_is_date(self, data):
        """Verifies is_date is properly functioning"""
        string, expectation = data
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
    def test_is_hashtag(self, data):
        """Verifies is_hashtag is properly functioning"""
        string, expectation = data
        self.assertEqual(search.is_hashtag(string), expectation)
