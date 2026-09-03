import json
from pathlib import Path


class Settings:

    SETTINGS_FILE = Path("settings.json")

    def __init__(self):

        self.game_directory = ""
        self.active_profile = ""

        self.load()

    def load(self):

        if not self.SETTINGS_FILE.exists():
            return

        data = json.loads(
            self.SETTINGS_FILE.read_text()
        )

        self.game_directory = data.get(
            "game_directory",
            ""
        )

        self.active_profile = data.get(
            "active_profile",
            ""
        )

    def save(self):

        data = {
            "game_directory": self.game_directory,
            "active_profile": self.active_profile
        }

        self.SETTINGS_FILE.write_text(
            json.dumps(data, indent=4)
        )
