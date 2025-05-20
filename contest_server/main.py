from fastapi import FastAPI, UploadFile, File, WebSocket, Depends
from auth import create_token, verify_token
from database import SessionLocal, init_db
from models import Team, Submission
from websocket import ws_manager
from scheduler import start_scheduler
from datetime import datetime
import aiofiles
import os

app = FastAPI()
init_db()
start_scheduler()

@app.post("/register")
def register(name: str):
    db = SessionLocal()
    token = create_token(name)
    team = Team(name=name, token=token)
    db.add(team)
    db.commit()
    return {"token": token}

@app.get("/task")
async def get_task(team: str = Depends(verify_token)):
    # Вернуть путь к последнему заданию
    files = sorted(os.listdir("tasks"))
    if not files:
        return {"error": "Нет доступных заданий"}
    latest = files[-1]
    async with aiofiles.open(f"tasks/{latest}", "r") as f:
        content = await f.read()
    return {"filename": latest, "content": content}

@app.post("/submit")
async def submit(file: UploadFile = File(...), team: str = Depends(verify_token)):
    db = SessionLocal()
    filename = f"{team}_{datetime.utcnow().isoformat()}.json"
    path = f"submissions/{filename}"
    async with aiofiles.open(path, "wb") as out:
        content = await file.read()
        await out.write(content)
    sub = Submission(team_name=team, task_file="unknown", submission_file=filename, received_at=datetime.utcnow())
    db.add(sub)
    db.commit()
    return {"status": "received"}

@app.websocket("/ws/{team}")
async def websocket_endpoint(websocket: WebSocket, team: str):
    await ws_manager.connect(team, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"[WS] {team}: {data}")
            await websocket.send_text(f"Echo: {data}")
    except Exception:
        ws_manager.disconnect(team)
