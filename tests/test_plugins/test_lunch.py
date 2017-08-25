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

    @unpack
    @data(
        (1373500800,
         'today: derp note',
         'today: derp note'),
        (1373500800,
         'went to lunch',
         "went to lunch"),
        (1373500800,
         'lunch',
         "<table style='width:100%;font-weight:bold;background-color:#511;" \
         "color:#fff;text-align:center;'>" \
         "<tr><td style='width: 100%;'>lunch break</td></tr></table>"),
    )
    def test_format_note_line(self, timestamp, note, expectation):
        """Verifies format_note_line is properly functioning"""
        self.assertEqual(
            expectation,
            Plugin().format_note_line(timestamp, note)
        )
