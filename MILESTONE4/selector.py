import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import re
import time
from pygame import mixer
import pygame
from variables import VariableManager
from history import TextHistoryManager
from novel_manager import NovelManager
import json
from sound import SoundManager

class VisualNovelSelector:
    def __init__(self, root, novels_path="novels"):
        """Initialize the main application window."""
        self.novels_path = novels_path
        self.root = root
        self.root.resizable(False, False)
        self.root.title("Select a Visual Novel")

        self.initialize_managers()
        self.initialize_game_state()
        self.create_widgets()

    def initialize_managers(self):
        """Initialize external managers."""
        self.variable_manager = VariableManager()
        self.text_history_manager = TextHistoryManager(self.root)
        self.novel_manager = NovelManager()
        self.novel_manager.novels_path = self.novels_path
        self.novels = self.novel_manager.get_novels()

    def initialize_game_state(self):
        """Initialize game state variables."""
        self.skip_stack = []
        self.is_typing = False
        self.is_fading = False
        self.is_delaying = False
        self.is_choosing = False
        self.current_music = None
        self.foreground_images = []
        self.active_sounds = []
        self.variables = {}
        self.current_novel = ""
        self.width = 256
        self.height = 192
        self.background = None
        mixer.init()

    def create_widgets(self):
        """Create the GUI elements."""
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.novel_manager.parent = scrollable_frame
        self.novel_manager.select_novel_callback = self.select_novel
        for novel in self.novels:
            self.novel_manager.add_novel_entry(novel)
    
    def load_script(self, script_name, target_label=None):
        """Load a new script file, reset execution, and optionally jump to a label."""
        script_path = os.path.join("novels", self.current_novel, "script", script_name)
        if not os.path.exists(script_path):
            print(f"Error: Script file '{script_name}' not found.")
            return

        with open(script_path, "r") as script_file:
            self.script_lines = script_file.readlines()

        self.current_line = 0

        self.labels = {}
        for i, line in enumerate(self.script_lines):
            line = line.strip()
            if line.startswith("label "):
                label_name = line[6:].strip()
                self.labels[label_name] = i

        if target_label:
            if target_label in self.labels:
                self.current_line = self.labels[target_label]
            else:
                print(f"Error: Label '{target_label}' not found in '{script_name}'.")

    def clean_text(self, text):
        """Remove ANSI escape sequences from the text."""
        ansi_escape_pattern = re.compile(r'\\x1b\[[0-9;]*[mK]')
        cleaned_text = ansi_escape_pattern.sub('', text)
        return cleaned_text
    
    def split_long_string(self, s, limit=50):
        """Split a long string into smaller parts based on a character limit."""
        result = []
        while len(s) > limit:
            split_point = s.rfind(" ", 0, limit)
            if split_point == -1:
                split_point = limit
            
            result.append(s[:split_point].rstrip())
            s = s[split_point:].lstrip()
        
        if s:
            result.append(s)
        return result
    
    def save_game(self):
        """Save the current game state to a JSON file in the current novel's folder."""
        if not self.current_novel:
            print("No novel is currently selected.")
            return

        save_file = os.path.join("novels", self.current_novel, "save_data.json")
        save_data = {
            "current_line": self.current_line,
            "current_script": getattr(self, "current_script", None),
            "variables": self.variable_manager.variables,
            "current_music": self.current_music,
            "background": self.background,
            "foreground_images": [
                {"file_path": img_data["file_path"], "x": img_data["x"], "y": img_data["y"]}
                for img_data in self.foreground_images
            ],
            #"active_sounds": [sound.get_raw() for sound in self.active_sounds],
            "current_novel": self.current_novel,
            "skip_stack": self.skip_stack
        }
        with open(save_file, "w") as f:
            json.dump(save_data, f, indent=4)
        print(f"Game saved to {save_file}")

    def load_game(self):
        """Load the game state from a JSON file in the current novel's folder."""
        if not self.current_novel:
            print("No novel is currently selected.")
            return

        save_file = os.path.join("novels", self.current_novel, "save_data.json")
        if not os.path.exists(save_file):
            print(f"No save file found in {save_file}.")
            return

        with open(save_file, "r") as f:
            save_data = json.load(f)

        self.current_script = save_data.get("current_script")
        self.current_line = save_data["current_line"]
        self.variable_manager.variables = save_data["variables"]
        self.current_music = save_data["current_music"]
        self.current_novel = save_data["current_novel"]
        self.background = save_data["background"]
        self.skip_stack = save_data["skip_stack"]
        if self.current_script:
            self.load_script(self.current_script)
        if self.current_music:
            self.sound_manager.play_music(self.current_music)
        for sound in self.active_sounds:
            sound.stop()

        self.fade_in_background(self.background, 0)
        self.foreground_images.clear()
        for img_data in save_data.get("foreground_images", []):
            img_path = img_data["file_path"]
            x, y = img_data["x"], img_data["y"]
            self.fade_in_foreground(img_path, x, y, 0)

        # self.active_sounds.clear()
        # for sound_raw in save_data.get("active_sounds", []):
        #     sound = pygame.mixer.Sound(buffer=sound_raw)
        #     self.active_sounds.append(sound)
        #     sound.play()
        print(f"Game loaded from {save_file}")
            
    def fade_in_background(self, image_path, duration):
        """Fade in a background image over the specified duration."""
        self.is_fading = True
        image = Image.open(image_path).resize((self.width * 2, self.height * 2), Image.Resampling.LANCZOS)
        bg_photo = ImageTk.PhotoImage(image)
        self.canvas.image = bg_photo
        steps = 10
        interval = int(duration / steps)
        for alpha in range(0, 256, int(255 / steps)):
            temp_image = image.copy()
            temp_image.putalpha(alpha)
            temp_photo = ImageTk.PhotoImage(temp_image)
            self.canvas.create_image(0, 0, anchor="nw", image=temp_photo, tags="bg")
            self.canvas.update()
            time.sleep(interval / 1000)
            
        self.canvas.delete("bg")
        self.canvas.create_image(0, 0, anchor="nw", image=bg_photo, tags="persistent_bg")
        self.is_fading = False
        self.background = image_path

    def fade_in_foreground(self, image_name, x, y, duration=16 * 1000 // 60):
        """Fade in a foreground image over 16/60 of a second, preserving transparency."""
        foreground_path = os.path.join("novels", self.current_novel, "foreground", image_name)
        print(foreground_path)
        if os.path.exists(foreground_path):
            image = Image.open(foreground_path).convert("RGBA")
            image = image.resize((image.width * 2, image.height * 2), Image.Resampling.LANCZOS)
            transparent_img = Image.new("RGBA", image.size, (0, 0, 0, 0))
            assumed_width = 256
            assumed_height = 192
            x_pos = int(x * (self.width * 2) / assumed_width)
            y_pos = int(y * (self.height * 2) / assumed_height)
            steps = 10
            interval = int(duration / steps)
            def fade_step(step=0):
                """Gradually increase image visibility using Image.blend()."""
                if step > steps:
                    return

                alpha = step / steps
                blended = Image.blend(transparent_img, image, alpha)
                photo = ImageTk.PhotoImage(blended)
                self.foreground_images.append({"image": photo, "file_path": image_name, "x": x, "y": y})
                image_tag = f"fg_{image_name}_{x}_{y}"
                self.canvas.create_image(x_pos, y_pos, anchor="nw", image=photo, tags=image_tag)
                self.canvas.tag_raise(image_tag)
                self.root.after(interval, fade_step, step + 1)

            fade_step()

    def select_novel(self, novel):
        """Handle selecting a novel."""
        try:
            script_path = os.path.join(novel["path"], "script/main.scr")
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Script file not found for {novel['name']}.")

            background_path = os.path.join(novel["path"], "background")
            if not os.path.exists(background_path):
                raise FileNotFoundError(f"Background folder not found for {novel['name']}.")

            background_images = [f for f in os.listdir(background_path) if f.endswith((".png", ".jpg", ".jpeg"))]
            if not background_images:
                raise FileNotFoundError(f"No background images found for {novel['name']}.")
            
            sound_path = os.path.join(novel["path"], "sound")
            if not os.path.exists(sound_path):
                raise FileNotFoundError(f"Sound folder not found for {novel['name']}.")
            
            self.sound_manager = SoundManager(sound_path)
            choice_buttons = []
            self.sound_manager.convert_all_aac_to_mp3()
            interpreter_window = tk.Toplevel(self.root)
            interpreter_window.title(novel["name"])
            interpreter_window.resizable(False, False)
            interpreter_window.grid_rowconfigure(0, weight=1)
            interpreter_window.grid_rowconfigure(1, weight=0)
            interpreter_window.grid_columnconfigure(0, weight=1)
            interpreter_window.geometry(f"{self.width * 2}x{self.height * 2 + 300}")
            self.canvas = tk.Canvas(interpreter_window, width=self.width * 2, height=self.height * 2)
            self.canvas.grid(row=0, column=0, sticky="nsew")
            root.grid_rowconfigure(0, weight=1)
            root.grid_columnconfigure(0, weight=1) 
            self.text_history_manager = TextHistoryManager(interpreter_window)
            text_frame = ttk.Frame(interpreter_window, height=100)
            text_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
            self.text_labels = [ttk.Label(text_frame, text="", font=("Arial", 16), anchor="w") for _ in range(7)]
            for i, label in enumerate(self.text_labels):
                label.grid(row=i, column=0, sticky="w")

            self.current_novel = novel["name"]
            history_button = ttk.Button(interpreter_window, text="Show History", command=self.text_history_manager.show_text_history)
            history_button.grid(row=3, column=0, columnspan=2, pady=5)
            file_path = os.path.join(novel["path"], "script")
            with open(script_path, "r") as script_file:
                self.script_lines = script_file.readlines()

            for filename in os.listdir(file_path):
                file_path = os.path.join("novels", novel["name"], "script", filename)
                if os.path.isfile(file_path):
                    print(f"Reading file: {filename}")
                    with open(file_path, 'r') as file:
                        for line in file:
                            if line.startswith("setvar") or line.startswith("gsetvar"):
                                self.variable_manager.set_variable(line)
                                continue
            
            self.current_line = 0
            self.current_script = "main.scr"
            self.on_screen_text = []

            def typewriter_effect(label, text, callback=None, index=0):
                """Display text character by character with a delay."""
                if index == 0:
                    self.is_typing = True 

                if index < len(text):
                    label.config(text=label.cget("text") + text[index])
                    label.after(50, typewriter_effect, label, text, callback, index + 1)
                else:
                    self.is_typing = False
                    if callback:
                        callback()
            
            def clear_background():
                """Clear all previous background images."""
                self.canvas.delete("all")

            def play_music(file_name):
                """Play a music file from the sound folder."""
                if self.current_music:
                    mixer.music.stop()
                    self.current_music = None

                if file_name != "~":
                    music_path = os.path.join(sound_path, file_name)
                    if os.path.exists(music_path):
                        mixer.music.load(music_path)
                        mixer.music.play(-1)
                        self.current_music = music_path

            def play_sound(sound_name, loops=1):
                """Play a sound effect using pygame in a non-blocking manner."""
                if sound_name == "~":
                    for sound in self.active_sounds:
                        sound.stop()

                    self.active_sounds.clear()
                    return
                
                sound_dir = os.path.join(sound_path, sound_name)
                if os.path.exists(sound_dir):
                    if sound_dir.endswith('.aac'):
                        mp3_file = sound_dir.replace('.aac', '.mp3')
                        sound_dir = mp3_file
                    
                    sound = pygame.mixer.Sound(sound_dir)
                    sound.play(loops=loops-1)
                    self.active_sounds.append(sound)
            
            def end_delay():
                """Ends the delay and allows user input again."""
                self.is_delaying = False

            def display_choices(choices):
                """Display choices as buttons in a row under the canvas."""
                clear_choice_buttons()
                self.choice_frame = ttk.Frame(interpreter_window)
                self.choice_frame.grid(row=2, column=0, columnspan=len(choices), pady=10)
                for i, choice in enumerate(choices):
                    button = ttk.Button(self.choice_frame, text=choice, command=lambda c=i+1: choice_selected(c))
                    button.grid(row=0, column=i, padx=5)
                    choice_buttons.append(button)

            def choice_selected(choice_index):
                """Handle choice selection, store the selected index, and continue the script."""
                self.selected_choice = choice_index
                print(f"Player selected option {self.selected_choice}")
                clear_choice_buttons()
                self.is_choosing = False
                display_next_line()

            def clear_choice_buttons():
                """Remove existing choice buttons."""
                for button in choice_buttons:
                    button.destroy()
                
                choice_buttons.clear()

            def display_next_line(event=None):
                """Display the next line of the script."""
                if self.is_typing or self.is_fading or self.is_delaying or self.is_choosing:
                    return
                
                if not hasattr(self, "labels"):
                    self.labels = {}
                    for i, line in enumerate(self.script_lines):
                        line = line.strip()
                        if line.startswith("label "):
                            label_name = line[6:].strip()
                            self.labels[label_name] = i

                while self.current_line < len(self.script_lines):
                    line = self.script_lines[self.current_line].strip()
                    self.current_line += 1
                    if self.skip_stack and self.skip_stack[-1]:
                        if line == "fi":
                            self.skip_stack.pop()
                        elif line.startswith("if "):
                            self.skip_stack.append(True)
                        continue
                    elif line.startswith("if selected == "):  
                        condition_value = int(line.split("==")[1].strip())
                        if self.selected_choice != condition_value:
                            self.skip_stack.append(True)
                        else:
                            self.skip_stack.append(False)
                        continue

                    if line.startswith("if "):
                        condition = line[3:].strip()
                        for var in self.variable_manager.variables:
                            condition = re.sub(rf"\b{var}\b", str(self.variable_manager.variables[var]), condition)

                        try:
                            result = eval(condition)
                            self.skip_stack.append(not result)
                        except Exception as e:
                            print(f"Error evaluating condition '{condition}': {e}")
                            self.skip_stack.append(True)

                        continue  

                    if line == "fi":
                        if self.skip_stack:
                            self.skip_stack.pop()
                        continue 
                    
                    if line.startswith("label "):
                        continue
                
                    if line.startswith("goto "):
                        label_name = line[5:].strip()
                        if label_name in self.labels:
                            self.current_line = self.labels[label_name]
                        else:
                            print(f"Error: Label '{label_name}' not found.")
                        continue
                    
                    if line.startswith("load"):
                        print("load")
                        self.load_game()
                    
                    if line.startswith("save"):
                        self.save_game()
                    
                    if line.startswith("delay "):
                        parts = line.split()
                        if len(parts) == 2 and parts[1].isdigit():
                            delay_time = int(parts[1]) * 1000 // 60
                            self.is_delaying = True
                            self.root.after(delay_time, end_delay())
                            continue
                        else:
                            print(f"Invalid delay command: {line}")
                        continue
                    elif line.startswith("choice "):
                        self.is_choosing = True
                        choices = line[7:].split("|")
                        display_choices(choices)
                        return
                    
                    if line.startswith("jump "):
                        parts = line.split()
                        script_name = parts[1]
                        target_label = parts[2] if len(parts) > 2 else None
                        self.skip_stack.clear()
                        self.load_script(script_name, target_label)
                        self.root.after(50, display_next_line)
                        self.current_script = parts[1]
                        continue

                    if line.startswith("text @"):
                        text = self.variable_manager.replace_variables(line[6:])
                        text = self.clean_text(text)
                        self.text_history_manager.add_to_history(text)
                        self.on_screen_text.append(text)
                        if len(self.on_screen_text) > 7:
                            self.on_screen_text.pop(0)

                        for i, label in enumerate(self.text_labels):
                            label.config(text=self.on_screen_text[i] if i < len(self.on_screen_text) else "")
                        
                        continue
                    elif line.startswith("sound"):
                        parts = line.split()
                        if len(parts) == 2:
                            play_sound(parts[1])
                        elif len(parts) == 3:
                            loops = int(parts[2])
                            play_sound(parts[1], loops=loops)
                        
                        continue
                    elif line == "text !":
                        self.text_history_manager.add_to_history("")
                        self.on_screen_text.append("")
                        if len(self.on_screen_text) > 7:
                            self.on_screen_text.pop(0)
                            
                        for i, label in enumerate(self.text_labels):
                            label.config(text=self.on_screen_text[i] if i < len(self.on_screen_text) else "")
                        
                        break
                    elif line.startswith("text ~"):
                        self.text_history_manager.add_to_history("")
                        self.on_screen_text.append("")
                        if len(self.on_screen_text) > 7:
                            self.on_screen_text.pop(0)
                        
                        for i, label in enumerate(self.text_labels):
                            label.config(text=self.on_screen_text[i] if i < len(self.on_screen_text) else "")
                        
                        continue
                    elif line.startswith("setimg"):
                        parts = line.split()
                        if len(parts) >= 4:
                            self.fade_in_foreground(parts[1], int(parts[2]), int(parts[3]))
                        
                        continue
                    elif line.startswith("setvar") or line.startswith("gsetvar"):
                        self.variable_manager.set_variables(line)
                        continue
                    elif line.startswith("text"):
                        text = self.variable_manager.replace_variables(line[5:])
                        text = self.clean_text(text)
                        text_parts = self.split_long_string(text, 48)
                        for part in text_parts:
                            self.text_history_manager.add_to_history(part)
                            self.on_screen_text.append(part)
                            
                        if len(self.on_screen_text) > 7:
                            self.on_screen_text = self.on_screen_text[-7:]

                        for i, label in enumerate(self.text_labels):
                            if i < len(self.on_screen_text):
                                label.config(text=self.on_screen_text[i])
                                if i == len(self.on_screen_text) - 1:
                                    pass
                            else:
                                label.config(text="")
                        break
                    elif line.startswith("bgload"):
                        parts = line.split()
                        image_name = parts[1]
                        duration = int(parts[2]) if len(parts) > 2 else 16
                        clear_background()
                        image_path = os.path.join(background_path, image_name)
                        self.fade_in_background(image_path, duration * 1000 / 60)
                        continue
                    elif line.startswith("music"):
                        parts = line.split()
                        music_name = parts[1]
                        play_music(music_name)
                        continue
                    elif line == "cleartext":
                        for label in self.text_labels:
                            label.config(text="")
                        self.on_screen_text.clear()
                        continue
                    elif line == "cleartext !":
                        self.on_screen_text.clear()
                        self.text_history_manager.text_history.clear()
                        continue
                    
            interpreter_window.bind("z", display_next_line)
            interpreter_window.bind("s", lambda event: self.save_game())
            interpreter_window.bind("l", lambda event: self.load_game())
            display_next_line()
        except Exception as e:
            print(f"Error opening novel {novel['name']}: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualNovelSelector(root)
    root.mainloop()