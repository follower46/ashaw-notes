""" Testing Search Module
"""

import unittest
from mock import MagicMock, patch, call
from ddt import ddt, data, unpack
from ashaw_notes.scripts import quicknote


@ddt
class QuicknoteTests(unittest.TestCase):
    """Unit Testing Quicknote"""

    @patch('ashaw_notes.scripts.quicknote.write_note')
    @patch('ashaw_notes.scripts.quicknote.take_note')
    @patch('ashaw_notes.scripts.quicknote.setup_auto_complete')
    @patch('ashaw_notes.scripts.quicknote.import_connectors')
    @patch('ashaw_notes.scripts.quicknote.add_parent_modules')
    def test_run_quicknote(self,
                           add_parent_modules,
                           import_connectors,
                           setup_auto_complete,
                           take_note,
                           write_note):
        """Verifies run_quicknote is properly functioning"""
        import_connectors.return_value = [1, 2, 3]
        take_note.return_value = "testing"
        quicknote.run_quicknote('ashaw_notes/scripts/quicknote.py')
        add_parent_modules.assert_called_once_with('ashaw_notes/scripts/quicknote.py')
        import_connectors.assert_called_once()
        setup_auto_complete.assert_called_once_with([1, 2, 3])
        take_note.assert_called_once()
        write_note.assert_called_once_with("testing", [1, 2, 3])


    @patch('sys.path')
    @patch('os.path')
    def test_add_parent_modules(self, os_path, sys_path):
        """Verifies add_parent_modules is properly functioning"""
        os_path.abspath.return_value = '/home/user/github_clone/ashaw_notes/scripts'
        os_path.dirname.side_effect = [
            'ashaw_notes/scripts',
            '/home/user/github_clone/ashaw_notes',
            '/home/user/github_clone',
        ]
        quicknote.add_parent_modules('ashaw_notes/scripts/quicknote.py')
        sys_path.append.assert_called_once_with('/home/user/github_clone')


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
        call_argument = only_call[1][0]
        call_argument.sort()
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


    @unpack
    @data(
        ('test', 'today: test'),
        ('lunch', 'lunch'),
        ('todo: fix unit tests', 'todo: fix unit tests'),
        ('todone[0]: watched', 'todone[0]: watched'),
        ('cal: 200', 'cal: 200'),
    )
    def test_process_note(self, note, expectation):
        """Verifies process_note is properly functioning"""
        self.assertEqual(
            expectation,
            quicknote.process_note(note)
        )
