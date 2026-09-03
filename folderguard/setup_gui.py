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

def remove_selected():
    selection = folder_listbox.curselection()
    if not selection:
        messagebox.showwarning("Remove Protection", "Select a folder from the list first.")
        return

    index = selection[0]
    cfg = config.load_config()
    folder_ids = list(cfg["protected_folders"].keys())
    folder_id = folder_ids[index]
    entry = cfg["protected_folders"][folder_id]

    confirmed = messagebox.askyesno(
        "Remove Protection",
        f"Remove protection from '{entry['name']}'? This cannot be undone."
    )
    if not confirmed:
        return

    try:
        vault.remove_protection(folder_id)
        refresh_folder_list()
    except Exception as e:
        messagebox.showerror("Error", str(e))


remove_button = tk.Button(root, text="Remove Protection", command=remove_selected)
remove_button.pack(pady=10)


root.mainloop()