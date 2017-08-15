"""Plugin Manager Module
"""
import importlib
import ashaw_notes.utils.configuration


class PluginManager:
    """Plugin Manager Class"""
    plugins = None

    def __init__(self):
        if not self.plugins:
            self.load_plugins()

    def load_plugins(self):
        """Returns all enabled plugins"""
        self.plugins = []
        config = ashaw_notes.utils.configuration.load_config()
        plugin_names = config.get('base_config', 'plugins')
        for plugin_name in [name.strip() for name in plugin_names.split(',')]:
            module = importlib.import_module(
                "ashaw_notes.plugins.%s" % plugin_name)
            self.plugins.append(module.Plugin())
        return self.get_plugins()

    def get_plugins(self):
        """Simple getter"""
        return self.plugins

    def bypass_today(self, note):
        """Checks if note should bypass today string"""
        for plugin in self.plugins:
            if plugin.bypass_today:
                if plugin.is_plugin_note(note):
                    return True
        return False

    def process_search_request(self, search_request):
        """Allows enabled plugins to modify search request"""
        for plugin in self.plugins:
            plugin.process_search_request(search_request)
        return search_request
