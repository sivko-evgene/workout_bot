# bot.py
import requests
import time
import re
from config import Config
from database import db
from workout_parser import WorkoutParser


class SimpleTelegramBot:
    def __init__(self):
        self.token = Config.BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.offset = None

    def get_updates(self):
        """Получает новые сообщения"""
        url = f"{self.base_url}/getUpdates"
        params = {'offset': self.offset, 'timeout': 30}

        try:
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ Ошибка получения updates: {e}")
        return {'ok': False, 'result': []}

    def send_message(self, chat_id, text):
        """Отправляет сообщение"""
        url = f"{self.base_url}/sendMessage"
        data = {'chat_id': chat_id, 'text': text}

        try:
            response = requests.post(url, data=data)
            return response.json()
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения: {e}")
            return {'ok': False}

    def save_workout_to_db(self, user_id, text, username):
        """Сохраняет тренировку в базу данных"""
        try:
            # Проверяем структурированная ли это тренировка
            if WorkoutParser.is_structured_workout(text):
                parsed_workouts = WorkoutParser.parse_workout_message(text)

                if parsed_workouts:
                    saved_count = 0
                    for workout in parsed_workouts:
                        success = db.save_workout(user_id, workout)
                        if success:
                            saved_count += 1
                            print(
                                f"💪 Упражнение сохранено: {workout['exercise']} - {workout['weight_kg']}kg × {workout['repetition']}")

                    return saved_count > 0
                else:
                    print("❌ Не удалось распарсить структурированную тренировку")
                    return False
            else:
                # Простое сообщение - сохраняем как есть
                workout_data = {
                    'exercise': f"Сообщение: {text[:100]}",
                    'weight_kg': 0,
                    'repetition': 0,
                    'set_number': 1,
                    'day': 'unknown',
                    'status_approach': 'info',
                    'notes': f'Пользователь: @{username}'
                }

                success = db.save_workout(user_id, workout_data)
                return success

        except Exception as e:
            print(f"❌ Ошибка сохранения в базу: {e}")
            return False

    def process_message(self, message):
        """Обрабатывает сообщение"""
        chat_id = message['chat']['id']
        text = message.get('text', '')
        user = message.get('from', {})
        user_id = user.get('id')
        username = user.get('username', f"user_{user_id}")
        first_name = user.get('first_name', 'User')

        print(f"👤 {first_name} (@{username}) написал: {text[:50]}...")

        # Сохраняем в базу данных
        db_success = self.save_workout_to_db(user_id, text, username)

        # Отправляем ответ
        if text == '/start' or text.lower() == 'go_go':
            welcome = (
                "🏋️ Добро пожаловать в Workout Bot!\n\n"
                "📝 Отправляйте структурированные тренировки в формате:\n\n"
                "push\n"
                "дата\n"
                "exercise_name\n"
                "Сет 1: 15 kg × 10\n"
                "Сет 2: 20 kg × 8\n\n"
                "Или просто текстовые сообщения для заметок."
            )
            self.send_message(chat_id, welcome)

        elif text == '/help':
            help_text = (
                "📋 Формат структурированных тренировок:\n\n"
                "push/pull\n"
                "дата\n"
                "название_упражнения\n"
                "Сет 1: вес kg × повторения\n"
                "Сет 2: вес kg × повторения\n\n"
                "Пример:\n"
                "push\n"
                "воскресенье, 23 ноября 2025 г. в 11:33\n"
                "chest_press_dumbbell\n"
                "Сет 1: 15 kg × 10\n"
                "Сет 2: 20 kg × 8"
            )
            self.send_message(chat_id, help_text)

        else:
            if WorkoutParser.is_structured_workout(text):
                response = (
                    f"✅ Структурированная тренировка получена!\n"
                    f"💾 Данные разобраны и сохранены в базу\n"
                    f"📊 Обработано упражнений из сообщения"
                )
            else:
                response = (
                    f"✅ Сообщение получено!\n"
                    f"💾 Сохранено в базу как заметка\n"
                    f"📝 Для структурированных данных используйте формат из /help"
                )
            self.send_message(chat_id, response)

    def run(self):
        """Запускает бота"""
        print("🤖 Умный бот с парсером запущен!")
        print("📱 Перейди в Telegram и напиши @workout_500_tg_bot")
        print("💾 Сохраняет структурированные тренировки и заметки")
        print("⏹️  Для остановки нажми Ctrl+C")

        while True:
            try:
                updates = self.get_updates()

                if updates.get('ok') and updates['result']:
                    for update in updates['result']:
                        self.offset = update['update_id'] + 1

                        if 'message' in update:
                            self.process_message(update['message'])

                time.sleep(1)

            except KeyboardInterrupt:
                print("\n🛑 Бот остановлен")
                break
            except Exception as e:
                print(f"❌ Ошибка в основном цикле: {e}")
                time.sleep(5)


# Создаем глобальный экземпляр бота
workout_bot = SimpleTelegramBot()
