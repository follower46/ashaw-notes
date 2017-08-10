""" Testing Local Notes Module
"""

import unittest
from connectors import local_notes
from mock import MagicMock, patch, call
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

        mock_config.get.assert_called_once_with('base_config', 'data_backends')


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


    @patch('utils.search.get_search_request')
    @patch('connectors.local_notes.find_local_notes')
    def test_find_notes(self, find_local_notes, get_search_request):
        """Verifies update_note is properly functioning"""
        local_notes.find_notes(["test note"])
        get_search_request.assert_called_once_with(["test note"])
        find_local_notes.assert_called_once()


    @patch('utils.configuration.load_config')
    def test_get_notes_file_location(self, load_config):
        """Verifies get_notes_file_location is properly functioning"""

        mock_config = MagicMock()
        mock_config.get.return_value = '/home/user/note'
        load_config.return_value = mock_config

        self.assertEqual('/home/user/note', local_notes.get_notes_file_location())

        mock_config.get.assert_called_once_with('local_notes', 'location')


    @unpack
    @data(
        (True, True),
        (False, False),
    )
    @patch('utils.configuration.load_config')
    def test_use_backup(self, enabled, expectation, load_config):
        """Verifies use_backup is properly functioning"""

        mock_config = MagicMock()
        mock_config.get.return_value = enabled
        load_config.return_value = mock_config

        self.assertEqual(expectation, local_notes.use_backup())

        mock_config.get.assert_called_once_with('local_notes', 'create_backup')


    @unpack
    @data(
        ([], 1373500800, False),
        (['not in here'], 1373500800, False),
        (['note', '2013-07-11T00:00:00', '=========='], 1373500800, True),
    )
    def test_is_header_found(self, file, timestamp, expectation):
        """Verifies is_header_found is properly functioning"""
        self.assertEqual(
            expectation,
            local_notes.is_header_found(file, timestamp)
        )


    def test_get_date_header(self):
        """Verifies get_date_header is properly functioning"""
        header = local_notes.get_date_header(1373500800)
        self.assertEqual('2013-07-11T00:00:00', header)


    def test_write_header(self):
        """Verifies write_header is properly functioning"""
        file = MagicMock()
        local_notes.write_header(file, "My Header")

        file.write.assert_has_calls([
            call("==========\n"),
            call("My Header\n")
        ])


    def test_build_note_line(self):
        """Verifies build_note_line is properly functioning"""
        line = local_notes.build_note_line(
            1373500800,
            "today: testing"
        )

        self.assertEqual(
            '[Thu Jul 11 00:00:00 2013] today: testing',
            line
        )


    @unpack
    @data(
        ('[Thu Jul 11 00:00:00 2013] today: testing', (
            'Thu Jul 11 00:00:00 2013', 'today: testing'
        )),
        ('[Thu Jul 11 00:00:00 2013] today: [Thu Jul 11 00:00:00 2013]', (
            'Thu Jul 11 00:00:00 2013', 'today: [Thu Jul 11 00:00:00 2013]'
        )),
        ('bad line', (None, None)),
    )
    def test_parse_note_line(self, line, expectation):
        """Verifies parse_note_line is properly functioning"""
        self.assertEqual(
            expectation,
            local_notes.parse_note_line(line)
        )


    def test_write_line(self):
        """Verifies write_line is properly functioning"""
        line = "[Thu Jul 11 00:00:00 2013] today: testing"
        file = MagicMock()
        local_notes.write_line(file, line)

        file.write.assert_called_once_with("%s\n" % line)
