# main.py
from bot import workout_bot

def main():
    print("🚀 Запуск Workout Bot (простая версия)...")
    try:
        workout_bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
