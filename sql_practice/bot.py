import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from database import (
    init_db, find_user_by_tg_id, create_user, get_all_news, create_news, find_news_by_id,
    create_comment, get_comments_by_news_id, toggle_like, get_like_count, has_user_liked
)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
init_db()

user_state = {}
user_context = {}
news_message_ids = {}

def seed_db():
    if not get_all_news():
        n1 = create_news("Новость 1", "Выход патча 7.37 в Dota 2.", "16.09.2026")
        n2 = create_news("Новость 2", "Обновление в CS2.", "20.10.2026")
        n3 = create_news("Новость 3", "Технологический прорыв.", "26.01.2026")
        
        from database import SessionLocal, User, Comment, Likes
        with SessionLocal() as session:
            user = User(tg_id=999999, first_name="Маткин И.А.", last_name="")
            session.add(user)
            session.commit()
            session.add_all([
                Comment(user_id=user.id, news_id=n1.id, text="Ждал!"),
                Comment(user_id=user.id, news_id=n2.id, text="Круто!"),
                Comment(user_id=user.id, news_id=n3.id, text="Отлично!"),
                Likes(user_id=user.id, news_id=n1.id),
                Likes(user_id=user.id, news_id=n2.id)
            ])
            session.commit()

def get_or_create_user(tg_id: int, first_name: str, last_name: str = ""):
    """Вспомогательная функция - убирает дублирование кода"""
    user = find_user_by_tg_id(tg_id)
    if not user:
        user = create_user(tg_id=tg_id, first_name=first_name, last_name=last_name)
    return user

async def send_news(chat_id, user, news, context, message_id=None):
    liked = has_user_liked(user.id, news.id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Убрать лайк" if liked else "Лайкнуть", callback_data=f"like_{news.id}")],
        [InlineKeyboardButton("оставить комментарий", callback_data=f"comment_{news.id}")],
        [InlineKeyboardButton("посмотреть комментарии", callback_data=f"view_{news.id}")]
    ])
    text = f"📰 *{news.title}*\n📅 {news.release_date}\n📝 {news.description}\n\n❤️ {get_like_count(news.id)} | 💬 {len(get_comments_by_news_id(news.id))}"
    
    if message_id:
        try:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard, parse_mode="Markdown")
        except: pass
    else:
        msg = await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard, parse_mode="Markdown")
        news_message_ids[news.id] = msg.message_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_or_create_user(update.effective_user.id, update.effective_user.first_name, update.effective_user.last_name or "")
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("список новостей")]], resize_keyboard=True)
    await update.message.reply_text(f"Привет, {user.first_name}!\n/news - новости\n/create - создать новость", reply_markup=keyboard)

async def cmd_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_or_create_user(update.effective_user.id, update.effective_user.first_name)
    for news in get_all_news():
        await send_news(update.message.chat_id, user, news, context)

async def cmd_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_state[update.effective_user.id] = "create_title"
    await update.message.reply_text("📝 Введите заголовок:")

async def cmd_comments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /comments <номер>")
        return
    try:
        news = get_all_news()[int(context.args[0]) - 1]
        comments = get_comments_by_news_id(news.id)
        text = f"Комментарии к \"{news.title}\":\n\n"
        if comments:
            for i, c in enumerate(comments, 1):
                text += f"{i}. {c.user.first_name}:\n   {c.text}\n\n"
        else:
            text += "Нет комментариев."
        await update.message.reply_text(text)
    except:
        await update.message.reply_text("Ошибка. Пример: /comments 1")

async def btn_news_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_news(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = get_or_create_user(query.from_user.id, query.from_user.first_name)
    action, news_id = query.data.split("_")
    news = find_news_by_id(int(news_id))
    
    if not news:
        return
    
    if action == "like":
        toggle_like(user.id, news.id)
        await send_news(query.message.chat_id, user, news, context, query.message.message_id)
    elif action == "comment":
        user_state[query.from_user.id] = "comment"
        user_context[query.from_user.id] = news.id
        await query.message.reply_text("✍️ Напишите комментарий:")
    elif action == "view":
        comments = get_comments_by_news_id(news.id)
        text = f"💬 Комментарии к \"{news.title}\":\n\n"
        text += "\n".join(f"{i}. {c.user.first_name}:\n   {c.text}" for i, c in enumerate(comments, 1)) if comments else "Нет комментариев."
        await query.message.reply_text(text)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    user = get_or_create_user(user_id, update.effective_user.first_name)
    
    if user_state.get(user_id) == "comment":
        create_comment(user.id, user_context[user_id], text)
        await update.message.reply_text("✅ Комментарий добавлен!")
        news = find_news_by_id(user_context[user_id])
        msg_id = news_message_ids.get(user_context[user_id])
        if msg_id:
            await send_news(update.message.chat_id, user, news, context, msg_id)
        del user_state[user_id]
        del user_context[user_id]
        
    elif user_state.get(user_id) == "create_title":
        user_state[user_id] = "create_text"
        user_context[user_id] = text
        await update.message.reply_text("✅ Теперь введите текст новости:")
        
    elif user_state.get(user_id) == "create_text":
        create_news(user_context[user_id], text, datetime.now().strftime("%d.%m.%Y"))
        await update.message.reply_text(f"🎉 Новость \"{user_context[user_id]}\" создана!")
        del user_state[user_id]
        del user_context[user_id]

def main():
    seed_db()
    app = Application.builder().token("8251614396:AAGOv3GlBz2hJp-Yl06_J2VKw1UR8EoQNOA").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", cmd_news))
    app.add_handler(CommandHandler("create", cmd_create))
    app.add_handler(CommandHandler("comments", cmd_comments))
    app.add_handler(MessageHandler(filters.Regex("^список новостей$"), btn_news_list))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()