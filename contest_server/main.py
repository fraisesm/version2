from fastapi import FastAPI, UploadFile, File, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from auth import create_token, verify_token
from database import SessionLocal, init_db
from models import Team, Submission
from datetime import datetime
import aiofiles
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
BASE_DIR = "contest_server"

@app.post("/register")
def register(name: str = Form(...)):
    db = SessionLocal()
    token = create_token(name)
    team = Team(name=name, token=token)
    db.add(team)
    db.commit()
    return {"token": token}

@app.get("/task")
async def get_task(team: str = Depends(verify_token)):
    task_path = os.path.join(BASE_DIR, "tasks")
    files = sorted(f for f in os.listdir(task_path) if f.endswith(".json"))
    if not files:
        return {"error": "Нет доступных заданий"}
    latest = files[-1]
    async with aiofiles.open(os.path.join(task_path, latest), "r") as f:
        content = await f.read()
    return {"filename": latest, "content": content}

@app.post("/submit")
async def submit(file: UploadFile = File(...), team: str = Depends(verify_token)):
    db = SessionLocal()
    sub_path = os.path.join(BASE_DIR, "submissions")
    os.makedirs(sub_path, exist_ok=True)
    filename = f"{team}_{datetime.utcnow().isoformat()}.json"
    path = os.path.join(sub_path, filename)
    async with aiofiles.open(path, "wb") as out:
        content = await file.read()
        await out.write(content)
    sub = Submission(team_name=team, task_file="unknown", submission_file=filename, received_at=datetime.utcnow())
    db.add(sub)
    db.commit()
    return {"status": "received"}