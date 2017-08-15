""" Testing Search Module
"""

import unittest
from ashaw_notes.plugins.base_plugin import Plugin


class SearchTests(unittest.TestCase):
    """Unit Testing Search"""

    def test_is_plugin_note(self):
        """Verifies is_plugin_note is properly functioning"""
        self.assertFalse(Plugin().is_plugin_note('anything'))

    def test_process_input(self):
        """Verifies process_input is properly functioning"""
        self.assertEqual(
            'anything',
            Plugin().process_input('anything')
        )
