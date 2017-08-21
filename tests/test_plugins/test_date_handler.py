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
         "<a href='filter:date:2013-07-11' " \
         "style='color:#A6E22E;text-decoration:none;' " \
         "title='Thu Jul 11 00:00:00 2013'>today:</a> yay"),
    )
    def test_format_note_line(self, timestamp, note, expectation):
        """Verifies format_note_line is properly functioning"""
        self.assertEqual(
            expectation,
            Plugin().format_note_line(timestamp, note)
        )
