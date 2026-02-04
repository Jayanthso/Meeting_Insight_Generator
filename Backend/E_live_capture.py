import sounddevice as sd
import scipy.io.wavfile as wav
import whisper

model = whisper.load_model("base")

def record_and_transcribe(seconds=10):

    fs = 16000
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()

    wav.write("live.wav", fs, recording)

    result = model.transcribe("live.wav")
    return result["text"]
