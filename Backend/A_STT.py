# Backend/A_STT.py

import wave
import numpy as np
from transformers import pipeline


# -------------------------------------------------
# Better model (much higher accuracy)
# -------------------------------------------------
asr = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-base",   # ← upgrade from small
    device=-1
)


# -------------------------------------------------
# Resample WITHOUT torchaudio (pure numpy)
# -------------------------------------------------
def resample(audio, orig_sr, target_sr=16000):
    if orig_sr == target_sr:
        return audio

    duration = len(audio) / orig_sr
    new_len = int(duration * target_sr)

    old_idx = np.linspace(0, len(audio), num=len(audio))
    new_idx = np.linspace(0, len(audio), num=new_len)

    return np.interp(new_idx, old_idx, audio).astype(np.float32)


# -------------------------------------------------
# Chunking improves whisper accuracy
# -------------------------------------------------
def chunk_audio(audio, sr, chunk_seconds=25):
    size = chunk_seconds * sr
    for i in range(0, len(audio), size):
        yield audio[i:i+size]


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def transcribe_audio(path: str) -> str:
    """
    Streamlit-Cloud safe:
    ✔ no ffmpeg
    ✔ no torchaudio
    ✔ no soundfile
    ✔ numpy only
    ✔ better accuracy
    """

    # -------- read wav --------
    with wave.open(path, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        sr = wf.getframerate()
        channels = wf.getnchannels()

    # -------- stereo → mono --------
    if channels == 2:
        audio = audio.reshape(-1, 2).mean(axis=1)

    # -------- resample to 16k --------
    audio = resample(audio, sr, 16000)

    # -------- chunk for better quality --------
    texts = []

    for chunk in chunk_audio(audio, 16000, 25):
        result = asr({"array": chunk, "sampling_rate": 16000})
        texts.append(result["text"])

    return " ".join(texts)
