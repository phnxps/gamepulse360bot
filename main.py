import os
import feedparser
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, JobQueue
from datetime import datetime, timedelta
import random

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

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
    "GTA V es el producto más rentable del entretenimiento. 💰",
    "La Nintendo 64 introdujo el primer joystick analógico. 🎮",
    "La Switch es la consola híbrida más vendida de la historia. 🔥",
    "La PlayStation 2 es la consola más vendida de todos los tiempos. 🥇",
    "En Japón, 'Kirby' es visto como un símbolo de felicidad. 🌟",
    "Zelda: Breath of the Wild reinventó los mundos abiertos. 🧭",
    "La primera consola portátil fue la Game Boy (1989). 📺",
]

sent_articles = set()
last_curiosity_sent = datetime.now() - timedelta(hours=6)
votes = {}

async def send_news(context, title, link, is_trailer=False):
    keyboard = [
        [InlineKeyboardButton("📖 Leer noticia", url=link)],
        [InlineKeyboardButton("👍 0", callback_data=f"like|{link}"),
         InlineKeyboardButton("👎 0", callback_data=f"dislike|{link}")]
    ]

    if is_trailer:
        keyboard.insert(1, [InlineKeyboardButton("🎬 Ver Tráiler Oficial", url=link)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    hashtags = "#Gamepulse360 #NoticiasGamer"
    message = f"🎮 *{title}*\n\n{hashtags}"

    try:
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=message,
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
            reply_markup=reply_markup,
            disable_web_page_preview=False
        )
    except Exception as e:
        print(f"Error al enviar noticia: {e}")

async def send_curiosity(context):
    curiosity = random.choice(CURIOSIDADES)
    hashtags = "#Gamepulse360 #DatoGamer"
    message = f"🕹️ *Curiosidad Gamer*\n{curiosity}\n\n{hashtags}"
    try:
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=message,
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
            disable_web_page_preview=False
        )
    except Exception as e:
        print(f"Error al enviar curiosidad: {e}")

async def check_feeds(context):
    global last_curiosity_sent
    new_article_sent = False

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            if entry.link not in sent_articles:
                title = entry.title
                link = entry.link
                is_trailer = any(word in title.lower() for word in ["tráiler", "trailer", "gameplay trailer"])
                await send_news(context, title, link, is_trailer)
                sent_articles.add(entry.link)
                new_article_sent = True
    if not new_article_sent:
        now = datetime.now()
        if now - last_curiosity_sent > timedelta(hours=6):
            await send_curiosity(context)
            last_curiosity_sent = now

async def vote_handler(update, context):
    query = update.callback_query
    await query.answer()
    vote_type, link = query.data.split("|")
    if link not in votes:
        votes[link] = {"like": 0, "dislike": 0}

    votes[link][vote_type] += 1
    print(f"Votos para {link}: {votes[link]}")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CallbackQueryHandler(vote_handler))

    job_queue = application.job_queue
    job_queue.run_repeating(check_feeds, interval=600, first=10)  # cada 10 minutos

    print("Bot iniciado correctamente.")
    application.run_polling()

if __name__ == "__main__":
    main()
