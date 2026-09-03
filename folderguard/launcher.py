import sys

from . import vault

def main():
    if len(sys.argv) < 2:
        print("No folder id provided")
        return

    folder_id = sys.argv[1]
    print("launcher received id:", folder_id)

    vault.unlock_folder(folder_id)
    print("folder unlocked")


if __name__ == "__main__":
    main()