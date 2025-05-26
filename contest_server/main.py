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
import json
import logging
from fastapi import HTTPException

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    # Отправляем статус подключения всем клиентам
    status_message = json.dumps({
        "type": "TEAM_STATUS",
        "status": {
            "team": team,
            "connected": True
        }
    })
    await ws_manager.broadcast(status_message)
    try:
        while True:
            await websocket.receive_text()
    except:
        ws_manager.disconnect(team)
        # Отправляем статус отключения всем клиентам
        status_message = json.dumps({
            "type": "TEAM_STATUS",
            "status": {
                "team": team,
                "connected": False
            }
        })
        await ws_manager.broadcast(status_message)

@app.post("/register")
def register(name: str = Form(...)):
    logger.info(f"Получен запрос на регистрацию команды: {name}")
    db = SessionLocal()
    try:
        logger.info("Создание JWT токена...")
        token = create_token(name)
        logger.info("Создание записи команды в БД...")
        team = Team(name=name, token=token)
        db.add(team)
        logger.info("Сохранение в БД...")
        db.commit()
        logger.info(f"Команда {name} успешно зарегистрирована")
        return {"token": token}
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {str(e)}")
        logger.exception("Полный стек ошибки:")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

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
    
    # Получаем время начала обработки
    submission_time = datetime.utcnow()
    
    filename = f"{team}_{submission_time.isoformat()}.json"
    path = os.path.join(SUBMISSIONS_DIR, filename)
    
    try:
        async with aiofiles.open(path, "wb") as out:
            content = await file.read()
            await out.write(content)
        
        # Проверяем валидность JSON и наличие необходимых полей
        try:
            solution = json.loads(content)
            if "selections" not in solution:
                raise ValueError("Missing 'selections' field")
            
            status = "SUCCESS"
        except json.JSONDecodeError:
            status = "INVALID_JSON"
        except ValueError as e:
            status = "INVALID_FORMAT"
        except Exception as e:
            status = "ERROR"
            
        # Вычисляем время обработки
        processing_time = int((datetime.utcnow() - submission_time).total_seconds() * 1000)
        
        sub = Submission(
            team_name=team,
            task_file="unknown",  # TODO: добавить связь с текущей задачей
            submission_file=filename,
            received_at=submission_time,
            submitted_at=datetime.utcnow(),
            processing_time=processing_time,
            status=status
        )
        db.add(sub)
        db.commit()

        # Отправляем статус решения всем клиентам
        status_message = json.dumps({
            "type": "SUBMISSION_STATUS",
            "status": {
                "team": team,
                "taskId": len(os.listdir(TASKS_DIR)) - 1,  # Индекс текущей задачи
                "status": "accepted" if status == "SUCCESS" else "submitted"
            }
        })
        await ws_manager.broadcast(status_message)
        
        return {"status": status, "processing_time": processing_time}
        
    except Exception as e:
        logger.error(f"Error processing submission: {str(e)}")
        return {"status": "ERROR", "message": str(e)}
    finally:
        db.close()
