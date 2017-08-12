""" Todo Plugin Module
"""
import re
from ashaw_notes.plugins import base_plugin

class Plugin(base_plugin.Plugin):
    """Todo Plugin Class"""
    bypass_today = True
    regex = re.compile(r'^todo(ne\[[0-9]*\])?:')

    def is_plugin_note(self, note):
        """Verifies note relates to plugin"""
        return bool(self.regex.match(note))


    def process_input(self, note):
        """Handle note input"""
        return note
