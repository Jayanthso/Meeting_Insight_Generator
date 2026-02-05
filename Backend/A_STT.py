import numpy as np
import soundfile as sf
from transformers import pipeline

# pure python loader (NO ffmpeg)
asr = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-small",
    device=-1
)

def transcribe_audio(path):
    # load audio with soundfile instead of ffmpeg
    audio, sr = sf.read(path)

    # convert stereo → mono
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)

    result = asr({
        "array": audio,
        "sampling_rate": sr
    })

    return result["text"]
