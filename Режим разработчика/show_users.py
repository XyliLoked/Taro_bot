# show_users.py
import sys
import os

# Добавляем путь к родительской папке
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import db

def show_all_users():
    """Показать всех пользователей и их ID"""
    session = db.Session()
    try:
        from database import User
        users = session.query(User).all()
        
        if not users:
            print("📭 Нет пользователей в базе")
            return
        
        print("📋 СПИСОК ПОЛЬЗОВАТЕЛЕЙ:")
        print("=" * 60)
        for user in users:
            print(f"🆔 Telegram ID: {user.telegram_id}")
            print(f"📝 Имя: {user.first_name} {user.last_name or ''}")
            print(f"📛 Username: @{user.username}" if user.username else "📛 Username: нет")
            print(f"📅 Зарегистрирован: {user.created_at}")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    show_all_users()