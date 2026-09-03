import shutil
from pathlib import Path
from utils.filesystem import open_file_manager
from core.manifest import Manifest
from core.sync import SyncEngine
from utils.filesystem import build_file_list

class ProfileManager:

    def __init__(self, settings):

        self.settings = settings

    @property
    def profiles_folder(self):

        if not self.settings.game_directory:
            return None

        return (
            Path(self.settings.game_directory)
            / "ModProfiles"
        )

    def get_profiles(self):
        folder = self.profiles_folder

        if folder is None:
            return []

        folder.mkdir(parents=True, exist_ok=True)

        return sorted(
            f.name
            for f in folder.iterdir()
            if f.is_dir()
        )

    def create_profile(self, name):

        profile = self.profiles_folder / name

        profile.mkdir(
            parents=True,
            exist_ok=True
        )

        (profile / "files").mkdir(
            exist_ok=True
        )

        manifest = Manifest(profile)

        manifest.data["name"] = name

        manifest.save()

    def delete_profile(self, name):

        shutil.rmtree(self.profiles_folder / name)

    
    def open_profile(self, name):
        profile_path = self.profiles_folder / name

        if profile_path.exists():
            open_file_manager(profile_path)
    
    def update_profile_manifest(self, name):

        profile = self.profiles_folder / name

        engine = SyncEngine(
            Path(self.settings.game_directory) / "Game"
        )
        engine.update_manifest(profile)
    
    def initialize_profiles(self):

        if self.profiles_folder is None:
            return


        self.profiles_folder.mkdir(
            parents=True,
            exist_ok=True
        )


        base_profile = (
            self.profiles_folder /
            "Base Game"
        )


        if base_profile.exists():
            return


        files_folder = (
            base_profile /
            "files"
        )

        files_folder.mkdir(
            parents=True
        )


        manifest = Manifest(base_profile)

        manifest.data["name"] = "Base Game"


        # Scan the current game installation
        game_folder = (
            Path(self.settings.game_directory)
            / "Game"
        )


        manifest.data["files"] = build_file_list(
            game_folder
        )


        manifest.save()