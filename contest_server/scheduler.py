TASK_POOL_DIR = "tasks_pool"  # задания тут
TASK_OUT_DIR = "tasks"        # выдача сюда

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import shutil
import os

issued_task_index = 1

def issue_task():
    global issued_task_index
    if issued_task_index > 50:
        print("[INFO] Все задания выданы.")
        return

    src_file = os.path.join(TASK_POOL_DIR, f"task_{issued_task_index:03}.json")
    dst_file = os.path.join(TASK_OUT_DIR, f"task_{issued_task_index:03}.json")

    try:
        shutil.copy(src_file, dst_file)
        print(f"[{datetime.now()}] Выдано задание: task_{issued_task_index:03}.json")
        issued_task_index += 1
    except FileNotFoundError:
        print(f"[ОШИБКА] Файл {src_file} не найден.")
    except Exception as e:
        print(f"[ОШИБКА] {e}")

def start_scheduler():
    os.makedirs(TASK_OUT_DIR, exist_ok=True)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(issue_task, "interval", seconds=30)
    scheduler.start()
