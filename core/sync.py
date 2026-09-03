from pathlib import Path
import shutil
import json

class SyncEngine:


    def __init__(self, game_folder):

        self.game_folder = Path(game_folder)


    def get_copy_operations(self, profile):

        # Base Game has no files folder
        if Path(profile).name == "Base Game":
            return []

        files_folder = (
            Path(profile) /
            "files"
        )

        operations = []

        if not files_folder.exists():
            return operations

        for file in files_folder.rglob("*"):

            if file.is_file():

                operations.append(
                    (
                        "copy",
                        file.relative_to(files_folder)
                    )
                )

        return operations



    def get_remove_operations(self, profile):

        manifest_path = (
            Path(profile) /
            "manifest.json"
        )

        if not manifest_path.exists():
            return []

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        operations = []

        if Path(profile).name == "Base Game":
            base_files = {
                Path(file["path"])
                for file in manifest.get("files", [])
            }

            for file in self.game_folder.rglob("*"):
                if file.is_file():
                    relative_path = file.relative_to(self.game_folder)

                    if relative_path not in base_files:
                        operations.append(("delete", relative_path))

            return operations

        for file in manifest.get("files", []):

            operations.append(
                (
                    "delete",
                    Path(file["path"])
                )
            )

        return operations



    def delete_file(self, path):

        target = self.game_folder / path

        print("Trying to delete:", target)

        if target.exists():

            target.unlink()

            print("Deleted:", target)

            return True

        print("Missing:", target)

        return False



    def copy_file(self, profile, path):

        source = (
            Path(profile)
            / "files"
            / path
        )


        destination = (
            self.game_folder
            / path
        )
        
        print("Copy source:", source)
        print("Copy destination:", destination)

        if not source.exists():
            print("SOURCE MISSING")
            return False

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )


        shutil.copy2(
            source,
            destination
        )

        print("Destination exists:", destination.exists())
        print("Destination size:", destination.stat().st_size)

    def update_manifest(self, profile):

        profile = Path(profile)

        is_base_game = (
            profile.name == "Base Game"
        )


        if is_base_game:
            files_folder = self.game_folder
        else:
            files_folder = profile / "files"
        manifest_file = profile / "manifest.json"

        file_list = []

        if files_folder.exists():

            for file in files_folder.rglob("*"):

                if file.is_file():

                    stat = file.stat()

                    file_list.append({
                        "path": str(
                            file.relative_to(files_folder)
                        ),
                        "size": stat.st_size,
                        "modified": stat.st_mtime
                    })


        data = {}

        if manifest_file.exists():

            with open(manifest_file, "r") as f:
                data = json.load(f)


        data["files"] = file_list


        with open(manifest_file, "w") as f:
            json.dump(
                data,
                f,
                indent=4
            )
        
    def remove_empty_folders(self):

        # Reverse order removes deepest folders first
        folders = sorted(
            self.game_folder.rglob("*"),
            key=lambda p: len(p.parts),
            reverse=True
        )

        for folder in folders:

            if folder.is_dir():

                try:
                    folder.rmdir()

                    print(
                        "Removed empty folder:",
                        folder
                    )

                except OSError:
                    # Folder is not empty
                    pass