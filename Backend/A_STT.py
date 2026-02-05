import numpy as np
import wave
from transformers import pipeline

asr = pipeline("automatic-speech-recognition", model="openai/whisper-small", device=-1)


def load_wav(path):
    with wave.open(path, "rb") as wf:
        sr = wf.getframerate()
        data = wf.readframes(wf.getnframes())

    audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
    return audio, sr


def transcribe_audio(path):
    audio, sr = load_wav(path)

    # Whisper accepts raw array → NO torchaudio needed
    result = asr({"array": audio, "sampling_rate": sr})

    return result["text"]
