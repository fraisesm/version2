import asyncio
import json
import random
import aiohttp
import websockets
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParticipantEmulator:
    def __init__(self, server_url="http://127.0.0.1:8000", ws_url="ws://127.0.0.1:8000"):
        self.server_url = server_url
        self.ws_url = ws_url
        self.token = None
        self.team_name = f"team_{random.randint(1000, 9999)}"
        self.ws = None
        self.is_running = False
        self.reconnect_delay = 1  # Starting delay for exponential backoff
        self.max_retries = 5  # Максимальное количество попыток для операций
        self.current_task = None  # Текущее задание
        self.pending_solution = None  # Ожидающее отправки решение

    async def register(self):
        """Регистрация команды и получение токена"""
        try:
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field('name', self.team_name)
                logger.info(f"Attempting to register team {self.team_name}")
                async with session.post(f"{self.server_url}/register", data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.token = result["token"]
                        logger.info(f"Успешная регистрация команды {self.team_name}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка регистрации: статус {response.status}, ответ: {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Ошибка при регистрации: {str(e)}")
            return False

    async def get_task(self):
        """Получение задания от сервера"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.token}"}
                async with session.get(f"{self.server_url}/task", headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Ошибка получения задания: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Ошибка при получении задания: {e}")
            return None

    async def submit_solution(self, solution):
        """Отправка решения на сервер"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.token}"}
                data = aiohttp.FormData()
                data.add_field('file', 
                             json.dumps(solution),
                             filename='solution.json',
                             content_type='application/json')
                
                async with session.post(f"{self.server_url}/submit", headers=headers, data=data) as response:
                    if response.status == 200:
                        logger.info("Решение успешно отправлено")
                        return True
                    else:
                        logger.error(f"Ошибка отправки решения: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Ошибка при отправке решения: {e}")
            return False

    def generate_solution(self, task_content):
        """Генерация решения с случайными координатами"""
        try:
            task_data = json.loads(task_content)
            text_length = len(task_data.get("text", ""))
            if text_length < 2:  # Проверка на минимальную длину текста
                return None
            
            start = random.randint(0, max(0, text_length - 10))
            end = random.randint(start + 1, min(text_length, start + 10))  # Уменьшил максимальный диапазон
            
            return {
                "selections": [
                    {
                        "type": "ЛОГИЧЕСКАЯ ОШИБКА",
                        "startSelection": start,
                        "endSelection": end
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Ошибка при генерации решения: {e}")
            return None

    async def submit_with_retry(self, solution, max_retries=None):
        """Отправка решения с автоматическими повторными попытками"""
        if max_retries is None:
            max_retries = self.max_retries
            
        retries = 0
        while retries < max_retries:
            try:
                if await self.submit_solution(solution):
                    self.pending_solution = None
                    return True
                    
                retries += 1
                await asyncio.sleep(min(2 ** retries, 30))  # Экспоненциальная задержка
                
            except Exception as e:
                logger.error(f"Попытка {retries + 1} не удалась: {e}")
                retries += 1
                if retries == max_retries:
                    self.pending_solution = solution  # Сохраняем для последующей отправки
                    return False
                await asyncio.sleep(min(2 ** retries, 30))
        
        return False

    async def handle_websocket(self):
        """Обработка WebSocket соединения с улучшенным механизмом переподключения"""
        while self.is_running:
            try:
                async with websockets.connect(f"{self.ws_url}/ws/{self.team_name}") as websocket:
                    self.ws = websocket
                    self.reconnect_delay = 1  # Сброс задержки при успешном подключении
                    logger.info("WebSocket подключение установлено")
                    
                    # Проверяем наличие ожидающего решения
                    if self.pending_solution:
                        logger.info("Отправка ожидающего решения после переподключения...")
                        await self.submit_with_retry(self.pending_solution)
                    
                    while self.is_running:
                        try:
                            message = await websocket.recv()
                            logger.info(f"Получено сообщение: {message}")
                            
                            # Обработка нового задания
                            try:
                                task_data = json.loads(message)
                                self.current_task = task_data
                                # Генерация и отправка решения с задержкой
                                await self.process_task(task_data)
                            except json.JSONDecodeError:
                                logger.error("Получено некорректное JSON сообщение")
                            
                        except websockets.ConnectionClosed:
                            logger.warning("WebSocket соединение закрыто")
                            break
                        
            except Exception as e:
                logger.error(f"Ошибка WebSocket соединения: {e}")
                if self.is_running:
                    await asyncio.sleep(self.reconnect_delay)
                    self.reconnect_delay = min(self.reconnect_delay * 2, 60)
                    continue

    async def process_task(self, task_data):
        """Обработка полученного задания"""
        # Случайная задержка 1-5 секунд
        delay = random.uniform(1, 5)
        await asyncio.sleep(delay)
        
        # Генерация решения
        solution = self.generate_solution(json.dumps(task_data))
        if solution:
            # Отправка с автоматическими повторными попытками
            await self.submit_with_retry(solution)

    async def main_loop(self):
        """Основной цикл работы эмулятора"""
        self.is_running = True
        
        if not await self.register():
            logger.error("Не удалось зарегистрироваться")
            return

        # Запуск WebSocket обработчика
        websocket_task = asyncio.create_task(self.handle_websocket())
        
        while self.is_running:
            try:
                # Получение задания
                task = await self.get_task()
                if task and "content" in task:
                    # Случайная задержка 1-5 секунд
                    delay = random.uniform(1, 5)
                    await asyncio.sleep(delay)
                    
                    # Генерация и отправка решения
                    solution = self.generate_solution(task["content"])
                    if solution:
                        success = await self.submit_solution(solution)
                        if not success:
                            logger.info("Повторная попытка отправки решения...")
                            await asyncio.sleep(1)
                            await self.submit_solution(solution)
                
                await asyncio.sleep(1)  # Пауза между итерациями
                
            except Exception as e:
                logger.error(f"Ошибка в основном цикле: {e}")
                await asyncio.sleep(1)

        # Отмена WebSocket задачи при остановке
        websocket_task.cancel()

    def stop(self):
        """Остановка эмулятора"""
        self.is_running = False
        logger.info("Эмулятор остановлен")

async def main():
    # Создаем несколько эмуляторов
    num_teams = 10  # Количество команд
    emulators = []
    
    for i in range(num_teams):
        emulator = ParticipantEmulator()
        emulators.append(emulator)
    
    try:
        # Запускаем все эмуляторы одновременно
        tasks = [emulator.main_loop() for emulator in emulators]
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        for emulator in emulators:
            emulator.stop()

if __name__ == "__main__":
    asyncio.run(main())
