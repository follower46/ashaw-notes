""" Date Handler Module
"""
import dateparser
from ashaw_notes.plugins import base_plugin

class Plugin(base_plugin.Plugin):
    """Date Handler Plugin Class"""

    def process_search_request(self, search_request):
        """Updates search request based on plugin parameters"""
        for term in search_request.inclusion_terms:
            date = dateparser.parse(term)
            if date:
                search_request.inclusion_terms.remove(term)
                search_request.date = date
        return search_request
