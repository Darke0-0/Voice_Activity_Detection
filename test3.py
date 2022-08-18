<<<<<<< HEAD
from pydub import AudioSegment
from pydub.silence import split_on_silence

def make_chunks():
    sound_file = AudioSegment.from_wav("recording\\a-z.wav")
    audio_chunks = split_on_silence(sound_file, 
    # must be silent for at least half a second
    min_silence_len=400,

    # consider it silent if quieter than -16 dBFS
    silence_thresh=-45,

    # keep 200 ms of leading/trailing silence
    keep_silence=200

    )

    for i, chunk in enumerate(audio_chunks):
        print(i)
        out_file = ".//recording//chunk{}.wav".format(i)
        print ("exporting", out_file)
        chunk.export(out_file, format="wav")

=======
from pydub import AudioSegment
from pydub.silence import split_on_silence

def make_chunks():
    sound_file = AudioSegment.from_wav("recording\\a-z.wav")
    audio_chunks = split_on_silence(sound_file, 
    # must be silent for at least half a second
    min_silence_len=400,

    # consider it silent if quieter than -16 dBFS
    silence_thresh=-45,

    # keep 200 ms of leading/trailing silence
    keep_silence=200

    )

    for i, chunk in enumerate(audio_chunks):
        print(i)
        out_file = ".//recording//chunk{}.wav".format(i)
        print ("exporting", out_file)
        chunk.export(out_file, format="wav")

>>>>>>> a8189213f616f2a3c6a493b2003682a28c473487
