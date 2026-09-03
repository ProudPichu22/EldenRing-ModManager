from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)


class CreateProfileDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create Profile")
        self.resize(450, 150)

        self.profile_name = QLineEdit()
        self.profile_name.setPlaceholderText(
            "Profile Name"
        )

        self.create_button = QPushButton(
            "Create"
        )

        self.cancel_button = QPushButton(
            "Cancel"
        )


        # Layouts

        name_layout = QHBoxLayout()
        name_layout.addWidget(
            QLabel("Name:")
        )
        name_layout.addWidget(
            self.profile_name
        )


        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(
            self.create_button
        )
        button_layout.addWidget(
            self.cancel_button
        )


        layout = QVBoxLayout(self)

        layout.addLayout(name_layout)
        layout.addLayout(button_layout)

        self.create_button.clicked.connect(
            self.validate
        )

        self.cancel_button.clicked.connect(
            self.reject
        )


    def validate(self):

        if not self.profile_name.text().strip():

            QMessageBox.warning(
                self,
                "Invalid Name",
                "Profile name cannot be empty."
            )

            return

        self.accept()


    def get_data(self):

        return {
            "name": self.profile_name.text().strip()
        }