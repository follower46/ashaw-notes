""" Testing Arrows Module
"""

import unittest
from ddt import ddt, data, unpack
from ashaw_notes.plugins.arrows import Plugin


@ddt
class PluginTests(unittest.TestCase):
    """Unit Testing Plugin"""

    @unpack
    @data(
        (1373500800, 'today: derp note', 'today: derp note'),
        (1373500800, 'ashaw --> "cool plugin, dude"', 'ashaw &rArr; "cool plugin, dude"'),
        (1373500800, 'see? <-- left arrow', 'see? &lArr; left arrow'),
        (1373500800, 'double <--> arrow', 'double &hArr; arrow'),
    )
    def test_format_note_line(self, timestamp, note, expectation):
        """Verifies format_note_line is properly functioning"""
        self.assertEqual(
            expectation,
            Plugin().format_note_line(timestamp, note)
        )
