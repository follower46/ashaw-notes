""" Testing Local Notes Module
"""

import unittest
from mock import MagicMock, mock_open, patch, call
from ddt import ddt, data, unpack
from ashaw_notes.connectors import local_notes
from ashaw_notes.utils.search import get_search_request


@ddt
class LocalNotesTests(unittest.TestCase):
    """Unit Testing Local Notes"""

    @unpack
    @data(
        ('local_notes', True),
        ('redis_notes, local_notes', True),
        ('redis_notes', False),
    )
    @patch('ashaw_notes.utils.configuration.load_config')
    def test_is_enabled(self, string, expectation, load_config):
        """Verifies is_enabled is properly functioning"""

        mock_config = MagicMock()
        mock_config.get.return_value = string
        load_config.return_value = mock_config

        self.assertEqual(expectation, local_notes.is_enabled())

        mock_config.get.assert_called_once_with('base_config', 'data_backends')


    @patch('ashaw_notes.connectors.local_notes.add_local_note')
    def test_save_note(self, add_local_note):
        """Verifies save_note is properly functioning"""
        local_notes.save_note(12345, "test note")
        add_local_note.assert_called_once_with(12345, "test note")


    @patch('ashaw_notes.connectors.local_notes.delete_local_note')
    def test_delete_note(self, delete_local_note):
        """Verifies delete_note is properly functioning"""
        local_notes.delete_note(12345)
        delete_local_note.assert_called_once_with(12345)


    @patch('ashaw_notes.connectors.local_notes.save_note')
    @patch('ashaw_notes.connectors.local_notes.delete_local_note')
    def test_update_note(self, delete_local_note, save_note):
        """Verifies update_note is properly functioning"""
        local_notes.update_note(12345, 23456, "test note")
        delete_local_note.assert_called_once_with(12345)
        save_note.assert_called_once_with(23456, "test note")


    @patch('ashaw_notes.utils.search.get_search_request')
    @patch('ashaw_notes.connectors.local_notes.find_local_notes')
    def test_find_notes(self, find_local_notes, get_search_request):
        """Verifies update_note is properly functioning"""
        local_notes.find_notes(["test note"])
        get_search_request.assert_called_once_with(["test note"])
        find_local_notes.assert_called_once()


    def test_get_common_words(self):
        """Verifies get_common_words is properly functioning"""
        self.assertEqual(
            set(),
            local_notes.get_common_words())


    @patch('ashaw_notes.connectors.local_notes.write_line')
    @patch('ashaw_notes.connectors.local_notes.write_header')
    @patch('ashaw_notes.connectors.local_notes.is_header_found')
    @patch('ashaw_notes.connectors.local_notes.get_notes_file_location')
    @patch('builtins.open')
    @patch('os.path.isfile')
    @patch('ashaw_notes.connectors.local_notes.backup_notes')
    def test_add_local_note(self,
                            backup_notes,
                            isfile,
                            mopen,
                            get_notes_file_location,
                            is_header_found,
                            write_header,
                            write_line):
        """Verifies add_local_note is properly functioning"""
        isfile.return_value = True
        get_notes_file_location.return_value = '/home/user/notes'
        is_header_found.return_value = True
        read_file = MagicMock()
        write_file = MagicMock()
        mopen.side_effect = [read_file, write_file]

        local_notes.add_local_note(1373500800, "testing")

        backup_notes.assert_called_once()
        write_header.assert_not_called()
        write_line.assert_called_once_with(write_file, '[Thu Jul 11 00:00:00 2013] testing')
        read_file.close.assert_called_once()
        write_file.close.assert_called_once()


    @patch('ashaw_notes.connectors.local_notes.write_line')
    @patch('ashaw_notes.connectors.local_notes.write_header')
    @patch('ashaw_notes.connectors.local_notes.is_header_found')
    @patch('ashaw_notes.connectors.local_notes.get_notes_file_location')
    @patch('builtins.open')
    @patch('os.path.isfile')
    @patch('ashaw_notes.connectors.local_notes.backup_notes')
    def test_add_local_note_with_header(self,
                                        backup_notes,
                            isfile,
                                        mopen,
                                        get_notes_file_location,
                                        is_header_found,
                                        write_header,
                                        write_line):
        """Verifies add_local_note is properly functioning"""
        isfile.return_value = True
        get_notes_file_location.return_value = '/home/user/notes'
        is_header_found.return_value = False
        read_file = MagicMock()
        write_file = MagicMock()
        mopen.side_effect = [read_file, write_file]

        local_notes.add_local_note(1373500800, "testing")

        backup_notes.assert_called_once()
        write_header.assert_called_once_with(write_file, '2013-07-11T00:00:00')
        write_line.assert_called_once_with(write_file, '[Thu Jul 11 00:00:00 2013] testing')
        read_file.close.assert_called_once()
        write_file.close.assert_called_once()


    @patch('ashaw_notes.connectors.local_notes.get_notes_file_location')
    @patch('builtins.open')
    @patch('ashaw_notes.connectors.local_notes.backup_notes')
    def test_delete_local_note(self,
                               backup_notes,
                               mopen,
                               get_notes_file_location):
        """Verifies delete_local_note is properly functioning"""
        get_notes_file_location.return_value = '/home/user/notes'
        read_file = MagicMock()
        write_file = MagicMock()
        read_file.readlines.return_value = [
            '[Thu Jul 10 23:59:00 2013] not it',
            '[Thu Jul 11 00:00:00 2013] Im it',
            '[Thu Jul 11 00:00:01 2013] not it',
        ]
        write_file.write.return_value = True
        mopen.side_effect = [read_file, write_file]

        local_notes.delete_local_note(1373500800)

        backup_notes.assert_called_once()
        self.assertListEqual(
            write_file.write.mock_calls,
            [
                call('[Thu Jul 10 23:59:00 2013] not it'),
                call('[Thu Jul 11 00:00:01 2013] not it'),
            ]
        )
        write_file.close.assert_called_once()


    @patch('builtins.open', new_callable=mock_open)
    @patch('ashaw_notes.connectors.local_notes.get_notes_file_location')
    def test_find_local_notes(self, get_notes_file_location, mopen):
        """Verifies get_notes_file_location is properly functioning"""
        get_notes_file_location.return_value = '/home/user/notes'
        mopen.return_value = [
            '[Thu Jul 11 00:00:00 2013] haystack 2',
            '[Thu Jul 11 00:00:01 2013] haystack 1',
            '[Thu Jul 11 00:00:02 2013] needle',
            '[Thu Jul 11 00:00:03 2013] haystack 3',
            '[Thu Jul 11 00:00:04 2013] needle...not.',
            '[Thu Jul 11 00:00:05 2013] needle number 2',
        ]
        request = get_search_request(['needle', '!not'])
        filtered_notes = local_notes.find_local_notes(request)
        self.assertListEqual(
            [(1373500802, 'needle'), (1373500805, 'needle number 2')],
            filtered_notes)

    @patch('ashaw_notes.utils.configuration.load_config')
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
    @patch('ashaw_notes.utils.configuration.load_config')
    def test_use_backup(self, enabled, expectation, load_config):
        """Verifies use_backup is properly functioning"""

        mock_config = MagicMock()
        mock_config.get.return_value = enabled
        load_config.return_value = mock_config

        self.assertEqual(expectation, local_notes.use_backup())

        mock_config.get.assert_called_once_with('local_notes', 'create_backup')


    @patch('shutil.copyfile')
    @patch('ashaw_notes.connectors.local_notes.use_backup')
    def test_backup_notes_disabled(self, use_backup, copyfile):
        """Verifies backup_notes doesn't run if disabled"""
        use_backup.return_value = False
        local_notes.backup_notes()

        use_backup.assert_called_once()
        copyfile.get.assert_not_called()


    @patch('shutil.copyfile')
    @patch('os.path.isfile')
    @patch('ashaw_notes.connectors.local_notes.use_backup')
    @patch('ashaw_notes.connectors.local_notes.get_notes_file_location')
    def test_backup_notes_enabled(self, get_notes_file_location, use_backup, isfile, copyfile):
        """Verifies backup_notes is properly functioning"""
        use_backup.return_value = True
        isfile.return_value = True
        get_notes_file_location.return_value = '/home/user/note'
        local_notes.backup_notes()

        use_backup.assert_called_once()
        copyfile.assert_called_once_with(
            '/home/user/note',
            '/home/user/note.bak'
        )


    @patch('shutil.copyfile')
    @patch('ashaw_notes.connectors.local_notes.use_backup')
    def test_restore_from_backup_disabled(self, use_backup, copyfile):
        """Verifies restore_from_backup doesn't run if disabled"""
        use_backup.return_value = False
        local_notes.restore_from_backup()

        use_backup.assert_called_once()
        copyfile.get.assert_not_called()


    @patch('shutil.copyfile')
    @patch('ashaw_notes.connectors.local_notes.use_backup')
    @patch('ashaw_notes.connectors.local_notes.get_notes_file_location')
    def test_backup_notes(self, get_notes_file_location, use_backup, copyfile):
        """Verifies restore_from_backup is properly functioning"""
        use_backup.return_value = True
        get_notes_file_location.return_value = '/home/user/note'
        local_notes.restore_from_backup()

        use_backup.assert_called_once()
        copyfile.assert_called_once_with(
            '/home/user/note.bak',
            '/home/user/note'
        )


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
