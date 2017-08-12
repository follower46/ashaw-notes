""" Testing Search Module
"""

import unittest
from ddt import ddt, data, unpack
from ashaw_notes.plugins.lunch import Plugin


@ddt
class PluginTests(unittest.TestCase):
    """Unit Testing Plugin"""

    @unpack
    @data(
        ('lunch', True),
        ('testing', False),
        ('lunch... almost', False),
        ('out for lunch', False),
    )
    def test_is_plugin_note(self, note, expectation):
        """Verifies is_plugin_note is properly functioning"""
        self.assertEqual(
            expectation,
            Plugin().is_plugin_note(note)
        )


    def test_process_input(self):
        """Verifies process_input is properly functioning"""
        self.assertEqual(
            'anything',
            Plugin().process_input('anything')
        )
