""" Testing Search Module
"""

import unittest
from scripts import quicknote
from ddt import ddt, data, unpack


@ddt
class QuicknoteTests(unittest.TestCase):
    """Unit Testing Quicknote"""

    def test_process_note(self):
        """Verifies is_date is properly functioning"""
        quicknote.process_note('test')
