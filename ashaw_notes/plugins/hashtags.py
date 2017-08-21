""" Hashtags Module
"""
import re
from ashaw_notes.plugins import base_plugin


class Plugin(base_plugin.Plugin):
    """Hashtag Plugin Class"""

    regex = re.compile(r'#([^ ]+)')

    def format_note_line(self, timestamp, note_line):
        """Allows enabled plugins to modify note display"""
        note_line = Plugin.regex.sub(
            r"<a href='filter:#\1' style='color:#A6E22E;text-decoration:underline;'>#\1</a>",
            note_line)
        return note_line
