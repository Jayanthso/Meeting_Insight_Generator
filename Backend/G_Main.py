import os 
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import JSONResponse
import os, traceback

from Backend.A_STT import transcribe_audio
from Backend.F_llm import generate_insights
from Backend.D_pdf_export import generate_pdf

app = FastAPI()

@app.post("/process")
async def process(
    transcript: str = Form(None),
    audio: UploadFile = File(None),
    title: str = Form(None),
    meeting_type: str = Form(None)
):
    try:
        if audio is not None:
            # ✅ Preserve original extension (.mp3, .wav, etc.)
            suffix = os.path.splitext(audio.filename)[-1] or ".mp3"
            audio_path = f"temp_upload{suffix}"

            # Save uploaded file
            with open(audio_path, "wb") as f:
                f.write(await audio.read())

            # Debug check
            print("Saved audio at:", audio_path)
            print("File exists?", os.path.exists(audio_path))

            # Transcribe audio
            transcript = transcribe_audio(audio_path)

            # Clean up
            os.remove(audio_path)

        if not transcript:
            return JSONResponse(
                status_code=400,
                content={"error": "No transcript or audio provided"}
            )

        # Generate insights
        insights = generate_insights(transcript)

        # Generate PDF
        pdf_path = "report.pdf"
        generate_pdf(insights, pdf_path)

        return {"insights": insights, "pdf_path": pdf_path}

    except Exception as e:
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})
