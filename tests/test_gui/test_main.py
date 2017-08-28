""" Testing Arrows Module
"""

import unittest
import logging
import PyQt5.QtWidgets
from mock import MagicMock, patch, call
from ddt import ddt, data, unpack
import ashaw_notes.utils.search as search

from ashaw_notes.gui import main as qt


@ddt
class PluginTests(unittest.TestCase):
    """Unit Testing Plugin"""

    def setUp(self):
        """Setup for logging."""
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Stubbed teardown."""
        pass

    @patch('sys.exit')
    @patch.object(PyQt5.QtWidgets.QApplication, 'exec_')
    @patch.object(qt.App, '__init__')
    @patch.object(PyQt5.QtWidgets.QApplication, '__init__')
    def test_run(self, qapp_init, app_init, app_exec, exit):
        """Verifies run is properly functioning"""
        qapp_init.return_value = None
        app_init.return_value = None
        qt.run()
        qapp_init.assert_called_once()
        app_init.assert_called_once()
        app_exec.assert_called_once()
        exit.assert_called_once()

    @patch.object(qt.App, 'main_program_loop')
    @patch('ashaw_notes.gui.main.timestamp_to_datestring')
    @patch('ashaw_notes.gui.main.get_logger')
    @patch('ashaw_notes.gui.main.PluginManager')
    @patch('ashaw_notes.gui.main.ConnectionManager')
    @patch('builtins.super')
    def test_app_init(self, mock_super, cm, pm, get_logger, t_to_d, loop):
        """Verifies App::__init__ is properly functioning"""
        cm.return_value = MagicMock()
        pm.return_value = MagicMock()
        get_logger.return_value = MagicMock()

        app = qt.App()
        mock_super.assert_called_once()
        self.assertEqual(app.connection_manager, cm.return_value)
        self.assertEqual(app.plugin_manager, pm.return_value)
        self.assertEqual(app.logger, get_logger.return_value)
        self.assertEqual(app.timestamp, t_to_d)
        loop.assert_called_once()

    @patch.object(qt.App, 'init_interface')
    @patch.object(qt.App, '__init__')
    def test_main_program_loop_success(self, app_init, init_interface):
        """Verifies App::main_program_loop is properly functioning"""
        app_init.return_value = None
        app = qt.App()
        app.main_program_loop()
        init_interface.assert_called_once()

    @patch.object(PyQt5.QtWidgets.QMessageBox, 'warning')
    @patch.object(qt.App, 'init_interface')
    @patch.object(qt.App, '__init__')
    def test_main_program_loop_single_failure(self, app_init, init_interface, warning):
        """Verifies App::main_program_loop is properly functioning"""
        app_init.return_value = None
        init_interface.side_effect = [Exception("oops"), None]
        warning.return_value = PyQt5.QtWidgets.QMessageBox.Retry
        app = qt.App()
        app.main_program_loop()
        warning.assert_called_once_with(
            app,
            'Notes Error Occured',
            'oops',
            PyQt5.QtWidgets.QMessageBox.Retry | PyQt5.QtWidgets.QMessageBox.Cancel,
            PyQt5.QtWidgets.QMessageBox.Retry)
        self.assertEqual(
            [call(), call()],
            init_interface.mock_calls
        )

    @patch.object(PyQt5.QtWidgets.QMessageBox, 'warning')
    @patch.object(qt.App, 'init_interface')
    @patch.object(qt.App, '__init__')
    def test_main_program_loop_single_cancel(self, app_init, init_interface, warning):
        """Verifies App::main_program_loop is properly functioning"""
        app_init.return_value = None
        init_interface.side_effect = [Exception("oops"), None]
        warning.return_value = PyQt5.QtWidgets.QMessageBox.Cancel
        app = qt.App()
        app.main_program_loop()
        warning.assert_called_once_with(
            app,
            'Notes Error Occured',
            'oops',
            PyQt5.QtWidgets.QMessageBox.Retry | PyQt5.QtWidgets.QMessageBox.Cancel,
            PyQt5.QtWidgets.QMessageBox.Retry)

        init_interface.assert_called_once()
