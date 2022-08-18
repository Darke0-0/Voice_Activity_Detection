import tkinter
import sounddevice as sd
from tkinter import *
import queue
import soundfile as sf
import threading
from tkinter import messagebox
from pydub import AudioSegment
from pydub.silence import split_on_silence
import test3 

#Functions to play, stop and record audio in Python voice recorder
#The recording is done as a thread to prevent it being the main process
def threading_rec(x):
   if x == 1:
       #If recording is selected, then the thread is activated
       t1=threading.Thread(target= record_audio)
       t1.start()
   elif x == 2:
        #To stop, set the flag to false
        global recording
        recording = False
        # messagebox.showinfo(message="Recording finished")
        voice_rec.config(bg="#ff0000")
        sound_file = AudioSegment.from_wav("recording\\a-z.wav")
        audio_chunks = split_on_silence(sound_file, 
            # must be silent for at least half a second
            min_silence_len=400,

            # consider it silent if quieter than -45 dBFS
            silence_thresh=-45,
        )

        for i, chunk in enumerate(audio_chunks):
            print(i)
            out_file = ".//recording//chunk{}.wav".format(i)
            print ("exporting", out_file)
            chunk.export(out_file, format="wav")

   elif x == 3:
       #To play a recording, it must exist.
       if file_exists:
           #Read the recording if it exists and play it
           data, fs = sf.read("recording\\a-z.wav", dtype='float32')
           sd.play(data,fs)
           sd.wait()
       else:
           #Display and error if none is found
           messagebox.showerror(message="Record something to play")

#Recording function
def record_audio():
   #Declare global variables   
   global recording
   #Set to True to record
   recording= True  
   global file_exists
   #Create a file to save the audio
   voice_rec.config(bg="#00FF00")
#    messagebox.showinfo(message="Recording Audio. Speak into the mic")
   with sf.SoundFile("recording\\a-z.wav", mode='w', samplerate=44100,
                       channels=2) as file:
   #Create an input stream to record audio without a preset time
           with sd.InputStream(samplerate=44100, channels=2, callback=callback):
               while recording == True:
                   #Set the variable to True to allow playing the audio later
                   file_exists =True
                   #write into file
                   file.write(q.get())

#Fit data into queue
def callback(indata, frames, time, status):
   q.put(indata.copy())

#Define the user interface for Voice Recorder using Python
voice_rec = Tk()
voice_rec.geometry("500x400")
voice_rec.title("Voice Recorder")
voice_rec.config(bg="#107dc2")
#Create a queue to contain the audio data
q = queue.Queue()
#Declare variables and initialise them
recording = False
file_exists = False

#Label to display app title in Python Voice Recorder Project
title_lbl  = Label(voice_rec, text="Voice Recorder", bg="#107dc2").grid(row=0, column=0, columnspan=3)
 
#Button to record audio
record_btn = Button(voice_rec, text="Record Audio", command=lambda m=1:threading_rec(m))
#Stop button
stop_btn = Button(voice_rec, text="Stop Recording", command=lambda m=2:threading_rec(m))
#Play button
play_btn = Button(voice_rec, text="Play Recording", command=lambda m=3:threading_rec(m))
#Position buttons
record_btn.grid(row=1,column=0)
stop_btn.grid(row=1,column=1)
# play_btn.grid(row=1,column=2)
voice_rec.mainloop()
test3.make_chunks()