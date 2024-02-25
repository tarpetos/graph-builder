from typing import Optional, Union

from PyQt5.QtWidgets import QMessageBox


class MessageBox(QMessageBox):
    def __init__(
        self,
        title: Optional[str] = "Message",
        text: Optional[str] = None,
        icon: Optional[QMessageBox.Information] = QMessageBox.Information,
        detailed_text: Optional[str] = None,
        informative_text: Optional[str] = None,
        buttons: Union[
            QMessageBox.StandardButtons, QMessageBox.StandardButton
        ] = QMessageBox.Ok,
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
