import ctypes
import sys
from pathlib import Path

import win32com.client

from . import config

# ---- Windows file attribute flags ----
FILE_ATTRIBUTE_HIDDEN = 0x02
FILE_ATTRIBUTE_SYSTEM = 0x04
FILE_ATTRIBUTE_NORMAL = 0x80

# ---- Shortcut target: this project's launcher.py, run with no console window ----
LAUNCHER_PYTHON = sys.executable.replace("python.exe", "pythonw.exe")


def _hide(path: Path):
    ctypes.windll.kernel32.SetFileAttributesW(
        str(path), FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM
    )


def _unhide(path: Path):
    ctypes.windll.kernel32.SetFileAttributesW(str(path), FILE_ATTRIBUTE_NORMAL)


PROJECT_ROOT = str(Path(__file__).parent.parent)


def create_shortcut(shortcut_path: Path, folder_id: str):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(str(shortcut_path))
    shortcut.TargetPath = LAUNCHER_PYTHON
    shortcut.Arguments = f'-m folderguard.launcher {folder_id}'
    shortcut.WorkingDirectory = PROJECT_ROOT
    shortcut.Save()


def lock_folder(original_path: str) -> str:
    original = Path(original_path)
    if not original.exists():
        raise FileNotFoundError(f"{original} does not exist")

    folder_id = config.new_id()
    hidden = original.parent / f".fg_{folder_id}"

    original.rename(hidden)
    _hide(hidden)

    shortcut_path = original.parent / f"{original.name}.lnk"
    create_shortcut(shortcut_path, folder_id)

    cfg = config.load_config()
    cfg["protected_folders"][folder_id] = {
        "name": original.name,
        "original_path": str(original),
        "hidden_path": str(hidden),
        "locked": True,
        "shortcut_path": str(shortcut_path),
    }
    config.save_config(cfg)

    return folder_id


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

def relock_folder(folder_id: str):
    cfg = config.load_config()
    entry = cfg["protected_folders"].get(folder_id)
    if entry is None:
        raise KeyError(f"No protected folder with id {folder_id}")

    original = Path(entry["original_path"])
    hidden = Path(entry["hidden_path"])

    original.rename(hidden)
    _hide(hidden)

    entry["locked"] = True
    config.save_config(cfg)

if __name__ == "__main__":
    import os
    os.makedirs("C:/Temp/TestFolder", exist_ok=True)
    fid = lock_folder("C:/Temp/TestFolder")
    print("locked, id:", fid)
    unlock_folder(fid)
    print("unlocked")
    relock_folder(fid)
    print("relocked")