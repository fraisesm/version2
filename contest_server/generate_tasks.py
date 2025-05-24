import json
import os

TASKS_DIR = "contest_server/tasks"
os.makedirs(TASKS_DIR, exist_ok=True)

# Текстовый шаблон
base_text = "Это пример задания №{id}. Найдите логическую ошибку или несоответствие в тексте."

# Генерация 50 файлов
for i in range(1, 51):
    task = {
        "id": i,
        "text": base_text.format(id=i),
        "selections": []
    }

    filename = os.path.join(TASKS_DIR, f"task_{i:03}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)

print("[OK] Сгенерировано 50 заданий в папке:", TASKS_DIR)
