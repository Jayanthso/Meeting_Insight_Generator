# Backend/A_STT.py

import wave
import numpy as np
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration

TARGET_SR = 16000

# load once (fast after cold start)
processor = WhisperProcessor.from_pretrained("openai/whisper-small")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")


# -------------------
# PURE NUMPY RESAMPLE
# -------------------
def resample(audio, orig_sr, target_sr=TARGET_SR):
    if orig_sr == target_sr:
        return audio

    duration = len(audio) / orig_sr
    new_len = int(duration * target_sr)

    old_idx = np.linspace(0, len(audio) - 1, len(audio))
    new_idx = np.linspace(0, len(audio) - 1, new_len)

    return np.interp(new_idx, old_idx, audio).astype(np.float32)


# -------------------
# TRANSCRIBE
# -------------------
def transcribe_audio(path: str) -> str:
    with wave.open(path, "rb") as wf:
        sr = wf.getframerate()
        frames = wf.readframes(wf.getnframes())

    audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

    audio = resample(audio, sr, TARGET_SR)

    inputs = processor(audio, sampling_rate=TARGET_SR, return_tensors="pt")

    with torch.no_grad():
        pred_ids = model.generate(inputs["input_features"])

    text = processor.batch_decode(pred_ids, skip_special_tokens=True)[0]

    return text
