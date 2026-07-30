from pathlib import Path
import json
from utils.filesystem import build_file_list


class Manifest:

    def __init__(self, profile_path):

        self.profile_path = Path(profile_path)
        self.file_path = self.profile_path / "manifest.json"

        self.data = {
            "name": self.profile_path.name,
            "files": []
        }


    def load(self):

        if not self.file_path.exists():
            return

        with open(self.file_path, "r") as file:
            self.data = json.load(file)



    def save(self):

        self.profile_path.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(self.file_path, "w") as file:
            json.dump(
                self.data,
                file,
                indent=4
            )


    def scan(self):

        files_folder = (
            self.profile_path /
            "files"
        )

        self.data["files"] = build_file_list(
            files_folder
        )


    def update(self):

        self.scan()
        self.save()