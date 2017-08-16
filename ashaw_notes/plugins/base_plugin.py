""" Lunch Plugin Module
"""


class Plugin:
    """Plugin Class"""
    bypass_today = False

    def __init__(self):
        pass

    def is_plugin_note(self, note):
        """Verifies note relates to plugin"""
        return False

    def process_input(self, note):
        """Handle note input"""
        return note

    def process_search_request(self, search_request):
        """Updates search request based on plugin parameters"""
        return search_request
