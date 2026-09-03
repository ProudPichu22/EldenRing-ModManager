from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QListWidget,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QHBoxLayout,
    QVBoxLayout
)
from PySide6.QtCore import QThread, Qt, QUrl
from PySide6.QtGui import QDesktopServices


from core.settings import Settings
from core.profiles import ProfileManager
from ui.create_profile import CreateProfileDialog
from utils.filesystem import is_valid_elden_ring_folder, open_file_manager
from ui.progress_dialog import ProgressDialog
from core.worker import SyncWorker
from core.updater import UpdateWorker

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.settings = Settings()
        self.profile_manager = ProfileManager(self.settings)

        self.setWindowTitle("Elden Ring Mod Manager")
        self.resize(700, 500)

        self.profile_list = QListWidget()

        self.launch_button = QPushButton("Set Profile")
        self.open_button = QPushButton("Open Folder")
        self.refresh_manifest_button = QPushButton("Refresh Manifest")

        self.create_button = QPushButton("Create")
        self.delete_button = QPushButton("Delete")
        self.settings_button = QPushButton("Settings")
        self.choose_game_button = QPushButton("Choose Elden Ring Folder")

        self.game_label = QLabel()

        self.refresh_profiles()

        self.launch_button.clicked.connect(self.launch_profile)
        self.open_button.clicked.connect(self.open_folder)
        self.refresh_manifest_button.clicked.connect(
            self.refresh_manifest
        )
        self.create_button.clicked.connect(self.create_profile)
        self.delete_button.clicked.connect(self.delete_profile)
        self.settings_button.clicked.connect(self.open_settings)
        self.thread = None
        self.worker = None
        self.progress_dialog = None
        self.update_thread = None
        self.update_worker = None

        left = QVBoxLayout()
        left.addWidget(self.profile_list)

        right = QVBoxLayout()
        right.addWidget(self.launch_button)
        right.addWidget(self.open_button)
        right.addWidget(self.refresh_manifest_button)
        right.addSpacing(20)
        right.addWidget(self.create_button)
        right.addWidget(self.delete_button)
        right.addStretch()
        right.addWidget(self.settings_button)
        right = QVBoxLayout()

        right.addWidget(self.launch_button)
        right.addWidget(self.open_button)
        right.addWidget(self.refresh_manifest_button)

        right.addSpacing(20)

        right.addWidget(self.create_button)
        right.addWidget(self.delete_button)

        right.addStretch()

        right.addWidget(self.settings_button)
        right.addWidget(
            self.choose_game_button,
            alignment=Qt.AlignmentFlag.AlignRight
        )

        layout = QHBoxLayout()
        layout.addLayout(left, 3)
        layout.addLayout(right, 1)

        root = QVBoxLayout(self)
        root.addLayout(layout)
        root.addWidget(self.game_label)

        self.update_game_label()
        self.profile_list.currentItemChanged.connect(
            self.update_delete_button
        )
        self.choose_game_button.clicked.connect(
            self.choose_game_folder
        )
        self.check_for_updates()
    def update_game_label(self):

        self.game_label.setText(
            f"Elden Ring Folder:\n{self.settings.game_directory}"
        )

        valid = bool(self.settings.game_directory)

        action_buttons = (
            self.launch_button,
            self.open_button,
            self.refresh_manifest_button,
            self.create_button,
            self.delete_button,
            self.settings_button
        )

        for button in action_buttons:
            button.setVisible(valid)
            button.setEnabled(valid)

        self.choose_game_button.setVisible(not valid)

    def check_for_updates(self):

        self.update_thread = QThread()
        self.update_worker = UpdateWorker()
        self.update_worker.moveToThread(self.update_thread)

        self.update_thread.started.connect(
            self.update_worker.run
        )
        self.update_worker.update_available.connect(
            self.update_available
        )
        self.update_worker.error.connect(
            self.update_failed
        )
        self.update_worker.finished.connect(
            self.update_thread.quit
        )
        self.update_worker.finished.connect(
            self.update_worker.deleteLater
        )
        self.update_thread.finished.connect(
            self.update_thread.deleteLater
        )
        self.update_thread.finished.connect(
            self.update_thread_finished
        )

        self.update_thread.start()

    def update_thread_finished(self):

        self.update_worker = None
        self.update_thread = None

    def update_available(self, version):

        result = QMessageBox.question(
            self,
            "Update Available",
            f"A new version is available. Would you like to download it?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if result == QMessageBox.Yes:
            QDesktopServices.openUrl(
                QUrl(
                    "https://github.com/ProudPichu22/"
                    "EldenRing-ModManager/releases/latest"
                )
            )

    def update_failed(self, error):

        QMessageBox.warning(
            self,
            "Update Check Failed",
            f"The latest update could not be checked:\n\n{error}"
        )

    def refresh_profiles(self):

        self.profile_list.clear()

        for profile in self.profile_manager.get_profiles():
            self.profile_list.addItem(profile)

        self.update_delete_button()

    def current_profile(self):
        item = self.profile_list.currentItem()
        return item.text() if item else None

    def choose_game_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Elden Ring Folder"
        )

        if not folder:
            return


        if not is_valid_elden_ring_folder(folder):

            QMessageBox.warning(
                self,
                "Invalid Folder",
                "This is not a valid Elden Ring folder.\n\n"
                "The folder must contain:\n"
                "Game/eldenring.exe"
            )

            return


        self.settings.game_directory = folder
        self.settings.save()


        self.profile_manager.initialize_profiles()


        self.refresh_profiles()
        self.update_game_label()


        QMessageBox.information(
            self,
            "Elden Ring Found",
            "Elden Ring folder configured successfully.\n"
            "Base Game profile has been created."
        )

    def create_profile(self):

        dialog = CreateProfileDialog(self)

        if dialog.exec():

            data = dialog.get_data()

            name = data["name"]

            if name in self.profile_manager.get_profiles():
                QMessageBox.warning(
                    self,
                    "Profile Exists",
                    "A profile with this name already exists."
                )
                return


            self.profile_manager.create_profile(
                name
            )

            self.refresh_profiles()

    def delete_profile(self):

        profile = self.current_profile()

        if profile is None:
            QMessageBox.warning(
                self,
                "No Profile Selected",
                "Please select a profile to delete."
            )
            return


        result = QMessageBox.question(
            self,
            "Delete Profile",
            f"Are you sure you want to delete '{profile}'?\n\n"
            "This will permanently delete the profile and its files.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )


        if result == QMessageBox.Yes:

            self.profile_manager.delete_profile(profile)

            self.refresh_profiles()

    def open_folder(self):
        profile = self.current_profile()

        if profile:
            self.profile_manager.open_profile(profile)

    def refresh_manifest(self):

        profile = self.current_profile()

        if not profile or profile == "Base Game":
            return

        self.profile_manager.update_profile_manifest(profile)

        QMessageBox.information(
            self,
            "Manifest Refreshed",
            f"The manifest for '{profile}' has been updated."
        )

    def launch_profile(self):

        print("Launched")

        if self.thread and self.thread.isRunning():
            QMessageBox.information(
                self,
                "Profile Switching",
                "A profile is already being applied."
            )
            return

        profile = self.current_profile()

        if not profile:
            return

        if profile == self.settings.active_profile:
            QMessageBox.information(
                self,
                "Already Active",
                "This profile is already loaded."
            )
            return

        self.progress_dialog = ProgressDialog()
        self.progress_dialog.show()


        self.thread = QThread()

        self.worker = SyncWorker(
            Path(self.settings.game_directory) / "Game",
            Path(self.settings.game_directory) / "ModProfiles",
            self.settings.active_profile,
            profile
        )


        self.worker.moveToThread(
            self.thread
        )


        self.thread.started.connect(
            self.worker.run
        )


        self.worker.progress.connect(
            self.progress_dialog.update_progress
        )


        self.worker.finished.connect(
            self.sync_finished
        )


        self.worker.error.connect(
            self.sync_error
        )


        self.worker.finished.connect(
            self.thread.quit
        )


        self.thread.finished.connect(
            self.thread_finished
        )


        self.thread.finished.connect(
            self.thread.deleteLater
        )


        self.worker.finished.connect(
            self.worker.deleteLater
        )

        print("Thread object:", self.thread)

        self.thread.start()
    
    def thread_finished(self):

        print("Thread cleaned up")

        self.worker = None
        self.thread = None
    
    def sync_error(self, error):

        print("Sync error:", error)

        if self.progress_dialog:
            self.progress_dialog.close_when_finished()

        QMessageBox.critical(
            self,
            "Profile Switch Failed",
            f"An error occurred while switching profiles:\n\n{error}"
        )

    def sync_finished(self):

        print("Sync finished")

        self.progress_dialog.close_when_finished()

        profile = self.current_profile()

        self.settings.active_profile = profile
        self.settings.save()


    def open_settings(self):
        self.settings.save()
        open_file_manager(self.settings.SETTINGS_FILE)
    
    def update_delete_button(self):

        profile = self.current_profile()

        if profile == "Base Game":
            self.delete_button.setEnabled(False)
            self.refresh_manifest_button.setEnabled(False)
        else:
            self.delete_button.setEnabled(True)
            self.refresh_manifest_button.setEnabled(
                bool(profile) and bool(self.settings.game_directory)
            )
