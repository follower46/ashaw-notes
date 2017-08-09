""" Testing Local Notes Module
"""

import unittest
from connectors import local_notes
from mock import MagicMock, patch
from ddt import ddt, data, unpack


@ddt
class LocalNotesTests(unittest.TestCase):
    """Unit Testing Local Notes"""

    @unpack
    @data(
        ('local_notes', True),
        ('redis_notes, local_notes', True),
        ('redis_notes', False),
    )
    @patch('utils.configuration.load_config')
    def test_is_enabled(self, string, expectation, load_config):
        """Verifies is_enabled is properly functioning"""

        mock_config = MagicMock()
        mock_config.get.return_value = string
        load_config.return_value = mock_config

        self.assertEqual(expectation, local_notes.is_enabled())


    @patch('connectors.local_notes.add_local_note')
    def test_save_note(self, add_local_note):
        """Verifies save_note is properly functioning"""
        local_notes.save_note(12345, "test note")
        add_local_note.assert_called_once_with(12345, "test note")


    @patch('connectors.local_notes.delete_local_note')
    def test_delete_note(self, delete_local_note):
        """Verifies delete_note is properly functioning"""
        local_notes.delete_note(12345)
        delete_local_note.assert_called_once_with(12345)


    @patch('connectors.local_notes.save_note')
    @patch('connectors.local_notes.delete_local_note')
    def test_update_note(self, delete_local_note, save_note):
        """Verifies update_note is properly functioning"""
        local_notes.update_note(12345, 23456, "test note")
        delete_local_note.assert_called_once_with(12345)
        save_note.assert_called_once_with(23456, "test note")
