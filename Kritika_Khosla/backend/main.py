# backend/main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
import shutil

from .pipeline import run_full_pipeline   # ✅ use relative import inside backend

app = FastAPI(title="PodIntel AI")

BASE_UPLOAD_DIR = os.path.join("dataset", "uploads")
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"message": "PodIntel AI Backend Running 🚀"}


@app.post("/analyze/")
async def analyze_audio(file: UploadFile = File(...)):
    try:
        # ✅ Generate unique session id
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:6]

        # ✅ Create session folder
        session_folder = os.path.join(BASE_UPLOAD_DIR, session_id)
        os.makedirs(session_folder, exist_ok=True)

        # ✅ Clean filename (avoid path issues)
        filename = os.path.basename(file.filename)

        file_path = os.path.join(session_folder, filename)

        # ✅ Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # ✅ Run pipeline
        result = run_full_pipeline(file_path, session_id)

        return JSONResponse(
            content={
                "session_id": session_id,
                "result": result
            }
        )

    except Exception as e:
        print("ERROR:", str(e))   # helpful for debugging
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )