""" Date Handler Module
"""
import re
import dateparser
from ashaw_notes.plugins import base_plugin
import ashaw_notes.utils.configuration


class Plugin(base_plugin.Plugin):
    """Date Handler Plugin Class"""

    right_arrow_regex = re.compile(r'-->')
    left_arrow_regex = re.compile(r'<--')
    double_arrow_regex = re.compile(r'<-->')

    def format_note_line(self, timestamp, note_line):
        """Allows enabled plugins to modify note display"""
        note_line = Plugin.right_arrow_regex.sub("&rArr;", note_line)
        note_line = Plugin.left_arrow_regex.sub("&lArr;", note_line)
        note_line = Plugin.double_arrow_regex.sub("&hArr;", note_line)
        return note_line
