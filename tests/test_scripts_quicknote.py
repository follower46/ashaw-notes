""" Testing Search Module
"""

import unittest
from scripts import quicknote
from ddt import ddt, data, unpack


@ddt
class QuicknoteTests(unittest.TestCase):
    """Unit Testing Quicknote"""

    def test_setup_auto_complete(self, string, expectation):
        """Verifies is_date is properly functioning"""
        quicknote.setup_auto_complete()
