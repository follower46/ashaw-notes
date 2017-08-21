""" Date Handler Module
"""
import re
import dateparser
from ashaw_notes.plugins import base_plugin
from ashaw_notes.utils.search import timestamp_to_datestring
import ashaw_notes.utils.configuration


class Plugin(base_plugin.Plugin):
    """Date Handler Plugin Class"""

    logger = ashaw_notes.utils.configuration.get_logger()
    regex = re.compile(r"^today:", re.IGNORECASE)

    def process_search_request(self, search_request):
        """Updates search request based on plugin parameters"""
        for term in search_request.inclusion_terms:
            if term[0:5] != 'date:':
                continue
            date_term = term[5:]
            self.logger.debug("Parsing %s", date_term)
            date = dateparser.parse(date_term)
            self.logger.debug("Date Parsed")
            if date:
                search_request.inclusion_terms.remove(term)
                search_request.date = date
        return search_request

    def format_note_line(self, timestamp, note_line):
        """Allows enabled plugins to modify note display"""
        note_line = Plugin.regex.sub(
            "<span style='color:#A6E22E' title='%s'>today:</span>"
            % timestamp_to_datestring(timestamp),
            note_line)
        return note_line
