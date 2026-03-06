# tarot_bot.py
import os
import json  # <-- Импорт для работы с JSON
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.request import HTTPXRequest
from spreads import TarotSpread
from database import db
from config import config

# Загружаем токен
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
GPTUNNEL_KEY = os.getenv("GPTUNNEL_API_KEY")


# Создаем кастомный request с правильными таймаутами
request = HTTPXRequest(
    connect_timeout=30.0,
    read_timeout=30.0,
    write_timeout=30.0,
    pool_timeout=30.0
)

# Создаем объект для раскладов
spreader = TarotSpread(gptunnel_api_key=GPTUNNEL_KEY)

# Состояния для диалога
QUESTION = 1

# Кнопки меню
main_keyboard = ReplyKeyboardMarkup([
    ["🔮 Три карты", "💖 Отношения"],
    ["💼 Карьера", "🌟 Карта дня"],
    ["❓ Помощь"]
], resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие"""
    user = update.effective_user
    db.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    await update.message.reply_text(
        "🔮 Добро пожаловать в бот Таро!\n\n"
        "Я помогу вам сделать расклад на любую тему. Выберите тип расклада:",
        reply_markup=main_keyboard
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    await update.message.reply_text(
        "🔮 *Как пользоваться ботом:*\n\n"
        "1. Выберите тип расклада из меню\n"
        "2. Напишите ваш вопрос\n"
        "3. Получите интерпретацию\n\n"
        "*Доступные расклады:*\n"
        "🔮 Три карты - прошлое/настоящее/будущее\n"
        "💖 Отношения - анализ отношений\n"
        "💼 Карьера - вопросы работы\n"
        "🌟 Карта дня - совет на сегодня\n\n"
        "*Команды:*\n"
        "/history - история раскладов",
        parse_mode='Markdown'
    )

async def handle_spread_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора расклада"""
    choice = update.message.text
    context.user_data['spread_type'] = choice
    
    await update.message.reply_text(
        f"Вы выбрали: {choice}\n\n"
        "Теперь напишите ваш вопрос (или отправьте 'любой' для общего расклада):"
    )
    return QUESTION

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка вопроса и выполнение расклада с проверкой на повторы"""
    question = update.message.text
    user = update.effective_user
    spread_type = context.user_data.get('spread_type', '🔮 Три карты')
    
    if question == "❌ Нет, спасибо" and context.user_data.get('after_history'):
        del context.user_data['after_history']
        
        await update.message.reply_text(
            "Хорошо! Если захотите сделать расклад позже - просто выберите тип расклада в меню.",
            reply_markup=main_keyboard
        )
        keys_to_clear = ['pending_question', 'existing_reading', 'spread_type', 'current_question', 'after_history']
        for key in keys_to_clear:
            if key in context.user_data:
                del context.user_data[key]
        return ConversationHandler.END
    
    if question in ["✅ Да, хочу новый расклад", "🔄 Уточнить вопрос", "📜 Показать прошлый расклад"]:
        return await handle_choice_after_warning(update, context)
    
    db.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    from datetime import datetime
    today = datetime.now().date()
    
    recent_readings = db.get_user_history(user.id, limit=10)
    
    similar_reading = None
    for reading in recent_readings:
        reading_date = reading.created_at.date()
        if reading_date == today:
            if question.lower() in reading.question.lower() or reading.question.lower() in question.lower():
                similar_reading = reading
                break
    
    if similar_reading:
        context.user_data['pending_question'] = question
        context.user_data['spread_type'] = spread_type
        context.user_data['existing_reading'] = {
            'question': similar_reading.question,
            'interpretation': similar_reading.interpretation,
            'date': similar_reading.created_at
        }
        
        keyboard = [
            ["✅ Да, хочу новый расклад"],
            ["🔄 Уточнить вопрос"],
            ["📜 Показать прошлый расклад"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        
        await update.message.reply_text(
            "🔮 *Вы уже делали расклад на похожий вопрос сегодня.*\n\n"
            "В традиции Таро считается, что повторный расклад на тот же вопрос может запутать, "
            "так как карты показывают текущий момент, который еще не успел измениться.\n\n"
            "Что хотите сделать?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return QUESTION
    
    return await perform_reading(update, context, question, spread_type)

async def handle_choice_after_warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора после предупреждения"""
    choice = update.message.text
    user = update.effective_user
    
    if choice == "✅ Да, хочу новый расклад":
        question = context.user_data.get('pending_question')
        spread_type = context.user_data.get('spread_type', '🔮 Три карты')
        
        await update.message.reply_text("🔮 Хорошо, делаю новый расклад...")
        return await perform_reading(update, context, question, spread_type)
    
    elif choice == "🔄 Уточнить вопрос":
        await update.message.reply_text(
            "📝 Напишите уточненную версию вашего вопроса.\n"
            "Постарайтесь сформулировать его иначе или добавить детали:"
        )
        return QUESTION
    
    elif choice == "📜 Показать прошлый расклад":
        existing = context.user_data.get('existing_reading', {})
        if existing:
            response = f"📜 *Ваш прошлый расклад*\n"
            response += f"📝 *Вопрос:* {existing['question']}\n"
            response += f"🕐 *Когда:* {existing['date'].strftime('%d.%m.%Y %H:%M')}\n\n"
            response += f"{existing['interpretation']}"
            
            try:
                await update.message.reply_text(response, parse_mode='Markdown')
            except:
                clean_response = response.replace('*', '').replace('_', '')
                await update.message.reply_text(clean_response)
            
            context.user_data['after_history'] = True
            
            keyboard = [
                ["✅ Да, хочу новый расклад"],
                ["❌ Нет, спасибо"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            
            await update.message.reply_text(
                "Хотите сделать новый расклад на эту тему?",
                reply_markup=reply_markup
            )
            return QUESTION
        
        return await perform_reading(update, context, 
                                     context.user_data.get('pending_question'), 
                                     context.user_data.get('spread_type'))
    
    elif choice == "❌ Нет, спасибо":
        await update.message.reply_text(
            "Хорошо! Если захотите сделать расклад позже - просто выберите тип расклада в меню.",
            reply_markup=main_keyboard
        )
        keys_to_clear = ['pending_question', 'existing_reading', 'spread_type', 'current_question']
        for key in keys_to_clear:
            if key in context.user_data:
                del context.user_data[key]
        return ConversationHandler.END
    
    else:
        return await perform_reading(update, context, choice, 
                                     context.user_data.get('spread_type', '🔮 Три карты'))

async def perform_reading(update: Update, context: ContextTypes.DEFAULT_TYPE, question: str, spread_type: str):
    """Выполнение расклада"""
    user = update.effective_user
    
    await update.message.reply_text("🔮 Делаю расклад... Подождите немного...")
    
    try:
        if "Три карты" in spread_type:
            result = await spreader.three_card_spread(question)
        elif "Отношения" in spread_type:
            result = await spreader.relationship_spread(question)
        elif "Карьера" in spread_type:
            result = await spreader.career_spread(question)
        elif "Карта дня" in spread_type:
            result = await spreader.daily_spread()
        else:
            result = await spreader.three_card_spread(question)
        
        db.save_reading(
            user_id=user.id,
            spread_type=spread_type,
            question=question,
            cards=result['cards'],
            interpretation=result['interpretation'],
            ai_generated=True
        )
        
        db.increment_reading_count(user.id)
        
        response = f"🔮 *{result['name']}*\n\n"
        response += f"📝 *Вопрос:* {question}\n\n"
        response += f"{result['interpretation']}"
        
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=main_keyboard)
        
        if 'pending_question' in context.user_data:
            del context.user_data['pending_question']
        if 'existing_reading' in context.user_data:
            del context.user_data['existing_reading']
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}", reply_markup=main_keyboard)
    
    return ConversationHandler.END

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать историю раскладов"""
    user = update.effective_user
    
    readings = db.get_user_history(user.id, limit=5)
    
    if not readings:
        await update.message.reply_text("📭 У вас пока нет сохраненных раскладов.")
        return
    
    response = "📜 *Ваши последние расклады:*\n\n"
    
    for i, r in enumerate(readings, 1):
        date = r.created_at.strftime("%d.%m.%Y %H:%M")
        response += f"{i}. *{date}*\n"
        response += f"   🔮 {r.spread_type}\n"
        response += f"   📝 {r.question[:50]}...\n\n"
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена"""
    await update.message.reply_text("❌ Отменено")
    return ConversationHandler.END

# ========== НОВЫЙ ОБРАБОТЧИК ДЛЯ MINI APP (ПРАВИЛЬНОЕ МЕСТО) ==========
async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает данные, отправленные из Mini App"""
    print("\n" + "="*50)
    print("🚨 ПОЛУЧЕН ВЫЗОВ HANDLE_WEB_APP_DATA")
    print("="*50)
    
    # Проверяем, что вообще пришло
    print(f"update: {update}")
    print(f"effective_message: {update.effective_message}")
    
    web_app_data = update.effective_message.web_app_data
    print(f"web_app_data: {web_app_data}")
    
    if not web_app_data:
        print("❌ Нет web_app_data")
        return
    
    try:
        # Логируем сырые данные
        print(f"📦 Сырые данные: {web_app_data.data}")
        
        # Парсим JSON
        data = json.loads(web_app_data.data)
        user = update.effective_user
        print(f"👤 Пользователь: {user.id} (@{user.username})")
        print(f"📊 Распарсенные данные: {data}")
        
        if data.get('action') == 'spread':
            spread_type = data.get('type')
            question = data.get('question', 'Общий вопрос')
            
            print(f"🎯 Тип расклада: {spread_type}")
            print(f"❓ Вопрос: {question}")
            
            # Проверяем наличие метода
            spread_map = {
                'three_cards': spreader.three_card_spread,
                'relationship': spreader.relationship_spread,
                'career': spreader.career_spread,
                'celtic_cross': spreader.celtic_cross_spread,
                'daily': spreader.daily_spread,
                'five_cards': spreader.three_card_spread
            }
            print(f"📋 Доступные методы: {list(spread_map.keys())}")
            
            spread_method = spread_map.get(spread_type)
            if not spread_method:
                print(f"❌ Неизвестный тип расклада: {spread_type}")
                await update.message.reply_text("❌ Неизвестный тип расклада")
                return
            
            # Отправляем подтверждение
            print("📤 Отправляю подтверждение пользователю...")
            await update.message.reply_text("✅ Данные получены! Сейчас сделаю расклад...")
            print("✅ Подтверждение отправлено")
            
            print("🔮 Вызываю spread_method...")
            print(f"🕐 Время: {datetime.now()}")
            
            try:
                result = await spread_method(question)
                print(f"✅ spread_method выполнен")
                print(f"📏 Длина ответа: {len(result.get('interpretation', ''))}")
                print(f"📝 Первые 100 символов ответа: {result.get('interpretation', '')[:100]}")
            except Exception as e:
                print(f"❌ Ошибка в spread_method: {e}")
                import traceback
                traceback.print_exc()
                await update.message.reply_text(f"❌ Ошибка при получении расклада: {e}")
                return
            
            print("💾 Сохраняю в базу данных...")
            try:
                db.save_reading(
                    user_id=user.id,
                    spread_type=result['name'],
                    question=question,
                    cards=result.get('cards', []),
                    interpretation=result['interpretation'],
                    ai_generated=True
                )
                db.increment_reading_count(user.id)
                print("✅ Данные сохранены в БД")
            except Exception as e:
                print(f"❌ Ошибка сохранения в БД: {e}")
            
            # Формируем ответ
            response = f"🔮 *{result['name']}*\n\n"
            response += f"📝 *Вопрос:* {question}\n\n"
            response += result['interpretation']
            print(f"📏 Длина ответа для отправки: {len(response)}")
            
            print("📤 Отправляю ответ пользователю...")
            await update.message.reply_text(
                response, 
                parse_mode='Markdown',
                reply_markup=main_keyboard
            )
            print("✅ Ответ отправлен пользователю")
            
        else:
            print(f"❌ Неизвестное действие: {data.get('action')}")
            
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        print(f"📦 Проблемные данные: {web_app_data.data}")
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*50 + "\n")

def main():
    """Запуск бота"""
    print("🔄 Запуск бота Таро...")
    print(f"Токен Telegram: {TOKEN[:10]}...")
    print(f"Ключ GPTunnel: {GPTUNNEL_KEY[:10]}...")
    
    if not TOKEN or not GPTUNNEL_KEY:
        print("❌ Ошибка: Не найдены токены в .env файле!")
        return
    
    app = Application.builder().token(TOKEN).request(request).build()
    
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^(🔮 Три карты|💖 Отношения|💼 Карьера|🌟 Карта дня)$'), handle_spread_choice)],
        states={
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex('^❓ Помощь$'), help_command))
    
    # ========== ВАЖНО: ДОБАВЛЯЕМ ОБРАБОТЧИК ДЛЯ MINI APP ==========
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    
    print("✅ Бот запущен! Напишите /start в Telegram")
    app.run_polling()
    

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class WebAppHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self._send_cors_headers()
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Tarot Bot is running!")
    
    def do_POST(self):
        self.send_response(200)
        self._send_cors_headers()
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if self.path == '/webapp-data':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                print(f"📥 Получен POST запрос: {data}")
                
                # Проверяем, что это запрос на расклад
                if data.get('action') == 'spread':
                    spread_type = data.get('type')
                    question = data.get('question', 'Общий вопрос')
                    
                    # Здесь нужно получить chat_id!
                    # Пока нет chat_id - не можем отправить ответ
                    print(f"⚠️ Нет chat_id, ответ не будет отправлен")
                    
                    # Временно отправляем тестовый ответ (позже заменим)
                    response_data = {
                        "status": "received", 
                        "message": f"Получен запрос: {spread_type} - {question}"
                    }
                    self.wfile.write(json.dumps(response_data).encode())
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                self.wfile.write(json.dumps({"error": str(e)}).encode())

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), WebAppHandler)
    print(f"📡 HTTP server listening on port {port}")
    server.serve_forever()

# Запускаем HTTP-сервер в отдельном потоке
threading.Thread(target=run_http_server, daemon=True).start()

if __name__ == "__main__":
    main()