import ctypes
from pathlib import Path

from . import config

FILE_ATTRIBUTE_HIDDEN = 0x02
FILE_ATTRIBUTE_SYSTEM = 0x04


def _hide(path: Path):
    ctypes.windll.kernel32.SetFileAttributesW(
        str(path), FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM
    )


def lock_folder(original_path: str) -> str:
    original = Path(original_path)
    if not original.exists():
        raise FileNotFoundError(f"{original} does not exist")

    folder_id = config.new_id()
    hidden = original.parent / f".fg_{folder_id}"

    original.rename(hidden)
    _hide(hidden)

    cfg = config.load_config()
    cfg["protected_folders"][folder_id] = {
        "name": original.name,
        "original_path": str(original),
        "hidden_path": str(hidden),
        "locked": True,
    }
    config.save_config(cfg)

    return folder_id

FILE_ATTRIBUTE_NORMAL = 0x80

def _unhide(path: Path):
    ctypes.windll.kernel32.SetFileAttributesW(str(path), FILE_ATTRIBUTE_NORMAL)

def unlock_folder(folder_id: str):
    cfg = config.load_config()
    entry = cfg["protected_folders"].get(folder_id)
    if entry is None:
        raise KeyError(f"No protected folder with id {folder_id}")

    hidden = Path(entry["hidden_path"])
    original = Path(entry["original_path"])

    _unhide(hidden)
    hidden.rename(original)

    entry["locked"] = False
    config.save_config(cfg)

if __name__ == "__main__":
    unlock_folder("ba02902832c1")
    print("unlocked")