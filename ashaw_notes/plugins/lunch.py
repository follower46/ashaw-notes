""" Lunch Plugin Module
"""
import re
from ashaw_notes.plugins import base_plugin


class Plugin(base_plugin.Plugin):
    """Lunch Plugin Class"""
    bypass_today = True
    regex = re.compile(r'^((s)?lunch)$')

    def is_plugin_note(self, note):
        """Verifies note relates to plugin"""
        return bool(self.regex.match(note))

    def process_input(self, note):
        """Handle note input"""
        return note

    def format_note_line(self, timestamp, note_line):
        """Allows enabled plugins to modify note display"""
        note_line = Plugin.regex.sub(
            "<table style='width:100%;font-weight:bold;background-color:#511;" \
            "color:#fff;text-align:center;'>" \
            r"<tr><td style='width: 100%;'>\1 break</td></tr></table>",
            note_line)
        return note_line
