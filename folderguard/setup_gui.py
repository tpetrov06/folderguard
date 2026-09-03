import tkinter as tk

from . import config

root = tk.Tk()
root.title("FolderGuard Setup")
root.geometry("400x300")

label = tk.Label(root, text="Protected Folders")
label.pack(pady=10)

folder_listbox = tk.Listbox(root, width=50)
folder_listbox.pack(pady=10)


def refresh_folder_list():
    folder_listbox.delete(0, tk.END)
    cfg = config.load_config()
    for folder_id, entry in cfg["protected_folders"].items():
        status = "locked" if entry["locked"] else "unlocked"
        folder_listbox.insert(tk.END, f"{entry['name']} ({status})")


from tkinter import filedialog, messagebox
from . import vault


def add_folder():
    folder_path = filedialog.askdirectory(title="Select a folder to protect")
    if not folder_path:
        return  # user cancelled

    try:
        vault.lock_folder(folder_path)
        refresh_folder_list()
    except Exception as e:
        messagebox.showerror("Error", str(e))


add_button = tk.Button(root, text="Add Folder", command=add_folder)
add_button.pack(pady=10)

from . import face_auth


def enroll():
    messagebox.showinfo("Enroll Face", "Click OK, then look at the camera.")
    success = face_auth.enroll_face()
    if success:
        messagebox.showinfo("Enroll Face", "Enrollment successful.")
    else:
        messagebox.showerror("Enroll Face", "Enrollment failed — try again with better lighting.")


enroll_button = tk.Button(root, text="Enroll Face", command=enroll)
enroll_button.pack(pady=10)

refresh_folder_list()


root.mainloop()