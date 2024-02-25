import sys

import qdarkstyle
from PyQt5.QtWidgets import QApplication

from .graph_builder import GraphBuilderWindow


class GraphBuilderApp:
    @staticmethod
    def start() -> None:
        app = QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyqt5"))
        win = GraphBuilderWindow()
        win.show()
        sys.exit(app.exec_())
