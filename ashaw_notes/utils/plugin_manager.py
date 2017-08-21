"""Plugin Manager Module
"""
import importlib
import ashaw_notes.utils.configuration


class PluginManager:
    """Plugin Manager Class"""
    plugins = None
    logger = ashaw_notes.utils.configuration.get_logger()

    def __init__(self):
        if not PluginManager.plugins:
            self.logger.debug("Loading Plugins")
            self.load_plugins()
            self.logger.debug("Plugins Loaded")

    def load_plugins(self):
        """Returns all enabled plugins"""
        PluginManager.plugins = []
        config = ashaw_notes.utils.configuration.load_config()
        plugin_names = config.get('base_config', 'plugins')
        for plugin_name in [name.strip() for name in plugin_names.split(',')]:
            module = importlib.import_module(
                "ashaw_notes.plugins.%s" % plugin_name)
            PluginManager.plugins.append(module.Plugin())
        return self.get_plugins()

    def get_plugins(self):
        """Simple getter"""
        return PluginManager.plugins

    def bypass_today(self, note):
        """Checks if note should bypass today string"""
        for plugin in PluginManager.plugins:
            if plugin.bypass_today:
                if plugin.is_plugin_note(note):
                    return True
        return False

    def process_search_request(self, search_request):
        """Allows enabled plugins to modify search request"""
        for plugin in PluginManager.plugins:
            self.logger.debug("Plugin Processing Search Request: %s", plugin.__class__)
            plugin.process_search_request(search_request)
            self.logger.debug("Processed")
        return search_request

    def format_note_line(self, timestamp, note_line):
        """Allows enabled plugins to modify note display"""
        if not note_line:
            return note_line

        for plugin in PluginManager.plugins:
            note_line = plugin.format_note_line(timestamp, note_line)
        return note_line
