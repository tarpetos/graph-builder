from typing import Optional

from PyQt5.QtWidgets import QMessageBox

from graph_builder.types import Buttons


class MessageBox(QMessageBox):
    def __init__(
        self,
        title: Optional[str] = "Message",
        text: Optional[str] = None,
        icon: Optional[QMessageBox.Icon] = QMessageBox.Information,
        detailed_text: Optional[str] = None,
        informative_text: Optional[str] = None,
        buttons: Buttons = QMessageBox.Ok,
    ) -> None:
        super().__init__()
        self.setIcon(icon)
        self.setWindowTitle(title)
        self.setText(text)
        self.setDetailedText(detailed_text)
        self.setInformativeText(informative_text)
        self.setStandardButtons(buttons)

    def display(self) -> None:
        self.exec()
