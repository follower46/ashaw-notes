""" Wiki Module
"""
import re
from ashaw_notes.plugins import base_plugin


class Plugin(base_plugin.Plugin):
    """Wikipedia Plugin Class"""

    regex = re.compile(r'(wiki:(?P<term>[^ \n]+))')
    regex_url = re.compile(r'(https://en.wikipedia.org/wiki/(?P<term>[^ \n]+))')

    def format_note_line(self, timestamp, note_line):
        """Allows enabled plugins to modify note display"""
        note_line = Plugin.regex.sub(
            self.url_injection,
            note_line)
        note_line = Plugin.regex_url.sub(
            self.url_injection,
            note_line)
        return note_line

    def url_injection(self, match):
        term = match.group('term')
        display_term = term.replace("_", " ").replace("#", " - ")
        return "<a style='color:#66D9B1;' " \
        "href='http://en.wikipedia.org/wiki/%s'>%s</a>" % (term, display_term)
