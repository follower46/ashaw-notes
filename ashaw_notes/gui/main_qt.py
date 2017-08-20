""" Main Notes UI
"""
import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtWidgets import QPushButton, QTextEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt


class App(QMainWindow):
    """QT Application"""

    def __init__(self):
        super().__init__()
        self.title = 'Notes'
        self.left = 10
        self.top = 10
        self.width = 720
        self.height = 380
        self.add_parent_modules(sys.argv[0])

        from ashaw_notes.utils.connection_manager import ConnectionManager
        from ashaw_notes.utils.configuration import get_logger
        from ashaw_notes.utils.search import timestamp_to_datestring

        self.connection_manager = ConnectionManager()
        self.logger = get_logger()
        self.timestamp = timestamp_to_datestring
        self.init_interface()

    def init_interface(self):
        """Sets up base UI"""
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.statusBar().showMessage('Message in statusbar.')

        notes_txt = QTextEdit(self)
        notes_txt.setReadOnly(True)
        self.notes_txt = notes_txt

        filter_txt = QTextEdit(self)
        filter_txt.setReadOnly(False)
        filter_txt.setText('date:today')
        filter_txt.setFocus()
        filter_txt.textChanged.connect(self.filter_notes)
        self.filter_txt = filter_txt

        self.filter_notes()
        self.logger.debug("[Window] Drawing Window")
        self.show()
        self.logger.debug("[Window] Window Drawn")

    def add_parent_modules(self, sys_args):
        """Adds parent modules to import"""
        script_path = os.path.abspath(os.path.dirname(sys_args))
        parent_path = os.path.dirname(script_path)
        parent_parent_path = os.path.dirname(parent_path)
        sys.path.append(parent_parent_path)

    def filter_notes(self):
        """Displays filtered down notes"""
        self.logger.debug("[Filter] Filtering Down Notes")
        self.logger.info(
            "[Filter] Filter Term: %s",
            self.filter_txt.toPlainText())
        self.notes_txt.setText('')
        connector = self.connection_manager.get_primary_connector()
        text = self.filter_txt.toPlainText()
        if text != "":
            terms = [term.strip() for term in text.split(' ')]
        else:
            terms = []
        notes = connector.find_notes(terms)
        for timestamp, note in notes:
            self.notes_txt.insertPlainText(
                "[%s] %s\n" %
                (self.timestamp(timestamp), note))
        self.logger.debug("[Filter] Notes Filtered")

    def resizeEvent(self, event):
        """Handles resizing"""
        input_height = 30
        self.notes_txt.setGeometry(
            0,
            0,
            event.size().width(),
            event.size().height() - input_height
        )
        self.filter_txt.setGeometry(
            0,
            event.size().height() - input_height,
            event.size().width(),
            input_height
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
