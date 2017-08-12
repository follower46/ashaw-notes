"""Plugin Manager Module
"""
import importlib
import ashaw_notes.utils.configuration

class PluginManager:
    """Plugin Class"""
    plugins = None

    def __init__(self):
        self.load_plugins()


    def load_plugins(self):
        """Returns all enabled plugins"""
        self.plugins = []
        plugin_names = ashaw_notes.utils.configuration.load_config().get('base_config', 'plugins')
        for plugin_name in [name.strip() for name in plugin_names.split(',')]:
            module = importlib.import_module("ashaw_notes.plugins.%s" % plugin_name)
            self.plugins.append(module.Plugin())


    def bypass_today(self, note):
        """Checks if note should bypass today string"""
        for plugin in self.plugins:
            if plugin.bypass_today:
                if plugin.is_plugin_note(note):
                    return True
        return False
