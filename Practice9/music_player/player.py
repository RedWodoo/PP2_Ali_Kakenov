import pygame
import os

class Player:
    def __init__(self):
        pygame.mixer.init()
        self.music_dir = "music"
        self.playlist = []
        
        if os.path.exists(self.music_dir):
            self.playlist = [f for f in os.listdir(self.music_dir) if f.endswith(('.mp3', '.wav'))]
            
        self.current_track = 0
        self.status = "Stopped"
        self.total_length = 0
        self.start_offset = 0

    def play(self, start_time=0):
        if self.playlist:
            file_path = os.path.join(self.music_dir, self.playlist[self.current_track])
            
            try:
                sound = pygame.mixer.Sound(file_path)
                self.total_length = sound.get_length()
            except:
                self.total_length = 1
                
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(start=start_time)
            
            self.start_offset = start_time
            self.status = "Playing"

    def pause(self):
        if self.status == "Playing":
            pygame.mixer.music.pause()
            self.status = "Paused"
        elif self.status == "Paused":
            pygame.mixer.music.unpause()
            self.status = "Playing"

    def stop(self):
        pygame.mixer.music.stop()
        self.status = "Stopped"
        self.start_offset = 0

    def next_track(self):
        if self.playlist:
            self.current_track = (self.current_track + 1) % len(self.playlist)
            self.play()

    def prev_track(self):
        if self.playlist:
            self.current_track = (self.current_track - 1) % len(self.playlist)
            self.play()

    def set_position(self, seconds):
        if self.status in ["Playing", "Paused"] and self.playlist:
            was_paused = (self.status == "Paused")
            self.play(start_time=seconds)
            if was_paused:
                pygame.mixer.music.pause()
                self.status = "Paused"

    def get_track_name(self):
        if self.playlist:
            return self.playlist[self.current_track]
        return "Empty Playlist"

    def get_current_time(self):
        if self.status in ["Playing", "Paused"]:
            pos_ms = pygame.mixer.music.get_pos()
            if pos_ms != -1:
                return self.start_offset + (pos_ms / 1000.0)
        return 0

    def get_progress_str(self):
        curr = int(self.get_current_time())
        tot = int(self.total_length)
        return f"{curr // 60:02}:{curr % 60:02} / {tot // 60:02}:{tot % 60:02}"