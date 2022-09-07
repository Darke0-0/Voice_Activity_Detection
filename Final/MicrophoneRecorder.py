from gettext import npgettext
import pyaudio
# import atexit
import threading
import numpy as np
import wave
from pydub import AudioSegment
from pydub.silence import split_on_silence
import matplotlib.pyplot as plt

class MicrophoneRecorder(object):
    def __init__(self, fname='Audio\\test.wav',mode='wb', rate=44100, chunksize=1024):
        self.rate = rate
        self.fname = fname
        self.mode = mode
        self.channels = 1
        self.chunksize = chunksize
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.lock = threading.Lock()
        self.stop = False
        self.frames = []
        self.all_frame = []
        # atexit.register(self.close)

    def __enter__(self):
        return self

    def new_frame(self, data, frame_count, time_info, status):
        data = np.frombuffer(data, 'int16')
        with self.lock:
            self.frames.append(data)
            self.wavefile.writeframes(data)
            if self.stop:
                return data, pyaudio.paComplete
        return data, pyaudio.paContinue

    def last_frames(self):
        with self.lock:
            frames = self.frames
            self.frames = []
            return frames

    # def all_frames(self):
    #     with self.lock:
    #         self.all_frame.append(self.frames)
    #         return self.all_frame

    def record(self, duration):
        # Use a stream with no callback function in blocking mode
        self._stream = self.p.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.chunksize)
        for _ in range(int(self.rate / self.chunksize * duration)):
            audio = self.stream.read(self.chunksize)
            self.wavefile.writeframes(audio)
        return None

    def start_recording(self):
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer = self.chunksize,
                                  stream_callback=self.new_frame)
        self.stream.start_stream()

    def stop_recording(self):
        if self.stream != None:
            self.stream.stop_stream()
            sound_file = AudioSegment.from_wav(self.fname)
            audio_chunks = split_on_silence(sound_file,
                                            min_silence_len=500,
                                            silence_thresh=-32,
                                            keep_silence=200)

            for i, chunk in enumerate(audio_chunks):
                # print(i)
                out_file = ".//Chunks//chunk{}.wav".format(i)
                # print ("exporting", out_file)
                chunk.export(out_file, format="wav")

            self.wavefile.close()
        else:
            pass

    def close(self):
        with self.lock:
            self.stop = True
        self.stream.close()
        self.p.terminate()

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile