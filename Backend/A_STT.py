# Backend/A_STT.py

import wave
import numpy as np
from transformers import pipeline

TARGET_SR = 16000

asr = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-small",
    device=-1
)


# -------------------------
# PURE NUMPY RESAMPLER
# -------------------------
def resample(audio, orig_sr, target_sr=TARGET_SR):
    if orig_sr == target_sr:
        return audio

    duration = len(audio) / orig_sr
    new_length = int(duration * target_sr)

    old_indices = np.linspace(0, len(audio) - 1, num=len(audio))
    new_indices = np.linspace(0, len(audio) - 1, num=new_length)

    return np.interp(new_indices, old_indices, audio).astype(np.float32)


# -------------------------
# TRANSCRIBE
# -------------------------
def transcribe_audio(path: str) -> str:
    with wave.open(path, "rb") as wf:
        sr = wf.getframerate()
        frames = wf.readframes(wf.getnframes())

    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

    # ⭐ KEY FIX: manual resample
    audio = resample(audio, sr, TARGET_SR)

    result = asr({
        "array": audio,
        "sampling_rate": TARGET_SR
    })

    return result["text"]
