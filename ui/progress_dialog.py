from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QProgressBar
)
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Qt


class ProgressDialog(QDialog):

    def __init__(self):

        super().__init__()

        self._can_close = False
        self.setWindowFlag(
            Qt.WindowType.WindowCloseButtonHint,
            False
        )

        self.setWindowTitle(
            "Applying Profile"
        )

        self.resize(
            400,
            120
        )


        self.label = QLabel(
            "Starting..."
        )


        self.progress = QProgressBar()


        layout = QVBoxLayout(self)

        layout.addWidget(
            self.label
        )

        layout.addWidget(
            self.progress
        )

    def closeEvent(self, event: QCloseEvent):

        if self._can_close:
            event.accept()
        else:
            event.ignore()

    def close_when_finished(self):

        self._can_close = True
        self.close()


    def update_progress(self, value, text):

        self.progress.setValue(
            value
        )

        self.label.setText(
            text
        )