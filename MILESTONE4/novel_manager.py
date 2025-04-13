import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class NovelManager:
    def __init__(self):
        self.parent = None
        self.select_novel_callback = None
        self.novels_path = None

    def add_novel_entry(self, novel):
        """Add an entry for a novel to the parent widget."""
        frame = ttk.Frame(self.parent, padding=5, relief="ridge")
        frame.pack(fill="x", pady=5)
        try:
            image = Image.open(novel["thumbnail"])
            image = image.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            label_image = tk.Label(frame, image=photo)
            label_image.image = photo
            label_image.pack(side="left", padx=5)
        except Exception as e:
            print(f"Error loading thumbnail for {novel['name']}: {e}")
        label_name = ttk.Label(frame, text=novel["name"], font=("Arial", 14))
        label_name.pack(side="left", padx=10)
        button_select = ttk.Button(frame, text="Select", command=lambda: self.select_novel_callback(novel))
        button_select.pack(side="right", padx=5)

    def get_novels(self):
        """Retrieve a list of novels with their names and thumbnail paths."""
        novels = []
        if os.path.exists(self.novels_path):
            for folder in os.listdir(self.novels_path):
                novel_path = os.path.join(self.novels_path, folder)
                if os.path.isdir(novel_path):
                    thumbnail_path = os.path.join(novel_path, "thumbnail.png")
                    if os.path.exists(thumbnail_path):
                        novels.append({"name": folder, "thumbnail": thumbnail_path, "path": novel_path})
        return novels