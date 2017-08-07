""" Testing Configuration Modules
"""

import unittest
import configparser
from utils import configuration
from mock import patch


class ConfigurationTests(unittest.TestCase):
    """Unit Testing Configuration"""

    def test_config_defaulted_empty(self):
        """Validates that local config global isn't set on empty load"""
        assert configuration.__local_config__ is None


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
        """Validates things"""
        isfile.return_value(True)
        self.assertEqual(configuration.get_notes_file_location(), 'notes-local.config')


    @patch('os.path.isfile')
    def test_get_notes_file_location_failure(self, isfile):
        """Validates things"""
        isfile.return_value(False)
        with self.assertRaises(Exception) as context:
            configuration.get_notes_file_location()
            self.assertTrue('Config not found. Please verify configuration deployment' 
                            in context.exception)
