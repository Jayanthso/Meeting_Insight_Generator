from transformers import pipeline

asr = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-small",
    device=-1
)

def transcribe_audio(path):
    result = asr(path)
    return result["text"]
