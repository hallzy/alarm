import pygame, os, random, subprocess, mutagen.easyid3, math
from datetime import datetime, timedelta

music_directory = r"/home/crclayton/Music"
excluded_genres = ["Hardcore", "Punk", "Podcast", "Various", 
                   "Rap", "Hip-Hop", "Classical"]

timeout       = 30 # minutes
fade_span     =  5 # minutes
end_volume    = 40 # %
start_volume  =  0 # %
i = 0

pygame.init()
pygame.mixer.init()

def start():
    end = datetime.now() + timedelta(minutes = timeout)
    while datetime.now() < end:
        print("Timeout -", end - datetime.now())
        start_song(get_song())
        fade_sound()

def get_random_file(dir, type):
    files = [os.path.join(path, filename)
         for path, dirs, files in os.walk(dir)
         for filename in files
         if filename.endswith(type)]
    return random.choice(files)

def get_song():
    skip = True # skip get until song w/o excluded genres
    while skip:
        f = get_random_file(music_directory, "mp3")
        mp3 = mutagen.easyid3.EasyID3(f)
        genre = get(mp3, "genre")
        skip = any([g in genre for g in excluded_genres])
    print("Music   -", get(mp3, "title"), get(mp3, "artist"), 
                       get(mp3, "album"), get(mp3, "genre"))
    return f

def get(obj, key):
    return obj.get(key, [""])[0]

def set_volume_to(percent):
    subprocess.call(["amixer", "-D", "pulse", "sset", "Master", 
       str(percent) + "%", "stdout=devnull"])

def start_song(song_file):
    pygame.mixer.music.load(song_file)
    pygame.mixer.music.play()

def fade_sound():
    global i 
    volume_sequence = log_scale(fade_span*60, start_volume, end_volume)
    while pygame.mixer.music.get_busy():
        volume = volume_sequence[i] if i < len(volume_sequence) else end_volume
        set_volume_to(volume)
        pygame.time.Clock().tick(1)
        i += 1
    print("Volume  -", volume)

def scale_number(unscaled, to_min, to_max, from_min, from_max):
    return (to_max-to_min)*(unscaled-from_min)/(from_max-from_min) + to_min

def scale_list(l, to_min, to_max):
    return [scale_number(i, to_min, to_max, min(l), max(l)) for i in l]

def log_scale(ticks, minimum, maximum):
    return scale_list([math.log(i+1) for i in range(ticks)], minimum, maximum)
        

if __name__ == "__main__":
    start()
