import subprocess
import sys
 
 
# ================= dependencies =================
 
DEPENDENCIES = [
    ("py7zr", "py7zr"),
    ("customtkinter", "customtkinter"),
]
 
for import_name, install_name in DEPENDENCIES:
    try:
        __import__(import_name)
    except ImportError:
        print(f"Installing {install_name}...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", install_name]
        )
 
# ================= imports (after deps are guaranteed) =================
 
import customtkinter as ctk
from app import App
 
 
# ================= entry point =================
 
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
 
    root = ctk.CTk()
    App(root, ctk)
    root.mainloop()