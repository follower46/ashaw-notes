""" Testing Base Plugin
"""

import unittest
from mock import MagicMock
from ashaw_notes.plugins.base_plugin import Plugin


class BaseTests(unittest.TestCase):
    """Unit Testing Base Plugin"""

    def test_is_plugin_note(self):
        """Verifies is_plugin_note is properly functioning"""
        self.assertFalse(Plugin().is_plugin_note('anything'))

    def test_process_input(self):
        """Verifies process_input is properly functioning"""
        self.assertEqual(
            'anything',
            Plugin().process_input('anything')
        )

    def test_process_search_request(self):
        """Verifies process_search_request is properly functioning"""
        search = MagicMock()
        self.assertEqual(
            search,
            Plugin().process_search_request(search))

    def test_format_note_line(self):
        """Verifies format_note_line is properly functioning"""
        self.assertEqual(
            "today: Did some unit tests",
            Plugin().format_note_line(1373500800, "today: Did some unit tests"))
