import ctypes
import sys
from pathlib import Path

import win32com.client
import ctypes.wintypes

from . import config

LAUNCHER_PYTHON = sys.executable.replace("python.exe", "pythonw.exe")

# ---- Windows file attribute flags ----
FILE_ATTRIBUTE_HIDDEN = 0x02
FILE_ATTRIBUTE_SYSTEM = 0x04
FILE_ATTRIBUTE_NORMAL = 0x80

SHCNF_PATH = 0x0001
SHCNE_UPDATEDIR = 0x00001000

def _notify_shell(path: Path):
    parent = ctypes.c_wchar_p(str(path.parent))
    ctypes.windll.shell32.SHChangeNotify(SHCNE_UPDATEDIR, SHCNF_PATH, parent, None)

SHCNE_ASSOCCHANGED = 0x08000000
SHCNF_IDLIST = 0x0000

def _notify_shell_refresh_all():
    ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)

def _hide(path: Path):
    ctypes.windll.kernel32.SetFileAttributesW(
        str(path), FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM
    )
    _notify_shell(path)


def _unhide(path: Path):
    ctypes.windll.kernel32.SetFileAttributesW(str(path), FILE_ATTRIBUTE_NORMAL)

def _restore_name(hidden: Path, original: Path):
    if original.exists():
        raise FileExistsError(
            f"Cannot restore '{original.name}' — something already exists at {original}"
        )
    hidden.rename(original)
    _notify_shell(original)

PROJECT_ROOT = str(Path(__file__).parent.parent)


def create_shortcut(shortcut_path: Path, folder_id: str):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(str(shortcut_path))

    if getattr(sys, "frozen", False):
        shortcut.TargetPath = sys.executable
        shortcut.Arguments = folder_id
        shortcut.WorkingDirectory = str(Path(sys.executable).parent)
    else:
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
    _restore_name(hidden, original)

    shortcut_path = Path(entry["shortcut_path"])
    if shortcut_path.exists():
        shortcut_path.unlink()

    _notify_shell_refresh_all()

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

    shortcut_path = Path(entry["shortcut_path"])
    create_shortcut(shortcut_path, folder_id)

    _notify_shell_refresh_all()

    entry["locked"] = True
    config.save_config(cfg)

def remove_protection(folder_id: str):
    cfg = config.load_config()
    entry = cfg["protected_folders"].get(folder_id)
    if entry is None:
        raise KeyError(f"No protected folder with id {folder_id}")

    hidden = Path(entry["hidden_path"])
    original = Path(entry["original_path"])

    if entry["locked"] and hidden.exists():
        _unhide(hidden)
        _restore_name(hidden, original)

    shortcut_path = Path(entry["shortcut_path"])
    if shortcut_path.exists():
        shortcut_path.unlink()

    del cfg["protected_folders"][folder_id]
    config.save_config(cfg)

if __name__ == "__main__":
    import os
    os.makedirs("C:/Temp/TestFolder", exist_ok=True)
    fid = lock_folder("C:/Temp/TestFolder")
    print("locked, id:", fid)
    input("press enter to unlock...")
    unlock_folder(fid)
    print("unlocked")