# database.py
import requests
from datetime import datetime
from config import Config


class Database:
    def __init__(self):
        self.url = Config.SUPABASE_URL
        self.key = Config.SUPABASE_KEY
        self.headers = {
            'Authorization': f'Bearer {self.key}',
            'apikey': self.key,
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }

    def save_workout(self, user_id, exercise_data):
        """Сохраняет тренировку в базу"""
        try:
            data = {
                'user_id': user_id,
                'date': datetime.now().isoformat(),
                'day': exercise_data.get('day', 'unknown'),
                'exercise': exercise_data.get('exercise', 'unknown'),
                'set_number': exercise_data.get('set_number', 1),
                'weight_kg': exercise_data.get('weight_kg', 0),
                'repetition': exercise_data.get('repetition', 0),
                'status_approach': exercise_data.get('status_approach', 'completed'),
                'notes': exercise_data.get('notes', '')
            }

            response = requests.post(
                f"{self.url}/rest/v1/workout_progress",
                headers=self.headers,
                json=data,
                timeout=10
            )

            if response.status_code in [200, 201]:
                print(f"✅ Упражнение сохранено: {data['exercise']} - {data['weight_kg']}kg × {data['repetition']}")
                return True
            else:
                print(f"❌ Ошибка сохранения: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Исключение при сохранении: {e}")
            return False


# Глобальный экземпляр
db = Database()
