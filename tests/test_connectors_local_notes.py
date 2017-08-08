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
        mock_config.get = MagicMock()
        mock_config.get.return_value = string
        load_config.return_value = mock_config

        self.assertEqual(expectation, local_notes.is_enabled())
