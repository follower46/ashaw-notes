""" Testing Rage/Bold Module
"""

import unittest
from ddt import ddt, data, unpack
from ashaw_notes.plugins.rage import Plugin


@ddt
class PluginTests(unittest.TestCase):
    """Unit Testing Plugin"""

    @unpack
    @data(
        (1373500800,
         'today: derp note',
         'today: derp note'),
        (1373500800,
         '*I said this*',
         "<span style='color:#ccc;text-shadow:0px 0px 20px #000;font-weight:bold;'>" \
         "I said this</span>"),
        (1373500800,
         '*a* & **b**',
         "<span style='color:#ccc;text-shadow:0px 0px 20px #000;font-weight:bold;'>" \
         "a</span> & <span style='color:#c33;font-weight:bold;text-transform:uppercase;'>" \
         "b</span>"),
    )
    def test_format_note_line(self, timestamp, note, expectation):
        """Verifies format_note_line is properly functioning"""
        self.assertEqual(
            expectation,
            Plugin().format_note_line(timestamp, note)
        )
