from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QProgressBar
)


class ProgressDialog(QDialog):

    def __init__(self):

        super().__init__()

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


    def update_progress(self, value, text):

        self.progress.setValue(
            value
        )

        self.label.setText(
            text
        )