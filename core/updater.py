from pathlib import Path
import ssl
from urllib.request import Request, urlopen

import certifi
from PySide6.QtCore import QObject, Signal


REPOSITORY_VERSION_URL = (
    "https://raw.githubusercontent.com/ProudPichu22/"
    "EldenRing-ModManager/main/.version"
)
VERSION_FILE = Path(__file__).resolve().parent.parent / ".version"
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


class UpdateWorker(QObject):

    finished = Signal()
    update_available = Signal(int)
    error = Signal(str)

    def run(self):

        try:
            remote_version = get_remote_version()
            local_version = load_local_version()

            if local_version is None:
                save_local_version(remote_version)
            elif remote_version > local_version:
                self.update_available.emit(remote_version)

        except Exception as error:
            self.error.emit(str(error))
        finally:
            self.finished.emit()


def get_remote_version():

    request = Request(
        REPOSITORY_VERSION_URL,
        headers={"User-Agent": "EldenRing-ModManager"}
    )

    with urlopen(request, timeout=10, context=SSL_CONTEXT) as response:
        version = response.read().decode("utf-8").strip()

    return int(version)


def load_local_version():

    if not VERSION_FILE.exists():
        return None

    version = VERSION_FILE.read_text().strip()
    return int(version) if version else None


def save_local_version(version):

    VERSION_FILE.write_text(f"{version}\n")