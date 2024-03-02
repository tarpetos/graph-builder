import sys

from PyQt5.QtWidgets import QApplication

from .graph_builder import GraphBuilderWindow


class GraphBuilderApp:
    @staticmethod
    def start() -> None:
        app = QApplication(sys.argv)
        win = GraphBuilderWindow()
        win.show()
        sys.exit(app.exec_())
