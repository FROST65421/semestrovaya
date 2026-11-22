import logging
from datetime import datetime
from typing import List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

from models import User, News, Article, Comment

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

users_db: List[User] = []
news_db: List[News] = []

# Глобальные словари для управления состояниями (строго по заданию)
user_state = {}
user_context = {}
news_message_ids = {}


def init_data():
    global users_db, news_db
    
    names = ["Маткин И.А.", "Илья Петелин", "Абдрахманов Б.Д.", "Наймушин К.В.", 
             "Кривоносов Роман", "Воронцов Максим", "Вахатов В.А.", "Пряхин Дима"]
    for i, name in enumerate(names):
        users_db.append(User(name, f"user_{i+1}"))

    news_db.append(News("Новость 1", "16.09.2026", "Выход патча 7.37 в Dota 2. Изменен баланс Tinker, добавлен новый предмет для саппортов."))
    news_db.append(News("Новость 2", "20.10.2026", "Обновление в CS2. Добавлено новое оружие, улучшен античит и система голосового чата."))
    news_db.append(Article("Новость 3", "26.01.2026", "Технологический прорыв в энергетике.", "Иван Иванов", "Ученые представили новый тип экологически чистых батарей, которые заряжаются за 5 минут."))

    # ✅ Комментарии к Новость 1 (index 0)
    news_db[0].add_comment(Comment(users_db[0], "Я давно этого ждал!"))
    news_db[0].add_comment(Comment(users_db[1], "Наконец-то нормальный патч, баланс улучшен."))
    news_db[0].add_comment(Comment(users_db[2], "Tinker всё ещё имба, нерфите!"))
    news_db[0].add_comment(Comment(users_db[3], "А где скины?!"))

    # ✅ Комментарии к Новость 2 (index 1)
    news_db[1].add_comment(Comment(users_db[4], "Неужели античит добавили..."))
    news_db[1].add_comment(Comment(users_db[5], "Наконец-то нормальное оружие!"))
    news_db[1].add_comment(Comment(users_db[6], "Голосовой чат — это прорыв!"))

    # ✅ Комментарии к Новость 3 (index 2)
    news_db[2].add_comment(Comment(users_db[7], "Отличная статья, очень познавательно."))
    news_db[2].add_comment(Comment(users_db[0], "Когда такие батареи появятся в продаже?"))
    news_db[2].add_comment(Comment(users_db[1], "Звучит как фантастика, но круто!"))

    # ✅ Лайки
    news_db[0].like(users_db[0])
    news_db[0].like(users_db[1])
    news_db[0].like(users_db[2])
    news_db[1].like(users_db[4])
    news_db[1].like(users_db[5])
    news_db[2].like(users_db[7])


async def send_or_update_news(chat_id, user_obj: User, news_index: int, news_item: News, context: ContextTypes.DEFAULT_TYPE, message_id: int = None):
    """Функция отправки или обновления сообщения с новостью"""
    liked = user_obj.username() in news_item.likes()
    like_text = "Убрать лайк" if liked else "Лайкнуть"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=like_text, callback_data=f"like_{news_index}")],
        [InlineKeyboardButton(text="оставить комментарий", callback_data=f"comment_{news_index}")],
        [InlineKeyboardButton(text="посмотреть комментарии", callback_data=f"view_{news_index}")]
    ])
    
    text = (f"📰 *{news_item.title()}*\n"
            f"📅 {news_item.date_publish()}\n"
            f"📝 {news_item.description()}\n\n"
            f"❤️ Лайков: {len(news_item.likes())} | 💬 Комментариев: {len(news_item.comments())}")
    
    if message_id:
        try:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception:
            pass
    else:
        msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard, parse_mode="Markdown")
        news_message_ids[news_index] = msg.message_id


# ==================== ОБРАБОТЧИКИ КОМАНД ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton(text="список новостей")]
    ], resize_keyboard=True)
    
    await update.message.reply_text(
        "Привет! Я бот новостей.\n"
        "Доступные команды:\n"
        "/news — список всех новостей\n"
        "/create — создать новую новость",
        reply_markup=keyboard
    )

async def cmd_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not news_db:
        await update.message.reply_text("Новостей пока нет.")
        return

    current_user = User(update.effective_user.first_name, str(update.effective_user.id))
    for index, n in enumerate(news_db):
        await send_or_update_news(update.message.chat_id, current_user, index, n, context)

