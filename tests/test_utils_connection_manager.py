""" Testing PluginManager Class
"""

import unittest
from mock import MagicMock, patch
from ashaw_notes.utils.connection_manager import ConnectionManager


class ConnectionManagerTests(unittest.TestCase):
    """Unit Testing ConnectionManager"""

    @patch('ashaw_notes.utils.configuration.load_config')
    def test_load_plugins_single(self, load_config):
        """Verifies process_note is properly functioning"""
        mock_config = MagicMock()
        mock_config.get.return_value = 'local_notes'
        load_config.return_value = mock_config
        modules = ConnectionManager().load_connectors()

        self.assertEqual(1, len(modules))
        self.assertEqual(
            'ashaw_notes.connectors.local_notes',
            modules[0].__name__
        )

    @patch('ashaw_notes.utils.configuration.load_config')
    def test_load_plugins_multiple(self, load_config):
        """Verifies process_note is properly functioning"""
        mock_config = MagicMock()
        mock_config.get.return_value = 'redis_notes, local_notes'
        load_config.return_value = mock_config
        modules = ConnectionManager().load_connectors()

        self.assertEqual(2, len(modules))
        self.assertEqual(
            'ashaw_notes.connectors.redis_notes',
            modules[0].__name__
        )
        self.assertEqual(
            'ashaw_notes.connectors.local_notes',
            modules[1].__name__
        )

    def test_get_primary_connector(self):
        """Verifies get_primary_connector is properly functioning"""
        manager = ConnectionManager()
        manager.connectors = [1, 2, 3, 4]
        self.assertEqual(1, manager.get_primary_connector())
