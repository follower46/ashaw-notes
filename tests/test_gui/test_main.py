""" Testing Arrows Module
"""

import unittest
import PyQt5.QtWidgets
from mock import MagicMock, patch, call
from ddt import ddt, data, unpack
import ashaw_notes.utils.search as search

from ashaw_notes.gui import main as qt


@ddt
class PluginTests(unittest.TestCase):
    """Unit Testing Plugin"""

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
