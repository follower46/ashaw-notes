""" Testing Date Handler Module
"""

import unittest
from ddt import ddt, data, unpack
from ashaw_notes.plugins.datehandler import Plugin


@ddt
class PluginTests(unittest.TestCase):
    """Unit Testing Plugin"""

    @unpack
    @data(
        (1373500800,
         'derp note',
         'derp note'),
        (1373500800,
         'today: yay',
         "<span style='color:#A6E22E' title='Thu Jul 11 00:00:00 2013'>today:</span> yay"),
    )
    def test_format_note_line(self, timestamp, note, expectation):
        """Verifies format_note_line is properly functioning"""
        self.assertEqual(
            expectation,
            Plugin().format_note_line(timestamp, note)
        )
