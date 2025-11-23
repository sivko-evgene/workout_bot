# config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен в .env файле")
        if not cls.SUPABASE_URL:
            raise ValueError("SUPABASE_URL не установлен в .env файле")
        if not cls.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY не установлен в .env файле")


Config.validate()

if __name__ == "__main__":
    print("✅ Конфигурация загружена успешно!")
    print(f"🤖 BOT_TOKEN: {'***' + Config.BOT_TOKEN[-5:] if Config.BOT_TOKEN else 'НЕТ'}")
    print(f"🗄️ SUPABASE_URL: {Config.SUPABASE_URL[:30]}...")
