from pathlib import Path
import os
import subprocess
import platform

from pathlib import Path
import hashlib


def is_valid_elden_ring_folder(folder):
    """
    Checks if a folder is a valid Elden Ring installation.

    Valid:
        Elden Ring/
        └── Game/
            └── eldenring.exe
    """

    folder = Path(folder)

    game_folder = folder / "Game"

    executable = game_folder / "eldenring.exe"

    return (
        folder.exists()
        and game_folder.exists()
        and executable.exists()
    )

from pathlib import Path


def build_file_list(folder):

    folder = Path(folder)

    if not folder.exists():
        return []

    files = []

    for file in folder.rglob("*"):

        if file.is_file():

            stat = file.stat()

            files.append({
                "path": str(file.relative_to(folder)),
                "size": stat.st_size,
                "modified": stat.st_mtime
            })

    return sorted(
        files,
        key=lambda x: x["path"]
    )

def open_file_manager(path):
    path = str(path)

    system = platform.system()

    if system == "Windows":
        os.startfile(path)

    elif system == "Linux":
        subprocess.run(["xdg-open", path])

    elif system == "Darwin":
        subprocess.run(["open", path])