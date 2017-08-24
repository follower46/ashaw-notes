""" Testing Wiki Module
"""

import unittest
from ddt import ddt, data, unpack
from ashaw_notes.plugins.wiki import Plugin


@ddt
class PluginTests(unittest.TestCase):
    """Unit Testing Plugin"""

    @unpack
    @data(
        (1373500800,
         'today: derp note',
         'today: derp note'),
        (1373500800,
         'today: wiki:unit_testing',
         "today: <a style='color:#66D9B1;' " \
         "href='http://en.wikipedia.org/wiki/unit_testing'>unit testing</a>"),
        (1373500800,
         'today: wiki:unit_testing#for_real',
         "today: <a style='color:#66D9B1;' " \
         "href='http://en.wikipedia.org/wiki/unit_testing#for_real'>unit testing - for real</a>"),
    )
    def test_format_note_line(self, timestamp, note, expectation):
        """Verifies format_note_line is properly functioning"""
        self.assertEqual(
            expectation,
            Plugin().format_note_line(timestamp, note)
        )
