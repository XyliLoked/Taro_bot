# clear_db.py
import sys
import os

# Добавляем путь к родительской папке, чтобы найти database.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database import db
from sqlalchemy import text

def clear_all_readings():
    """Очистить ВСЕ расклады всех пользователей"""
    session = db.Session()
    try:
        # Простой способ
        session.execute(text("DELETE FROM readings;"))
        session.commit()
        print("✅ Все расклады удалены!")
    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка: {e}")
    finally:
        session.close()

def clear_user_readings(telegram_id):
    """Очистить расклады конкретного пользователя"""
    session = db.Session()
    try:
        session.execute(
            text("DELETE FROM readings WHERE user_id = :user_id"),
            {"user_id": telegram_id}
        )
        session.commit()
        print(f"✅ Расклады пользователя {telegram_id} удалены!")
    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    print("1. Очистить ВСЕ расклады")
    print("2. Очистить расклады пользователя")
    
    choice = input("Выберите действие (1/2): ")
    
    if choice == "1":
        confirm = input("Точно очистить ВСЮ историю? (да/нет): ")
        if confirm.lower() == "да":
            clear_all_readings()
    elif choice == "2":
        user_id = input("Введите Telegram ID пользователя: ")
        try:
            clear_user_readings(int(user_id))
        except:
            print("❌ Некорректный ID")