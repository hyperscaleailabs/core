"""OpenAI-compatible transcription server backed by faster-whisper.

Exposes:
  POST /v1/audio/transcriptions  (multipart: file, model, language?, response_format?)
  GET  /healthz
"""

import os
import tempfile

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse
from faster_whisper import WhisperModel

MODEL_ID = os.environ.get("WHISPER_MODEL", "Systran/faster-whisper-small")
DEVICE = os.environ.get("WHISPER_DEVICE", "cpu")
COMPUTE_TYPE = os.environ.get("WHISPER_COMPUTE_TYPE", "int8")

app = FastAPI(title="faster-whisper-server")
model = WhisperModel(MODEL_ID, device=DEVICE, compute_type=COMPUTE_TYPE)


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "model": MODEL_ID, "device": DEVICE}


@app.post("/v1/audio/transcriptions")
async def transcribe(
    file: UploadFile = File(...),
    model_name: str = Form(default=MODEL_ID, alias="model"),
    language: str | None = Form(default=None),
    response_format: str = Form(default="json"),
):
    suffix = os.path.splitext(file.filename or "audio")[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        tmp.write(await file.read())
        tmp.flush()
        segments, info = model.transcribe(tmp.name, language=language)
        segment_list = [
            {"id": i, "start": s.start, "end": s.end, "text": s.text}
            for i, s in enumerate(segments)
        ]

    text = "".join(s["text"] for s in segment_list).strip()

    if response_format == "text":
        return PlainTextResponse(text)
    return JSONResponse(
        {
            "text": text,
            "language": info.language,
            "duration": info.duration,
            "segments": segment_list,
        }
    )
