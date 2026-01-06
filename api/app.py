from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil

from engine.run_engine import run_engine

import json
from datetime import datetime

from fastapi.middleware.cors import CORSMiddleware

# In-memory storage (temporary)
LAST_RUN_METADATA = []

app = FastAPI(title="ClipForge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLIPS_DIR = BASE_DIR / "clips"

RAW_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/clips",
    StaticFiles(directory=CLIPS_DIR),
    name="clips"
)

METADATA_FILE = BASE_DIR / "data" / "metadata.json"

METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_metadata():
    if not METADATA_FILE.exists():
        return {"matches": []}

    try:
        with open(METADATA_FILE, "r") as f:
            data = json.load(f)
            if "matches" not in data:
                return {"matches": []}
            return data
    except json.JSONDecodeError:
        # File exists but is empty or corrupted
        return {"matches": []}



def save_metadata(data):
    with open(METADATA_FILE, "w") as f:
        json.dump(data, f, indent=2)



# -----------------------------
# Health check
# -----------------------------
@app.get("/")
def root():
    return {"status": "ClipForge API is running"}


# -----------------------------
# Run engine
# -----------------------------
@app.post("/run")
async def options_run(request: Request):
    return JSONResponse(status_code=200, content={})

def run_clipforge(video: UploadFile = File(...)):
    video_path = RAW_DIR / video.filename

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    global LAST_RUN_METADATA
    metadata = run_engine(video_path)
    LAST_RUN_METADATA = metadata

    db = load_metadata()

    db["matches"].append({
        "video": video.filename,
        "timestamp": datetime.utcnow().isoformat(),
        "clips": metadata
    })

    save_metadata(db)

    return JSONResponse(content={
        "video": video.filename,
        "clips_generated": len(metadata),
        "metadata": metadata
    })


# -----------------------------
# List clips
# -----------------------------
@app.get("/clips")
def list_clips():
    clip_list = []

    for video_dir in CLIPS_DIR.iterdir():
        if video_dir.is_dir():
            for clip in video_dir.glob("*.mp4"):
                clip_list.append(str(clip.relative_to(CLIPS_DIR)))

    return {"clips": clip_list}


# -----------------------------
# Stream clip
# -----------------------------
@app.get("/clips/{video}/{clip_name}")
def get_clip(video: str, clip_name: str):
    clip_path = CLIPS_DIR / video / clip_name

    if not clip_path.exists():
        return JSONResponse(
            status_code=404,
            content={"error": "Clip not found"}
        )

    return FileResponse(clip_path, media_type="video/mp4")

# -----------------------------
# ANALYTICS
# -----------------------------
@app.get("/analytics")
def anlytics():
    if not LAST_RUN_METADATA:
        return JSONResponse(
            status_code=400,
            content={"error": "No run data available"}
        )
    
    durations= [clip["duration"] for clip in LAST_RUN_METADATA]

    return {
        "total_clips": len(LAST_RUN_METADATA),
        "total goals": len(LAST_RUN_METADATA)-1,
        "total_highlight_time": round(sum(durations), 2),
        "average_clip_duration": round(sum(durations) / len(durations), 2),
        "longest_clip": round(max(durations), 2),
        "shortest_clip": round(min(durations), 2)
    }

@app.get("/history")
def history():
    return load_metadata()