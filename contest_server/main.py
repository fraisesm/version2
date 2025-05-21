from fastapi import FastAPI, UploadFile, File, Depends, Form, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from auth import create_token, verify_token
from database import SessionLocal, init_db
from models import Team, Submission
from datetime import datetime
import aiofiles
import os
import glob
from scheduler import start_scheduler
from websocket import ws_manager

app = FastAPI()

# Разрешаем CORS для всех (для отладки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = "contest_server"
TASKS_DIR = "tasks"
SUBMISSIONS_DIR = "submissions"

@app.on_event("startup")
async def startup_event():
    print("[STARTUP] Инициализация...")

    # Инициализация БД
    init_db()

    # Очистка и создание папок
    os.makedirs(TASKS_DIR, exist_ok=True)
    os.makedirs(SUBMISSIONS_DIR, exist_ok=True)
    for file in glob.glob(f"{TASKS_DIR}/*.json"):
        os.remove(file)
    for file in glob.glob(f"{SUBMISSIONS_DIR}/*.json"):
        os.remove(file)
    print("[CLEANUP] tasks/ и submissions/ очищены")

    # Запуск планировщика
    start_scheduler()

    print("[STARTUP] Сервер готов.")

@app.websocket("/ws/{team}")
async def websocket_endpoint(websocket: WebSocket, team: str):
    await ws_manager.connect(team, websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        ws_manager.disconnect(team)

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
    task_path = TASKS_DIR
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
    os.makedirs(SUBMISSIONS_DIR, exist_ok=True)
    filename = f"{team}_{datetime.utcnow().isoformat()}.json"
    path = os.path.join(SUBMISSIONS_DIR, filename)
    async with aiofiles.open(path, "wb") as out:
        content = await file.read()
        await out.write(content)
    sub = Submission(team_name=team, task_file="unknown", submission_file=filename, received_at=datetime.utcnow())
    db.add(sub)
    db.commit()
    return {"status": "received"}
