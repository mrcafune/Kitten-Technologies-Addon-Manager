import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os
import requests
import zipfile
import io
import threading
import shutil

# Width variable for uniform widget width
widget_width = 350

def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        with open("config.txt", "w") as file:
            file.write(folder_path)
        update_file_list()
        current_folder_label.config(text=folder_path)  # Update the displayed folder path
    else:
        messagebox.showerror("Error", "No folder selected.")

def download_addon():
    response = messagebox.askokcancel("Download", "Download will initiate. This may take a minute.")
    if response:
        download_button.config(state=tk.DISABLED)
        threading.Thread(target=download_addon_thread, daemon=True).start()
    else:
        pass

def download_addon_thread():
    github_repo_url = github_entry.get()
    repo_name = github_repo_url.split('/')[-1]

    def get_download_url(branch):
        return f"{github_repo_url}/archive/refs/heads/{branch}.zip"
    
    def try_download(branch):
        zip_url = get_download_url(branch)
        try:
            response = requests.get(zip_url)
            if response.status_code == 200:
                with open("config.txt", "r") as file:
                    folder_path = file.read().strip()
                addon_folder = os.path.join(folder_path, repo_name)

                if not os.path.exists(addon_folder):
                    os.makedirs(addon_folder)

                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                    temp_dir = os.path.join(folder_path, 'temp')
                    zip_ref.extractall(temp_dir)

                    temp_addon_dir = os.path.join(temp_dir, os.listdir(temp_dir)[0])
                    for filename in os.listdir(temp_addon_dir):
                        shutil.move(os.path.join(temp_addon_dir, filename), addon_folder)

                    shutil.rmtree(temp_dir)

                update_file_list()
                return True
            else:
                return False
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            return False

    if not try_download('main'):
        if not try_download('master'):
            messagebox.showerror("Error", "Failed to download from GitHub.")
    
    download_button.config(state=tk.NORMAL)

def update_file_list():
    file_list.delete(0, tk.END)
    try:
        with open("config.txt", "r") as file:
            folder_path = file.read().strip()
        if os.path.exists(folder_path):
            for folder_name in os.listdir(folder_path):
                file_list.insert(tk.END, folder_name)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def initialize_current_folder_label():
    if os.path.exists("config.txt"):
        with open("config.txt", "r") as file:
            folder_path = file.read().strip()
            current_folder_label.config(text=folder_path)

app = tk.Tk()
app.title("KTAM WoW Addon Manager")
app.configure(bg='#333333')

# Load and display the banner image
banner_image = Image.open("banner.jpg")
banner_image = banner_image.resize((400, 100), Image.Resampling.LANCZOS)
banner_photo = ImageTk.PhotoImage(banner_image)
banner_label = tk.Label(app, image=banner_photo, bg='#333333')
banner_label.pack(pady=(5, 5))

github_entry_label = tk.Label(app, text="GitHub URL", fg='white', bg='#333333')
github_entry_label.pack()

github_entry = tk.Entry(app, width=widget_width // 10)
github_entry.pack()

download_button = tk.Button(app, text="Download Addon", command=download_addon, bg='#4f4f4f', fg='white', width=widget_width // 10)
download_button.pack(pady=(5,10))

file_list_label = tk.Label(app, text="Addons Loaded", fg='white', bg='#333333')
file_list_label.pack(pady=(20, 5))

file_list = tk.Listbox(app, width=widget_width // 10)
file_list.pack(pady=(0,20))

select_folder_button = tk.Button(app, text="Change Addon Folder", command=select_folder, bg='#4f4f4f', fg='white', width=widget_width // 10)
select_folder_button.pack(pady=(20, 5))

# Label to display the current WoW addon path
current_folder_label = tk.Label(app, text="", fg='white', bg='#333333')
current_folder_label.pack(pady=(0, 5))

# Initialize the current folder label when the app starts
initialize_current_folder_label()

app.mainloop()
