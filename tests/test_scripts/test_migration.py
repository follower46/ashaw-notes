""" Testing Migration Module
"""

import unittest
from mock import MagicMock, patch, call
from ashaw_notes.utils.connection_manager import ConnectionManager
from ashaw_notes.scripts import migration


class MigrationTests(unittest.TestCase):
    """Unit Testing Migration"""

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
        migration.add_parent_modules('ashaw_notes/scripts/quicknote.py')
        sys_path.append.assert_called_once_with('/home/user/github_clone')

    @patch('ashaw_notes.scripts.migration.migrate_notes')
    @patch.object(ConnectionManager, 'load_connector')
    @patch('ashaw_notes.scripts.migration.add_parent_modules')
    def test_run_migrations_no_parameters(
            self,
            add_parent_modules,
            load_connector,
            migrate_notes):
        """Verifies run_migrations blocks call with no parameters"""
        migration.run_migrations(['/ashaw_notes/scripts/migration.py'])
        add_parent_modules.called_once_with(
            '/ashaw_notes/scripts/migration.py')
        load_connector.assert_not_called()
        migrate_notes.assert_not_called()

    @patch('ashaw_notes.scripts.migration.migrate_notes')
    @patch.object(ConnectionManager, 'load_connectors')
    @patch.object(ConnectionManager, 'load_connector')
    @patch('ashaw_notes.scripts.migration.add_parent_modules')
    def test_run_migrations_one_parameters(
            self,
            add_parent_modules,
            load_connector,
            load_connectors,
            migrate_notes):
        """Verifies run_migrations blocks call with only one parameter"""
        load_connector.return_value = 1
        load_connectors.return_value = True
        migration.run_migrations(
            ['/ashaw_notes/scripts/migration.py', 'local_notes'])
        add_parent_modules.called_once_with(
            '/ashaw_notes/scripts/migration.py')
        load_connector.assert_called_once_with('local_notes')
        migrate_notes.assert_not_called()

    @patch('ashaw_notes.scripts.migration.migrate_notes')
    @patch.object(ConnectionManager, 'load_connectors')
    @patch.object(ConnectionManager, 'load_connector')
    @patch('ashaw_notes.scripts.migration.add_parent_modules')
    def test_run_migrations_success(
            self,
            add_parent_modules,
            load_connector,
            load_connectors,
            migrate_notes):
        """Verifies run_migrations is properly functioning"""
        load_connector.side_effect = ['source', 'target']
        load_connectors.return_value = True
        migration.run_migrations([
            '/ashaw_notes/scripts/migration.py',
            'local_notes',
            'redis_notes'
        ])
        add_parent_modules.called_once_with(
            '/ashaw_notes/scripts/migration.py')
        load_connector.assert_has_calls(
            [call('local_notes'), call('redis_notes')])
        migrate_notes.assert_called_once_with('source', 'target')

    def test_migrate_notes(self):
        """Verifies migrate_notes is properly functioning"""
        source = MagicMock()
        source.find_notes.return_value = [
            (0, 'note1'),
            (1, 'note2'),
            (2, 'note3'),
        ]
        target = MagicMock()

        migration.migrate_notes(source, target)

        source.find_notes.assert_called_once_with([])
        target.save_note.assert_has_calls([
            call(0, 'note1'),
            call(1, 'note2'),
            call(2, 'note3'),
        ])
