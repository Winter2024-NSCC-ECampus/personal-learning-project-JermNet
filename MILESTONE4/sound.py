import os
from pygame import mixer
from pydub import AudioSegment
import pygame

class SoundManager:
    def __init__(self, sound_path):
        self.sound_path = sound_path
        self.current_music = None
        self.active_sounds = []
        mixer.init()

    def play_music(self, file_name):
        """Play background music."""
        if self.current_music:
            mixer.music.stop()
            self.current_music = None

        if file_name != "~":
            music_path = os.path.join(self.sound_path, file_name)
            if os.path.exists(music_path):
                mixer.music.load(music_path)
                mixer.music.play(-1)
                self.current_music = music_path

    def stop_music(self):
        """Stop the currently playing music."""
        if self.current_music:
            mixer.music.stop()
            self.current_music = None

    def play_sound(self, sound_name, loops=1):
        """Play a sound effect."""
        if sound_name == "~":
            for sound in self.active_sounds:
                sound.stop()
            self.active_sounds.clear()
            return

        sound_path = os.path.join(self.sound_path, sound_name)
        if os.path.exists(sound_path):
            if sound_path.endswith('.aac'):
                mp3_file = sound_path.replace('.aac', '.mp3')
                self.convert_aac_to_mp3(sound_path, mp3_file)
                sound_path = mp3_file
            sound = pygame.mixer.Sound(sound_path)
            sound.play(loops=loops-1)
            self.active_sounds.append(sound)

    def convert_aac_to_mp3(self, aac_path, mp3_path):
        """Convert an AAC file to MP3 using pydub."""
        if not os.path.exists(mp3_path):
            try:
                audio = AudioSegment.from_file(aac_path, format='aac')
                audio.export(mp3_path, format='mp3')
                print(f"Converted {aac_path} to {mp3_path}")
            except Exception as e:
                print(f"Error converting {aac_path} to MP3: {e}")

    def convert_all_aac_to_mp3(self):
        """Convert all AAC files in the sound folder to MP3."""
        for file_name in os.listdir(self.sound_path):
            if file_name.endswith(".aac"):
                aac_path = os.path.join(self.sound_path, file_name)
                mp3_path = os.path.join(self.sound_path, file_name.replace(".aac", ".mp3"))
                self.convert_aac_to_mp3(aac_path, mp3_path)