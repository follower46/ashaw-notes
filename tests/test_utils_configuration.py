""" Testing Configuration Module
"""

import unittest
import configparser
from mock import MagicMock, patch
from ashaw_notes.utils import configuration


class ConfigurationTests(unittest.TestCase):
    """Unit Testing Configuration"""

    def test_config_load(self):
        """Validates that global config is actually set"""
        configuration.__local_config__ = None
        configuration.load_config()
        self.assertTrue(configuration.__local_config__ is not None)


    def test_config_multiple_load(self):
        """Validates that successive load_config calls does reload config object"""
        configuration.load_config()
        config = configuration.__local_config__
        configuration.load_config()
        self.assertEqual(configuration.__local_config__, config)


    def test_reload_config(self):
        """Validates reload_configs blows away config global"""
        config = configparser.ConfigParser()
        configuration.__local_config__ = config
        configuration.reload_config()
        self.assertNotEqual(configuration.__local_config__, config)


    @patch('os.path.isfile')
    def test_get_notes_file_location(self, isfile):
        """Validates local config wins if found"""
        isfile.return_value = True
        self.assertEqual(configuration.get_notes_file_location(), 'notes-local.config')


    @patch('os.path.isfile')
    def test_config_missing(self, isfile):
        """Checks for proper exception handling"""
        isfile.return_value = False
        with self.assertRaises(Exception) as context:
            configuration.get_notes_file_location()
            self.assertTrue('Config not found. Please verify configuration deployment'
                            in context.exception)


    @patch('ashaw_notes.utils.configuration.load_config')
    def test_get_connection_modules_single(self, load_config):
        """Verifies process_note is properly functioning"""
        mock_config = MagicMock()
        mock_config.get.return_value = 'local_notes'
        load_config.return_value = mock_config
        connectors = configuration.get_connection_modules()

        self.assertEqual(1, len(connectors))
        self.assertEqual(
            'ashaw_notes.connectors.local_notes',
            connectors[0].__name__
        )


    @patch('ashaw_notes.utils.configuration.load_config')
    def test_get_connection_modules_multiple(self, load_config):
        """Verifies process_note is properly functioning"""
        mock_config = MagicMock()
        mock_config.get.return_value = 'redis_notes, local_notes'
        load_config.return_value = mock_config
        connectors = configuration.get_connection_modules()

        self.assertEqual(2, len(connectors))
        self.assertEqual(
            'ashaw_notes.connectors.redis_notes',
            connectors[0].__name__
        )
        self.assertEqual(
            'ashaw_notes.connectors.local_notes',
            connectors[1].__name__
        )


    @patch('ashaw_notes.utils.configuration.get_connection_modules')
    def test_get_primary_connection_module(self, get_connection_modules):
        """Verifies get_primary_connection_module is properly functioning"""
        get_connection_modules.return_value = [1, 2, 3]
        self.assertEqual(1, configuration.get_primary_connection_module())
