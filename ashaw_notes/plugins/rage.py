""" Rage Module
"""
import re
from ashaw_notes.plugins import base_plugin


class Plugin(base_plugin.Plugin):
    """String Plugin Class"""

    rage_regex = re.compile(r'\*\*([^\*]*)\*\*')
    bold_regex = re.compile(r'\*([^\*]*)\*')

    def format_note_line(self, timestamp, note_line):
        """Allows enabled plugins to modify note display"""
        note_line = Plugin.rage_regex.sub(
            r"<span style='color:#c33;font-weight:bold;text-transform:uppercase;'>\1</span>",
            note_line)
        note_line = Plugin.bold_regex.sub(
            r"<span style='color:#ccc;text-shadow:0px 0px 20px #000;font-weight:bold;'>\1</span>",
            note_line)
        return note_line
