from pathlib import Path

from core.sync import SyncEngine


class ModManager:


    def __init__(self, settings):

        self.settings = settings


    def launch_profile(self, name):

        profiles = (
            Path(self.settings.game_directory)
            / "ModProfiles"
        )


        current = self.settings.active_profile


        engine = SyncEngine(
            Path(self.settings.game_directory)
            / "Game"
        )


        # Remove old profile

        if current:

            engine.remove_profile_files(
                profiles / current
            )


        # Apply new profile

        engine.copy_profile_files(
            profiles / name
        )


        self.settings.active_profile = name
        self.settings.save()