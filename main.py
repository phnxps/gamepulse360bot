import os
import feedparser
import random
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
)

# Variables de entorno
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

# Feeds y curiosidades
RSS_FEEDS = [
    'https://blog.playstation.com/feed/',
    'https://news.xbox.com/en-us/feed/',
    'https://www.nintendo.com/news/rss',
    'https://www.ign.com/rss',
    'https://vandal.elespanol.com/xml/rss/6/0.1/vandal.xml',
]
CURIOSIDADES = [
    "La PlayStation nació tras un fallo con Nintendo. 🎮",
    "El primer easter egg fue en Adventure (1979). 🚀",
    "Mario se iba a llamar 'Jumpman'. 🍄",
    # ... (más curiosidades) ...
]

sent_articles = set()
last_curiosity = datetime.now() - timedelta(hours=6)
votes = {}

async def send_news(context, title, link, is_trailer):
    keyboard = [
        [ InlineKeyboardButton("📖 Leer noticia", url=link) ],
        [
            InlineKeyboardButton(f"👍 {votes.get(link, {}).get('like',0)}", callback_data=f"like|{link}"),
            InlineKeyboardButton(f"👎 {votes.get(link, {}).get('dislike',0)}", callback_data=f"dislike|{link}")
        ]
    ]
    if is_trailer:
        keyboard.insert(1, [ InlineKeyboardButton("🎬 Ver Tráiler Oficial", url=link) ])

    await context.bot.send_message(
        chat_id=CHANNEL_USERNAME,
        text=f"🎮 *{title}*\n\n#Gamepulse360 #NoticiasGamer",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=False
    )

async def send_curiosity(context):
    global last_curiosity
    curiosity = random.choice(CURIOSIDADES)
    await context.bot.send_message(
        chat_id=CHANNEL_USERNAME,
        text=f"🕹️ *Curiosidad Gamer*\n{curiosity}\n\n#Gamepulse360 #DatoGamer",
        parse_mode="Markdown"
    )
    last_curiosity = datetime.now()

async def check_feeds(context):
    global sent_articles, last_curiosity
    new_sent = False

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            if entry.link not in sent_articles:
                is_trailer = any(k in entry.title.lower() for k in ["tráiler","trailer"])
                await send_news(context, entry.title, entry.link, is_trailer)
                sent_articles.add(entry.link)
                new_sent = True

    if not new_sent and datetime.now() - last_curiosity > timedelta(hours=6):
        await send_curiosity(context)

async def vote_handler(update, context):
    query = update.callback_query
    await query.answer()
    typ, link = query.data.split("|",1)
    if link not in votes:
        votes[link] = {"like":0,"dislike":0}
    votes[link][typ] += 1
    print(f"Votos {link}: {votes[link]}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CallbackQueryHandler(vote_handler))

    # se crea automáticamente job_queue cuando instalas el extra
    jq = app.job_queue
    jq.run_repeating(check_feeds, interval=600, first=10)

    print("Bot iniciando…")
    app.run_polling()

if __name__ == "__main__":
    main()
