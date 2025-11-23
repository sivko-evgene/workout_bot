# workout_parser.py
import re
from datetime import datetime


class WorkoutParser:
    @staticmethod
    def parse_workout_message(text):
        """
        Парсит структурированное сообщение о тренировке
        Обрабатывает упражнения, сеты и заметки для каждого упражнения
        """
        lines = text.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]

        if len(lines) < 4:
            return None

        parsed_data = []

        try:
            day = lines[0].lower()  # push/pull

            # Группируем упражнения с их сетами и заметками
            exercises = []
            current_exercise = None
            current_sets = []
            current_notes = "unknown"

            for i in range(2, len(lines)):  # Начинаем с третьей строки
                line = lines[i]

                # Пропускаем пустые строки, даты и URL
                if (not line or
                        any(date_word in line.lower() for date_word in ['г.', 'в', '2025']) or
                        line.startswith('http')):
                    continue

                # Если нашли заметки - сохраняем для текущего упражнения
                if line.lower().startswith('заметки:'):
                    notes_text = line[8:].strip()  # Убираем "Заметки:"
                    current_notes = notes_text if notes_text else "unknown"
                    continue

                # Если нашли новое упражнение
                if (not line.lower().startswith('сет') and
                        not line.lower().startswith('заметки:') and
                        not any(word in line.lower() for word in ['push', 'pull', 'legs'])):

                    # Сохраняем предыдущее упражнение если есть
                    if current_exercise and current_sets:
                        exercises.append({
                            'name': current_exercise,
                            'sets': current_sets.copy(),
                            'notes': current_notes
                        })

                    # Начинаем новое упражнение
                    current_exercise = line
                    current_sets = []
                    current_notes = "unknown"  # Сбрасываем заметки
                    continue

                # Если нашли сет
                if line.lower().startswith('сет'):
                    set_data = WorkoutParser.parse_set_line(line)
                    if set_data and current_exercise:
                        current_sets.append(set_data)

            # Сохраняем последнее упражнение
            if current_exercise and current_sets:
                exercises.append({
                    'name': current_exercise,
                    'sets': current_sets.copy(),
                    'notes': current_notes
                })

            # Создаем финальные данные для базы
            for exercise in exercises:
                for set_num, set_data in enumerate(exercise['sets'], 1):
                    parsed_data.append({
                        'day': day,
                        'exercise': exercise['name'],
                        'set_number': set_num,
                        'weight_kg': set_data['weight'],
                        'repetition': set_data['repetition'],
                        'status_approach': 'completed',
                        'notes': exercise['notes']
                    })

        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")
            import traceback
            traceback.print_exc()
            return None

        return parsed_data if parsed_data else None

    @staticmethod
    def parse_set_line(set_line):
        """Парсит строку сета: 'Сет 1: 15 kg × 10'"""
        try:
            # Ищем вес и повторения
            match = re.search(r'(\d+\.?\d*)\s*kg\s*×\s*(\d+)', set_line.lower())
            if match:
                weight = float(match.group(1))
                repetition = int(match.group(2))
                return {'weight': weight, 'repetition': repetition}

            # Альтернативный формат с кириллицей
            match = re.search(r'(\d+\.?\d*)\s*кг\s*×\s*(\d+)', set_line.lower())
            if match:
                weight = float(match.group(1))
                repetition = int(match.group(2))
                return {'weight': weight, 'repetition': repetition}

        except Exception as e:
            print(f"❌ Ошибка парсинга сета '{set_line}': {e}")
        return None

    @staticmethod
    def is_structured_workout(text):
        """Проверяет, является ли сообщение структурированной тренировкой"""
        lines = text.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]

        if len(lines) < 4:
            return False

        # Проверяем формат
        first_line = lines[0].lower()
        if first_line not in ['push', 'pull', 'legs']:
            return False

        # Должны быть строки с "Сет"
        set_lines = [line for line in lines if 'сет' in line.lower()]
        if len(set_lines) < 1:
            return False

        return True
