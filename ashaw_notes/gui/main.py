""" Main Notes UI
"""
import sys
import os
import webbrowser
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox
from PyQt5.QtWidgets import QPushButton, QTextBrowser, QLineEdit, QCompleter, QLabel
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import pyqtSlot, Qt

from ashaw_notes.utils.connection_manager import ConnectionManager
from ashaw_notes.utils.plugin_manager import PluginManager
from ashaw_notes.utils.configuration import get_logger
from ashaw_notes.utils.search import timestamp_to_datestring


class App(QMainWindow):
    """QT Application"""

    def __init__(self):
        super().__init__()
        self.title = 'Notes'
        self.left = 10
        self.top = 10
        self.width = 920
        self.height = 380

        self.connection_manager = ConnectionManager()
        self.plugin_manager = PluginManager()
        self.logger = get_logger()
        self.timestamp = timestamp_to_datestring
        while True:
            try:
                self.init_interface()
                break
            except Exception as error:
                response = QMessageBox.warning(
                    self, 'Notes Error Occured', "%s" % error,
                    QMessageBox.Retry | QMessageBox.Cancel, QMessageBox.Retry)

                if response == QMessageBox.Cancel:
                    exit()

    def init_interface(self):
        """Sets up base UI"""
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.statusBar().showMessage('Message in statusbar.')

        notes_txt = QTextBrowser(self)
        notes_txt.setReadOnly(True)
        notes_txt.anchorClicked.connect(self.click_link)
        notes_txt.setOpenLinks(False)

        font = QFont('Monospace')
        notes_txt.setFont(font)
        self.setStyleSheet("""
        QTextEdit, QLineEdit {
            background-color: #272822;
            color: #aaa;
        }
        QLabel {
            font-weight: bold;
            color: #aaa;
            padding: 5px;
        }
        """)

        self.notes_txt = notes_txt

        filter_txt = QLineEdit(self)
        filter_txt.setReadOnly(False)
        filter_txt.setText('date:today')
        filter_txt.setFocus()
        filter_txt.textChanged.connect(self.filter_notes)
        filter_txt.returnPressed.connect(self.filter_notes)
        filter_txt.setStyleSheet("border: 0px;")
        filter_txt.setToolTip("Filter Input")
        self.filter_txt = filter_txt

        completer = QCompleter(self.connection_manager.get_primary_connector().get_common_words())
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)

        completer.popup().setStyleSheet("""
        QListView {
            background-color: #272822;
            color: #aaa;
            selection-background-color: #511;
        }
        """)
        filter_txt.setCompleter(completer)

        count_label = QLabel(self)
        count_label.setAlignment(Qt.AlignRight)
        self.count_label = count_label

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
            self.filter_txt.text())
        self.notes_txt.setText('')
        self.count_label.setText('loading...')
        text = self.filter_txt.text()
        if len(text) > 2:
            terms = [term.strip() for term in text.split(' ')]
        else:
            # for repsonsiveness, don't allow sub-3 character searches
            return
        connector = self.connection_manager.get_primary_connector()
        notes = connector.find_notes(terms)
        self.logger.debug("[Filter] Found %s notes", len(notes))
        self.count_label.setText('%s results' % len(notes))
        html = ''
        for timestamp, note in notes:
            html += "%s<br>" % self.plugin_manager.format_note_line(timestamp, note)
        self.logger.debug("[Filter] DOM prepared. Drawing")
        self.notes_txt.insertHtml(html)
        self.logger.debug("[Filter] Notes Filtered")
        self.notes_txt.verticalScrollBar().setValue(
            self.notes_txt.verticalScrollBar().maximum()
        )

    def click_link(self, qurl):
        """Handles Note Clicking"""
        url = qurl.toString()
        self.logger.debug("Processing click: %s", url)
        if url[0:7] == 'filter:':
            self.filter_txt.setText(url[7:])
            self.filter_notes()
        elif url[0:4] == 'http':
            webbrowser.open(url, autoraise=True)

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
        self.count_label.setGeometry(
            event.size().width() - self.count_label.width(),
            event.size().height() - input_height,
            self.count_label.width(),
            input_height
        )

def run():
    """Runs the Application"""
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
