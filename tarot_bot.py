# tarot_bot.py
import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from spreads import TarotSpread  # Ваш класс из spreads.py

# Загружаем токен
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Создаем объект для раскладов
spreader = TarotSpread(gptunnel_api_key=os.getenv("GPTUNNEL_API_KEY"))

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
    await update.message.reply_text(
        "🔮 Добро пожаловать в бот Таро!\n\n"
        "Я помогу вам сделать расклад на любую тему. Выберите тип расклада:",
        reply_markup=main_keyboard
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    await update.message.reply_text(
        "🔮 Как пользоваться ботом:\n\n"
        "1. Выберите тип расклада из меню\n"
        "2. Напишите ваш вопрос\n"
        "3. Получите интерпретацию\n\n"
        "Доступные расклады:\n"
        "- Три карты (прошлое/настоящее/будущее)\n"
        "- Отношения (5 карт)\n"
        "- Карьера (4 карты)\n"
        "- Карта дня (совет на сегодня)"
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
    """Обработка вопроса и выполнение расклада"""
    question = update.message.text
    spread_type = context.user_data.get('spread_type', 'Три карты')
    
    await update.message.reply_text("🔮 Делаю расклад... Подождите немного...")
    
    try:
        # Выполняем нужный расклад
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
        
        # Отправляем результат
        response = f"🔮 *{result['name']}*\n\n"
        response += f"📝 *Вопрос:* {question}\n\n"
        response += f"{result['interpretation']}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена"""
    await update.message.reply_text("❌ Отменено")
    return ConversationHandler.END

def main():
    """Запуск бота"""
    print("🔄 Запуск бота Таро...")
    
    app = Application.builder().token(TOKEN).build()
    
    # Диалог для раскладов
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r'^(🔮 Три карты|💖 Отношения|💼 Карьера|🌟 Карта дня)$'), handle_spread_choice)],
        states={
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(conv_handler)
    
    print("✅ Бот запущен! Напишите /start в Telegram")
    app.run_polling()

if __name__ == "__main__":
    main()