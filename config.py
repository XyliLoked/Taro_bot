import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Токен бота Telegram
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    # API ключ OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Альтернативно можно использовать другие API
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY', '')
    
    # Настройки базы данных
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///tarot_bot.db')
    
    # Настройки ИИ
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
    AI_TEMPERATURE = float(os.getenv('AI_TEMPERATURE', '0.7'))
    
    # Лимиты
    MAX_DAILY_READINGS = int(os.getenv('MAX_DAILY_READINGS', '3'))
    
config = Config()