""" Testing Hashtags Module
"""

import unittest
from ddt import ddt, data, unpack
from ashaw_notes.plugins.hashtags import Plugin


@ddt
class PluginTests(unittest.TestCase):
    """Unit Testing Plugin"""

    @unpack
    @data(
        (1373500800,
         'today: derp note',
         'today: derp note'),
        (1373500800,
         'I love tests #truestory',
         "I love tests <a href='filter:#truestory' " \
         "style='color:#A6E22E;text-decoration:underline;'>" \
         "#truestory</a>"),
        (1373500800,
         'yolo #thuglyfe #hipster #crossfit #vegan',
         "yolo <a href='filter:#thuglyfe' " \
         "style='color:#A6E22E;text-decoration:underline;'>" \
         "#thuglyfe</a> " \
         "<a href='filter:#hipster' " \
         "style='color:#A6E22E;text-decoration:underline;'>" \
         "#hipster</a> " \
         "<a href='filter:#crossfit' " \
         "style='color:#A6E22E;text-decoration:underline;'>" \
         "#crossfit</a> " \
         "<a href='filter:#vegan' " \
         "style='color:#A6E22E;text-decoration:underline;'>" \
         "#vegan</a>"),
    )
    def test_format_note_line(self, timestamp, note, expectation):
        """Verifies format_note_line is properly functioning"""
        self.assertEqual(
            expectation,
            Plugin().format_note_line(timestamp, note)
        )