async def cmd_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_state[user_id] = "create_title"
    await update.message.reply_text("📝 Введите заголовок для новой новости:")

async def cmd_comments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /comments <номер_новости>\nПример: /comments 1")
        return
    
    try:
        news_number = int(context.args[0])
        index = news_number - 1
        if index < 0 or index >= len(news_db):
            await update.message.reply_text(f"Новости №{news_number} не существует.")
            return
        
        n = news_db[index]
        text = f"Комментарии к новости \"{n.title()}\":\n\n"
        
        if n.comments():
            for i, c in enumerate(n.comments(), 1):
                text += f"{i}. {c.user().name()} (@{c.user().username()}):\n   {c.text()}\n\n"
        else:
            text += "Комментариев пока нет."
        
        await update.message.reply_text(text)
    except (ValueError, IndexError):
        await update.message.reply_text("Номер новости должен быть числом.")


# ==================== ОБРАБОТЧИК REPLY-КНОПКИ ====================

async def btn_news_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_news(update, context)


# ==================== ОБРАБОТЧИК INLINE-КНОПОК ====================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    current_user = User(query.from_user.first_name, str(user_id))
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    
    action, idx_str = query.data.split("_")
    index = int(idx_str)
    
    if index < 0 or index >= len(news_db):
        await query.edit_message_text("Новость не найдена.")
        return
        
    news_item = news_db[index]
    
    if action == "like":
        if current_user.username() in news_item.likes():
            news_item.likes().remove(current_user.username())
        else:
            news_item.like(current_user)
        
        await send_or_update_news(chat_id, current_user, index, news_item, context, message_id)
        
    elif action == "comment":
        user_state[user_id] = "comment"
        user_context[user_id] = index
        await query.message.reply_text("✍️ Напишите ваш комментарий к этой новости:")
        
    elif action == "view":
        text = f" Комментарии к новости \"{news_item.title()}\":\n\n"
        if news_item.comments():
            for i, c in enumerate(news_item.comments(), 1):
                text += f"{i}. {c.user().name()} (@{c.user().username()}):\n   {c.text()}\n\n"
        else:
            text += "Комментариев пока нет."
        await query.message.reply_text(text)


# ==================== ГЛОБАЛЬНЫЙ ОБРАБОТЧИК СООБЩЕНИЙ ====================

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id in user_state.keys() and user_state[user_id] == "comment":
        news_index = user_context.get(user_id, 0)
        if news_index < len(news_db):
            current_user = User(update.effective_user.first_name, str(user_id))
            
            new_comment = Comment(current_user, text)
            news_db[news_index].add_comment(new_comment)
            
            await update.message.reply_text("✅ Комментарий успешно добавлен!")
            
            msg_id = news_message_ids.get(news_index)
            if msg_id:
                await send_or_update_news(update.message.chat_id, current_user, news_index, news_db[news_index], context, msg_id)
        
        del user_state[user_id]
        if user_id in user_context:
            del user_context[user_id]
        return

    if user_id in user_state.keys() and user_state[user_id] == "create_title":
        user_state[user_id] = "create_text"
        user_context[user_id] = text
        await update.message.reply_text("✅ Заголовок принят. Теперь введите текст новости:")
        return

    if user_id in user_state.keys() and user_state[user_id] == "create_text":
        title = user_context.get(user_id, "Без названия")
        current_user = User(update.effective_user.first_name, str(user_id))
        
        date_str = datetime.now().strftime("%d.%m.%Y")
        new_news = News(title, date_str, text)
        news_db.append(new_news)
        new_index = len(news_db) - 1
        
        await update.message.reply_text(f"🎉 Новость \"{title}\" успешно создана!")
        
        del user_state[user_id]
        if user_id in user_context:
            del user_context[user_id]
            
        await send_or_update_news(update.message.chat_id, current_user, new_index, new_news, context)
        return
        
    await update.message.reply_text("Неизвестная команда или текст. Используйте /start для вызова меню.")


# ==================== ЗАПУСК БОТА ====================

def main():
    init_data()
    
    TOKEN = "8251614396:AAGOv3GlBz2hJp-Yl06_J2VKw1UR8EoQNOA"
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("news", cmd_news))
    application.add_handler(CommandHandler("create", cmd_create))
    application.add_handler(CommandHandler("comments", cmd_comments))
    
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^список новостей$"), btn_news_list))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()