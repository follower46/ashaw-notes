""" Lunch Plugin Module
"""
import re
from ashaw_notes.plugins import base_plugin

class Plugin(base_plugin.Plugin):
    """Lunch Plugin Class"""
    bypass_today = True
    regex = re.compile(r'^(s)?lunch$')

    def is_plugin_note(self, note):
        """Verifies note relates to plugin"""
        return self.regex.match(note)


    def process_input(self, note):
        """Handle note input"""
        return note
