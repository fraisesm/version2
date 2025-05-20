from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import shutil
import os

task_counter = 1

def issue_task():
    global task_counter
    if task_counter > 50:
        return
    src = "tasks/template.json"
    dst = f"tasks/task_{task_counter:03}.json"
    shutil.copy(src, dst)
    print(f"[{datetime.now()}] Issued: {dst}")
    task_counter += 1

def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(issue_task, "interval", seconds=30)
    scheduler.start()
