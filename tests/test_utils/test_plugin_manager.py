""" Testing PluginManager Class
"""

import unittest
from mock import MagicMock, patch
from ashaw_notes.utils.plugin_manager import PluginManager


class PluginManagerTests(unittest.TestCase):
    """Unit Testing PluginManager"""

    @patch('ashaw_notes.utils.configuration.load_config')
    def test_load_plugins_single(self, load_config):
        """Verifies process_note is properly functioning"""
        mock_config = MagicMock()
        mock_config.get.return_value = 'lunch'
        load_config.return_value = mock_config
        plugins = PluginManager().load_plugins()

        self.assertEqual(1, len(plugins))
        self.assertEqual(
            'ashaw_notes.plugins.lunch',
            plugins[0].__module__
        )

    @patch('ashaw_notes.utils.configuration.load_config')
    def test_load_plugins_multiple(self, load_config):
        """Verifies process_note is properly functioning"""
        mock_config = MagicMock()
        mock_config.get.return_value = 'lunch, todo'
        load_config.return_value = mock_config
        plugins = PluginManager().load_plugins()

        self.assertEqual(2, len(plugins))
        self.assertEqual(
            'ashaw_notes.plugins.lunch',
            plugins[0].__module__
        )
        self.assertEqual(
            'ashaw_notes.plugins.todo',
            plugins[1].__module__
        )

    @patch('ashaw_notes.utils.configuration.load_config')
    def test_bypass_today(self, load_config):
        """Verifies bypass_today is properly functioning"""
        mock_config = MagicMock()
        mock_config.get.return_value = 'lunch, todo'
        load_config.return_value = mock_config

        manager = PluginManager()
        self.assertTrue(manager.bypass_today('lunch'))
        self.assertFalse(manager.bypass_today('flunch'))

    def test_process_search_request(self):
        """Verifies bypass_today is properly functioning"""
        request = MagicMock()
        plugin = MagicMock()

        manager = PluginManager()
        PluginManager.plugins = [plugin]

        self.assertEqual(request, manager.process_search_request(request))
        plugin.process_search_request.assert_called_once_with(request)

    def test_format_note_line(self):
        """Verifies bypass_today is properly functioning"""
        request = MagicMock()
        plugin = MagicMock()
        plugin.format_note_line.return_value = 'An updated string'

        manager = PluginManager()
        PluginManager.plugins = [plugin]

        self.assertEqual(None, manager.format_note_line(1373500800, None))
        self.assertEqual('An updated string', manager.format_note_line(1373500800, 'A string'))
        plugin.process_search_request.format_note_line(1373500800, 'A string')
