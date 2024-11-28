import cv2
from fer import FER
import os
import vlc
from tkinter import *
from pathlib import Path
import random
import threading

# Initialize the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Initialize the emotion detector
emotion_detector = FER()

# VLC instance
Instance = vlc.Instance()
player = Instance.media_player_new()

os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')  # For VLC DLLs on Windows

class MusicPlayer:
    def __init__(self, root, emotionStr):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("1000x200+200+200")
        self.track = StringVar()
        self.status = StringVar()

        # Track Frame
        trackframe = LabelFrame(self.root, text="Song Track", font=("times new roman", 15, "bold"),
                                bg="lightblue", fg="purple", bd=5, relief=GROOVE)
        trackframe.place(x=0, y=0, width=620, height=100)
        songtrack = Label(trackframe, textvariable=self.track, width=20,
                          font=("times new roman", 24, "bold"), bg="lightblue", fg="yellowgreen").grid(row=0, column=0, padx=10, pady=5)
        trackstatus = Label(trackframe, textvariable=self.status,
                            font=("times new roman", 18, "bold"), bg="lightblue", fg="yellowgreen").grid(row=0, column=1, padx=5, pady=5)

        # Button Frame
        buttonframe = LabelFrame(self.root, text="Control Panel", font=("times new roman", 15, "bold"),
                                 bg="lightblue", fg="purple", bd=5, relief=GROOVE)
        buttonframe.place(x=0, y=100, width=620, height=100)
        Button(buttonframe, text="PLAY", command=self.playsong, width=6, height=1,
               font=("times new roman", 16, "bold"), fg="lightblue", bg="blue").grid(row=0, column=0, padx=10, pady=5)
        Button(buttonframe, text="PAUSE", command=self.pausesong, width=8, height=1,
               font=("times new roman", 16, "bold"), fg="lightblue", bg="lightyellow").grid(row=0, column=1, padx=10, pady=5)
        Button(buttonframe, text="SHUFFLE", command=self.shufflesong, width=10, height=1,
               font=("times new roman", 16, "bold"), fg="lightblue", bg="violet").grid(row=0, column=2, padx=10, pady=5)
        Button(buttonframe, text="STOP", command=self.stopsong, width=6, height=1,
               font=("times new roman", 16, "bold"), fg="lightblue", bg="red").grid(row=0, column=3, padx=10, pady=5)
        Button(buttonframe, text="NEXT", command=self.nextsong, width=6, height=1,
               font=("times new roman", 16, "bold"), fg="lightblue", bg="navy").grid(row=0, column=4, padx=10, pady=5)

        # Playlist Frame
        songsframe = LabelFrame(self.root, text="Song Playlist", font=("times new roman", 15, "bold"),
                                bg="lightblue", fg="purple", bd=5, relief=GROOVE)
        songsframe.place(x=600, y=0, width=400, height=200)
        scrol_y = Scrollbar(songsframe, orient=VERTICAL)
        self.playlist = Listbox(songsframe, yscrollcommand=scrol_y.set, selectbackground="blue",
                                selectmode=SINGLE, font=("times new roman", 12, "bold"), bg="lightcyan", fg="navyblue", bd=5, relief=GROOVE)
        scrol_y.pack(side=RIGHT, fill=Y)
        scrol_y.config(command=self.playlist.yview)
        self.playlist.pack(fill=BOTH)

        self.load_songs(emotionStr)

    def load_songs(self, emotionStr):
        os.chdir(str(Path(__file__).parent.absolute()) + "\\songs\\" + emotionStr + "\\")
        songtracks = os.listdir()
        self.songtracks = songtracks
        for track in songtracks:
            self.playlist.insert(END, track)

        if not player.is_playing():
            ranSong = random.choice(self.songtracks)
            self.track.set(ranSong)
            self.status.set("-Playing")
            Media = Instance.media_new(ranSong)
            player.set_media(Media)
            player.play()

    def playsong(self):
        self.track.set(self.playlist.get(ACTIVE))
        self.status.set("-Playing")
        Media = Instance.media_new(self.playlist.get(ACTIVE))
        player.set_media(Media)
        player.play()

    def pausesong(self):
        self.status.set("-Paused")
        player.pause()

    def stopsong(self):
        self.status.set("-Stopped")
        player.stop()

    def nextsong(self):
        next_index = (self.playlist.curselection()[0] + 1) % len(self.songtracks)
        next_song = self.songtracks[next_index]
        self.track.set(next_song)
        Media = Instance.media_new(next_song)
        player.set_media(Media)
        player.play()

    def shufflesong(self):
        self.status.set("-Shuffle Play")
        song = random.choice(self.songtracks)
        self.track.set(song)
        Media = Instance.media_new(song)
        player.set_media(Media)
        player.play()

def display_webcam():
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break
        cv2.imshow("Webcam Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def update_music_player_for_emotion(emotion):
    root = Tk()
    emotion_map = {"happy": "happy", "sad": "sad", "angry": "angry", "surprise": "surprised", "neutral": "neutral"}
    emotionStr = emotion_map.get(emotion, "neutral")
    MusicPlayer(root, emotionStr)
    root.mainloop()

def detect_emotion():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face = frame[y:y+h, x:x+w]
            emotion, score = emotion_detector.top_emotion(face)
            if emotion:
                update_music_player_for_emotion(emotion)

webcam_thread = threading.Thread(target=display_webcam)
emotion_thread = threading.Thread(target=detect_emotion)

webcam_thread.start()
emotion_thread.start()

webcam_thread.join()
emotion_thread.join()

cap.release()
cv2.destroyAllWindows()