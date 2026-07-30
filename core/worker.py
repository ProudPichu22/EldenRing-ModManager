from PySide6.QtCore import QObject, Signal
from pathlib import Path
from core.sync import SyncEngine


class SyncWorker(QObject):

    progress = Signal(int, str)
    finished = Signal()
    error = Signal(str)



    def __init__(self, game_folder, profiles_folder, old_profile, new_profile):
        super().__init__()

        self.engine = SyncEngine(game_folder)

        self.profiles_folder = Path(profiles_folder)

        self.old_profile = (
            self.profiles_folder / old_profile
            if old_profile
            else None
        )

        self.new_profile = (
            self.profiles_folder / new_profile
        )


    def run(self):

        print("Worker Started")
        print("Old profile:", self.old_profile)
        print("New profile:", self.new_profile)
        
        if self.new_profile.name != "Base Game":
            self.engine.update_manifest(
                self.new_profile
            )

        try:

            operations = []

            if self.old_profile:

                print("Generating delete list")
                if self.old_profile.name != "Base Game":
                    self.engine.update_manifest(
                        self.old_profile
                    )

                remove_ops = self.engine.get_remove_operations(
                    self.old_profile
                )


                operations += remove_ops

            else:

                print("No old profile set")

            if self.new_profile.name == "Base Game":
                copy_operations = []
            else:
                copy_operations = self.engine.get_copy_operations(
                    self.new_profile
                )

            operations += copy_operations

            print("Total operations:", len(operations))
            total = len(operations)

            if total == 0:
                print("No file operations needed")
            else:

                for index, operation in enumerate(operations):

                    action, path = operation

                    if action == "delete":

                        self.engine.delete_file(path)

                        description = f"Deleting File: {path}"

                    elif action == "copy":

                        self.engine.copy_file(
                            self.new_profile,
                            path
                        )

                        description = f"Copying File: {path}"
                    else:

                        print("Unknown operation:", action, path)
                        continue


                    percent = int(
                        ((index + 1) / total) * 100
                    )

                    self.progress.emit(
                        percent,
                        description
                    )

                self.engine.remove_empty_folders()

        except Exception as e:

            print("Worker Error:", e)

            self.error.emit(
                str(e)
            )


        print("Worker Finished")

        self.finished.emit()