import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import shutil
import os
from websocket import ws_manager
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TASK_POOL_DIR = "tasks_pool"  # задания тут
TASK_OUT_DIR = "tasks"        # выдача сюда

issued_task_index = 1
total_tasks = 50

async def issue_task():
    global issued_task_index
    if issued_task_index > total_tasks:
        logger.info("[SCHEDULER] Все задания выданы.")
        return

    src_file = os.path.join(TASK_POOL_DIR, f"task_{issued_task_index:03}.json")
    dst_file = os.path.join(TASK_OUT_DIR, f"task_{issued_task_index:03}.json")

    try:
        # Копируем файл задания
        shutil.copy(src_file, dst_file)
        
        # Читаем содержимое задания для отправки через WebSocket
        with open(src_file, 'r', encoding='utf-8') as f:
            task_content = json.load(f)
        
        # Добавляем метаданные
        task_data = {
            "task_id": issued_task_index,
            "timestamp": datetime.now().isoformat(),
            "content": task_content
        }
        
        # Отправляем всем подключенным клиентам
        await ws_manager.broadcast(json.dumps(task_data))
        
        logger.info(f"[SCHEDULER] [{datetime.now()}] Выдано задание {issued_task_index}/{total_tasks}: task_{issued_task_index:03}.json")
        issued_task_index += 1
        
    except FileNotFoundError:
        logger.error(f"[SCHEDULER] Файл {src_file} не найден.")
    except Exception as e:
        logger.error(f"[SCHEDULER] Ошибка при выдаче задания: {e}")

def start_scheduler():
    """Запуск планировщика задач"""
    try:
        os.makedirs(TASK_OUT_DIR, exist_ok=True)
        scheduler = AsyncIOScheduler()
        scheduler.add_job(issue_task, "interval", seconds=30)
        scheduler.start()
        logger.info("[SCHEDULER] Планировщик успешно запущен")
    except Exception as e:
        logger.error(f"[SCHEDULER] Ошибка при запуске планировщика: {e}")
