# app/main.py
from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import pandas as pd
import shutil
import uuid
import zipfile
import json
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "app" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".psd", ".pdf"}
ALLOWED_CSV_EXTENSION = ".csv"

app = FastAPI(title="OrganizeBy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload_csv")
async def upload_csv(
    csv_file: UploadFile = File(...),
    team_col: str = Form(...),
    photo_col: str = Form(...),
    storage_days: int = Form(...)
):
    if not csv_file.filename.lower().endswith(ALLOWED_CSV_EXTENSION):
        raise HTTPException(status_code=400, detail="Invalid CSV file format")

    session_id = str(uuid.uuid4())
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "images").mkdir(exist_ok=True)

    with open(session_dir / "uploaded.csv", "wb") as f:
        f.write(await csv_file.read())

    (session_dir / "session.json").write_text(json.dumps({
        "team_col": team_col,
        "photo_col": photo_col,
        "storage_days": min(int(storage_days), 3),
        "created": datetime.now().isoformat()
    }))

    return {"session_id": session_id}

@app.post("/upload_image")
async def upload_image(
    image_file: UploadFile = File(...),
    session_id: str = Form(...)
):
    session_dir = UPLOAD_DIR / session_id
    image_dir = session_dir / "images"

    if not image_dir.exists():
        return JSONResponse(status_code=404, content={"error": "Invalid session"})

    file_ext = Path(image_file.filename).suffix.lower()
    if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid image file format")

    safe_name = image_file.filename.replace("/", "_").replace("\\", "_")
    with open(image_dir / safe_name, "wb") as f:
        f.write(await image_file.read())

    return {"status": "uploaded", "filename": safe_name}

@app.post("/sort_and_download")
async def sort_and_download(request: Request):
    data = await request.json()
    session_id = data.get("session_id")

    session_dir = UPLOAD_DIR / session_id
    image_dir = session_dir / "images"
    csv_path = session_dir / "uploaded.csv"
    zip_path = session_dir / "sorted_photos.zip"

    if not (session_dir.exists() and csv_path.exists() and image_dir.exists()):
        return JSONResponse(status_code=404, content={"error": "Session or files missing"})

    config = json.loads((session_dir / "session.json").read_text())
    team_col = config["team_col"]
    photo_col = config["photo_col"]

    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        team_name = str(row[team_col]).strip().replace("/", "_").replace("\\", "_")
        photo_name = str(row[photo_col]).strip()
        team_folder = image_dir / team_name
        team_folder.mkdir(exist_ok=True)
        source = image_dir / photo_name
        dest = team_folder / photo_name
        if source.exists():
            shutil.move(str(source), str(dest))

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in image_dir.rglob("*"):
            zipf.write(file, arcname=file.relative_to(image_dir))

    expiry_time = datetime.now() + timedelta(days=config["storage_days"])
    (session_dir / "expiry.txt").write_text(expiry_time.isoformat())

    return FileResponse(zip_path, filename="sorted_photos.zip", media_type="application/zip")
