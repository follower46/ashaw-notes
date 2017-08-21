""" Testing Strings Module
"""

import unittest
from ddt import ddt, data, unpack
from ashaw_notes.plugins.grawlixes import Plugin


@ddt
class PluginTests(unittest.TestCase):
    """Unit Testing Plugin"""

    def test_astyle(self):
        """Verifies style is set correct"""
        self.assertEqual(
            'color:#ccc;font-weight:bold;text-transform:uppercase;',
            Plugin.style
        )

    @unpack
    @data(
        (1373500800,
         'today: derp note',
         'today: derp note'),
        (1373500800,
         'hell, this is fun',
         '<span style="" title="hell">@#$%</span>, this is fun'),
        (1373500800,
         'fucking',
         '<span style="" title="fucking">@#$%ing</span>'),
        (1373500800,
         'CRAPSICKLES',
         '<span style="" title="CRAPSICKLES">@#$%SICKLES</span>'),
        (1373500800,
         'really iboubid that up',
         'really <span style="" title="iboubid">@#$%d</span> that up'),
        (1373500800,
         'bitching shithead',
         '<span style="" title="bitching">@#$%ing</span>' \
         ' <span style="" title="shithead">@#$%head</span>'),
        (1373500800,
         'fuckildoo... for the laughs',
         '<span style="" title="fuckildoo">@#$%ildoo</span>... for the laughs'),
    )
    def test_format_note_line(self, timestamp, note, expectation):
        """Verifies format_note_line is properly functioning"""
        Plugin.style = ''
        self.assertEqual(
            expectation,
            Plugin().format_note_line(timestamp, note)
        )
