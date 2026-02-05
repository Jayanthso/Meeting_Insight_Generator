# Backend/A_STT.py

import wave
import numpy as np
from transformers import pipeline

# lightweight whisper
asr = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-small"
)


def transcribe_audio(path: str) -> str:
    """
    Works with .wav only
    No ffmpeg
    No soundfile
    100% Streamlit Cloud safe
    """

    with wave.open(path, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        sr = wf.getframerate()

    result = asr({"array": audio, "sampling_rate": sr})
    return result["text"]
