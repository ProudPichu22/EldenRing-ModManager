from pathlib import Path
import os
import subprocess
import platform

from PySide6.QtWidgets import (
    QWidget,
    QListWidget,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QHBoxLayout,
    QVBoxLayout
)
from PySide6.QtCore import QThread


from core.settings import Settings
from core.profiles import ProfileManager
from ui.create_profile import CreateProfileDialog
from utils.filesystem import is_valid_elden_ring_folder
from core.manager import ModManager
from ui.progress_dialog import ProgressDialog
from core.worker import SyncWorker

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

        self.create_button = QPushButton("Create")
        self.delete_button = QPushButton("Delete")
        self.settings_button = QPushButton("Settings")
        self.choose_game_button = QPushButton("Choose Elden Ring Folder")

        self.game_label = QLabel()

        self.refresh_profiles()

        self.launch_button.clicked.connect(self.launch_profile)
        self.open_button.clicked.connect(self.open_folder)
        self.create_button.clicked.connect(self.create_profile)
        self.delete_button.clicked.connect(self.delete_profile)
        self.settings_button.clicked.connect(self.open_settings)
        self.thread = None
        self.worker = None
        self.progress_dialog = None

        left = QVBoxLayout()
        left.addWidget(self.profile_list)

        right = QVBoxLayout()
        right.addWidget(self.launch_button)
        right.addWidget(self.open_button)
        right.addSpacing(20)
        right.addWidget(self.create_button)
        right.addWidget(self.delete_button)
        right.addStretch()
        right.addWidget(self.settings_button)
        right = QVBoxLayout()

        right.addWidget(self.choose_game_button)
        right.addWidget(self.launch_button)
        right.addWidget(self.open_button)

        right.addSpacing(20)

        right.addWidget(self.create_button)
        right.addWidget(self.delete_button)

        right.addStretch()

        right.addWidget(self.settings_button)

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
        self.mod_manager = ModManager(
            self.settings
        )

    def update_game_label(self):

        self.game_label.setText(
            f"Elden Ring Folder:\n{self.settings.game_directory}"
        )

        valid = bool(self.settings.game_directory)

        self.launch_button.setEnabled(valid)
        self.create_button.setEnabled(valid)
        self.open_button.setEnabled(valid)

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
                name,
                data["executable"]
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


        self.launch_executable(
            profile
        )

    def launch_executable(self, profile):

        manifest = self.profile_manager.get_manifest(profile)

        launch_type = manifest.get(
            "launchType"
        )

        target = manifest.get(
            "launchTarget"
        )


        if launch_type == "steam":

            url = f"steam://rungameid/{target}"

            if platform.system() == "Windows":
                os.startfile(url)
            else:
                subprocess.Popen(
                    ["xdg-open", url]
                )


        elif launch_type == "executable":

            executable = (
                Path(profile) /
                target
            )

            subprocess.Popen(
                [str(executable)]
            )

    def open_settings(self):
        self.settings.save()
        settings_path = self.settings.SETTINGS_FILE

        if platform.system() == "Windows":
            os.startfile(settings_path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", settings_path])
        else:
            subprocess.run(["xdg-open", settings_path])
    
    def update_delete_button(self):

        profile = self.current_profile()

        if profile == "Base Game":
            self.delete_button.setEnabled(False)
        else:
            self.delete_button.setEnabled(True)
