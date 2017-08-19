""" Date Handler Module
"""
import dateparser
from ashaw_notes.plugins import base_plugin
import ashaw_notes.utils.configuration


class Plugin(base_plugin.Plugin):
    """Date Handler Plugin Class"""

    logger = ashaw_notes.utils.configuration.get_logger()

    def process_search_request(self, search_request):
        """Updates search request based on plugin parameters"""
        for term in search_request.inclusion_terms:
            if term[0:5] != 'date:':
                continue
            dateTerm = term[5:]
            self.logger.debug("Parsing %s", dateTerm)
            date = dateparser.parse(dateTerm)
            self.logger.debug("Date Parsed")
            if date:
                search_request.inclusion_terms.remove(term)
                search_request.date = date
        return search_request
