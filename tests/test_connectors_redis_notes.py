""" Testing Local Notes Module
"""

import unittest
from connectors import redis_notes
from mock import MagicMock, patch
from ddt import ddt, data, unpack


@ddt
class LocalNotesTests(unittest.TestCase):
    """Unit Testing Local Notes"""

    @unpack
    @data(
        ('redis_notes', True),
        ('redis_notes, local_notes', True),
        ('local_notes', False),
    )
    @patch('utils.configuration.load_config')
    def test_is_enabled(self, string, expectation, load_config):
        """Verifies is_enabled is properly functioning"""

        mock_config = MagicMock()
        mock_config.get.return_value = string
        load_config.return_value = mock_config

        self.assertEqual(expectation, redis_notes.is_enabled())


    @patch('connectors.redis_notes.add_redis_note')
    def test_save_note(self, add_redis_note):
        """Verifies save_note is properly functioning"""
        redis_notes.save_note(12345, "test note")
        add_redis_note.assert_called_once_with(12345, "test note")
