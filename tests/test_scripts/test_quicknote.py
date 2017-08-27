""" Testing Quicknote Module
"""

import unittest
from mock import MagicMock, patch, call
from ddt import ddt, data, unpack
from ashaw_notes.utils.connection_manager import ConnectionManager
from ashaw_notes.scripts import quicknote


@ddt
class QuicknoteTests(unittest.TestCase):
    """Unit Testing Quicknote"""

    @patch('ashaw_notes.scripts.quicknote.write_note')
    @patch('ashaw_notes.scripts.quicknote.take_note')
    @patch('ashaw_notes.scripts.quicknote.setup_auto_complete')
    @patch('ashaw_notes.scripts.quicknote.import_connectors')
    def test_run_quicknote(self,
                           import_connectors,
                           setup_auto_complete,
                           take_note,
                           write_note):
        """Verifies run_quicknote is properly functioning"""
        import_connectors.return_value = [1, 2, 3]
        take_note.return_value = "testing"
        quicknote.run()
        import_connectors.assert_called_once()
        setup_auto_complete.assert_called_once_with([1, 2, 3])
        take_note.assert_called_once()
        write_note.assert_called_once_with("testing", [1, 2, 3])

    @patch.object(ConnectionManager, 'load_connectors')
    def test_import_connectors(self, load_connectors):
        """Verifies import_connectors is properly functioning"""
        load_connectors.return_value = [1, 2, 3]
        self.assertListEqual(
            [1, 2, 3],
            quicknote.import_connectors()
        )

    @patch('readline.parse_and_bind')
    @patch('ashaw_notes.scripts.quicknote.Completer')
    def test_setup_auto_complete(self, completer, parse_and_bind):
        """Verifies process_note is properly functioning"""
        module1 = MagicMock()
        module1.get_common_words.return_value = set(['a', 'b', 'c'])
        module2 = MagicMock()
        module2.get_common_words.return_value = set(['c', 'd', 'e'])
        quicknote.setup_auto_complete([module1, module2])

        parse_and_bind.assert_called_once_with('tab: complete')
        self.assertEqual(1, len(completer.mock_calls))
        only_call = completer.mock_calls[0]
        call_argument = sorted(only_call[1][0])
        self.assertListEqual(['a', 'b', 'c', 'd', 'e'], call_argument)

    def test_completer(self):
        """Verifies Completer class is properly functioning"""
        test = quicknote.Completer(['test', 'top', 'tent'])
        self.assertEqual('test ', test.complete('te', 0))
        self.assertEqual('tent ', test.complete('te', 1))
        self.assertEqual(None, test.complete('te', 2))
        self.assertEqual(None, test.complete('p', 2))

    @patch('time.time')
    def test_write_note(self, time):
        """Verifies write_note is properly functioning"""
        time.return_value = 1373500800
        module1 = MagicMock()
        module2 = MagicMock()
        quicknote.write_note("testing", [module1, module2])
        module1.save_note.assert_called_once_with(1373500800, "today: testing")
        module2.save_note.assert_called_once_with(1373500800, "today: testing")

    @patch('builtins.input')
    def test_take_note(self, mock_input):
        quicknote.take_note()
        mock_input.assert_called_once_with("note: ")

    @unpack
    @data(
        ('test', 'today: test'),
        ('lunch', 'lunch'),
        ('todo: fix unit tests', 'todo: fix unit tests'),
        ('todone[0]: watched', 'todone[0]: watched'),
    )
    def test_process_note(self, note, expectation):
        """Verifies process_note is properly functioning"""
        self.assertEqual(
            expectation,
            quicknote.process_note(note)
        )
