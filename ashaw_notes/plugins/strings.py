""" String/Quote Module
"""
import re
from ashaw_notes.plugins import base_plugin


class Plugin(base_plugin.Plugin):
    """String Plugin Class"""

    regex = re.compile(r'"([^"]*)"')

    def format_note_line(self, timestamp, note_line):
        """Allows enabled plugins to modify note display"""
        note_line = Plugin.regex.sub(
            r"<span style='color:#E6DB5A'>&quot;\1&quot;</span>",
            note_line)
        return note_line
