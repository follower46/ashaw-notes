""" Testing Configuration Module
"""

import unittest
import configparser
import logzero
from mock import MagicMock, patch, call
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
        self.assertEqual(
            configuration.get_config_location(),
            'notes-local.config')

    @patch('os.path.isfile')
    def test_config_missing(self, isfile):
        """Checks for proper exception handling"""
        isfile.return_value = False
        with self.assertRaises(Exception) as context:
            configuration.get_config_location()
            self.assertTrue(
                'Config not found. Please verify configuration deployment' in context.exception)

    @patch.object(logzero, 'logfile')
    @patch('ashaw_notes.utils.configuration.load_config')
    def test_get_logger(self, load_config, logfile):
        """Verifies get_logger is properly functioning"""
        config = MagicMock()
        config.get.side_effect = [
            '/tmp/mylogs.log',
            '1e7',
            '5',
        ]
        load_config.return_value = config
        logger = configuration.get_logger()
        load_config.assert_called_once()
        config.get.assert_has_calls([
            call('logging', 'location'),
            call('logging', 'max_bytes'),
            call('logging', 'backup_count'),
        ])
        logfile.assert_called_once_with(
            '/tmp/mylogs.log',
            maxBytes=1e7,
            backupCount=5,
        )
        self.assertEqual("<class 'logging.Logger'>", str(logger.__class__))
