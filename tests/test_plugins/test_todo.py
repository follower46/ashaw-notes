""" Testing Search Module
"""

import unittest
from ddt import ddt, data, unpack
from ashaw_notes.plugins.todo import Plugin


@ddt
class PluginTests(unittest.TestCase):
    """Unit Testing Plugin"""

    @unpack
    @data(
        ('todo: finish unit tests', True),
        ('todone[0]: ugh, what a pain', True),
        ('todonatello', False),
        ('I almost todid something', False),
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
