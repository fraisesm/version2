import requests
import time
import random
import json
import os

# === Настройки ===
API_URL = "http://localhost:8000"  # Адрес сервера
TEAM_NAME = "Команда_1"            # Имя команды
HEADERS = {}

# === Регистрация команды и получение токена ===
def register_team():
    global HEADERS
    try:
        response = requests.post(f"{API_URL}/register", data={"name": TEAM_NAME})
        response.raise_for_status()
        token = response.json()["token"]
        HEADERS = {"Authorization": f"Bearer {token}"}
        print(f"[OK] Получен токен для команды '{TEAM_NAME}'")
    except Exception as e:
        print(f"[Ошибка регистрации] {e}")
        exit(1)

# === Получение задания ===
def get_task():
    try:
        response = requests.get(f"{API_URL}/task", headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if "content" not in data:
            print("[!] Нет доступных заданий")
            return None, None
        return data["filename"], json.loads(data["content"])
    except Exception as e:
        print(f"[Ошибка получения задания] {e}")
        return None, None

# === Создание фейкового решения ===
def create_solution(task_json):
    task_json["selections"] = [{
        "type": "ЛОГИЧЕСКАЯ ОШИБКА",
        "startSelection": 5,
        "endSelection": 223
    }]
    filename = "solution.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(task_json, f, ensure_ascii=False, indent=2)
    return filename

# === Отправка решения ===
def send_solution(filepath):
    try:
        with open(filepath, "rb") as f:
            response = requests.post(f"{API_URL}/submit", headers=HEADERS, files={"file": f})
            response.raise_for_status()
            print(f"[OK] Решение отправлено: {response.json()}")
    except Exception as e:
        print(f"[Ошибка отправки решения] {e}")

# === Основной цикл работы эмулятора ===
def main_loop():
    while True:
        filename, task_json = get_task()
        if not task_json:
            time.sleep(5)
            continue

        print(f"[->] Получено задание: {filename}")

        delay = random.randint(1, 5)
        print(f"[~] Имитируем работу... ждём {delay} сек")
        time.sleep(delay)

        solution_path = create_solution(task_json)
        send_solution(solution_path)

        print("[=] Ждём 30 секунд до следующего задания\n")
        time.sleep(30)

# === Точка входа ===
if __name__ == "__main__":
    register_team()
    main_loop()
