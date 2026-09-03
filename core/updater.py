from pathlib import Path
from urllib.request import Request, urlopen

from PySide6.QtCore import QObject, Signal


REPOSITORY_ARCHIVE_URL = (
    "https://github.com/ProudPichu22/EldenRing-ModManager/"
    "archive/refs/heads/main.zip"
)
REPOSITORY_VERSION_URL = (
    "https://raw.githubusercontent.com/ProudPichu22/"
    "EldenRing-ModManager/main/.version"
)
VERSION_FILE = Path(__file__).resolve().parent.parent / ".version"


class UpdateWorker(QObject):

    finished = Signal()
    updated = Signal(int, str)
    error = Signal(str)

    def run(self):

        try:
            remote_version = get_remote_version()
            local_version = load_local_version()

            if local_version is None:
                save_local_version(remote_version)
            elif remote_version > local_version:
                update_path = download_latest_update()
                save_local_version(remote_version)
                self.updated.emit(remote_version, str(update_path))

        except Exception as error:
            self.error.emit(str(error))
        finally:
            self.finished.emit()


def get_remote_version():

    request = Request(
        REPOSITORY_VERSION_URL,
        headers={"User-Agent": "EldenRing-ModManager"}
    )

    with urlopen(request, timeout=10) as response:
        version = response.read().decode("utf-8").strip()

    return int(version)


def load_local_version():

    if not VERSION_FILE.exists():
        return None

    version = VERSION_FILE.read_text().strip()
    return int(version) if version else None


def save_local_version(version):

    VERSION_FILE.write_text(f"{version}\n")


def download_latest_update(destination=None):

    if destination is None:
        destination = Path.home() / "Downloads" / "EldenRing-ModManager-latest.zip"
    else:
        destination = Path(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)

    request = Request(
        REPOSITORY_ARCHIVE_URL,
        headers={"User-Agent": "EldenRing-ModManager"}
    )

    with urlopen(request, timeout=30) as response:
        with destination.open("wb") as archive:
            while chunk := response.read(1024 * 1024):
                archive.write(chunk)

    return destination