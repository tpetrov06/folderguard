import sys
import os
import time

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

from . import vault, face_auth, config


def main():
    if len(sys.argv) < 2:
        print("No folder id provided")
        return

    folder_id = sys.argv[1]

    if not face_auth.has_enrolled_face():
        print("No face enrolled yet — run setup first")
        return

    verified = face_auth.verify_face()

    if not verified:
        print("Face not recognized — access denied")
        return

    vault.unlock_folder(folder_id)
    print("unlocked")

    os.startfile(get_original_path(folder_id))

    cfg = config.load_config()
    timeout_minutes = cfg["settings"]["relock_timeout_minutes"]
    time.sleep(timeout_minutes * 60)

    vault.relock_folder(folder_id)
    print("relocked")


def get_original_path(folder_id):
    cfg = config.load_config()
    return cfg["protected_folders"][folder_id]["original_path"]


if __name__ == "__main__":
    main()