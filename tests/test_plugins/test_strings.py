""" Testing Strings Module
"""

import unittest
from ddt import ddt, data, unpack
from ashaw_notes.plugins.strings import Plugin


@ddt
class PluginTests(unittest.TestCase):
    """Unit Testing Plugin"""

    @unpack
    @data(
        (1373500800,
         'today: derp note',
         'today: derp note'),
        (1373500800,
         '"I said this"',
         '<span style=\'color:#E6DB5A\'>&quot;I said this&quot;</span>'),
        (1373500800,
         '"a" & "b"',
         '<span style=\'color:#E6DB5A\'>&quot;a&quot;</span>' \
         ' & <span style=\'color:#E6DB5A\'>&quot;b&quot;</span>'),
    )
    def test_format_note_line(self, timestamp, note, expectation):
        """Verifies format_note_line is properly functioning"""
        self.assertEqual(
            expectation,
            Plugin().format_note_line(timestamp, note)
        )
