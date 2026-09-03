from pathlib import Path
import os
import subprocess
import platform
import shutil

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
    path = Path(path).expanduser().resolve()

    if not path.exists():
        return False

    system = platform.system()

    if system == "Windows":
        os.startfile(str(path))

    elif system == "Linux":
        opener = shutil.which("xdg-open") or shutil.which("gio")

        if opener is None:
            return False

        environment = os.environ.copy()
        for variable in (
            "LD_LIBRARY_PATH",
            "LD_LIBRARY_PATH_ORIG",
            "QT_PLUGIN_PATH",
            "QML2_IMPORT_PATH"
        ):
            environment.pop(variable, None)

        subprocess.Popen(
            [opener, str(path)],
            start_new_session=True,
            env=environment
        )

    elif system == "Darwin":
        subprocess.Popen(
            ["open", str(path)],
            start_new_session=True
        )

    else:
        return False

    return True