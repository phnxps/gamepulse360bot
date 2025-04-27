import os
import feedparser
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler
import asyncio
from datetime import datetime, timedelta
import random

# Variables de entorno
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

# Feeds de noticias oficiales
RSS_FEEDS = [
    'https://blog.playstation.com/feed/',
    'https://news.xbox.com/en-us/feed/',
    'https://www.nintendo.com/news/rss',
    'https://www.ign.com/rss',
    'https://vandal.elespanol.com/xml/rss/6/0.1/vandal.xml',
]

# Curiosidades gamer
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

# Estado interno
sent_articles = set()
last_curiosity_sent = datetime.now() - timedelta(hours=6)
votes = {}

async def send_news(bot, title, link, is_trailer=False):
    keyboard = [
        [InlineKeyboardButton("📖 Leer noticia", url=link)],
        [
            InlineKeyboardButton("👍 0", callback_data=f"like_{link}"),
            InlineKeyboardButton("👎 0", callback_data=f"dislike_{link}")
        ]
    ]
    if is_trailer:
        keyboard.insert(1, [InlineKeyboardButton("🎬 Ver Tráiler Oficial", url=link)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"🎮 *{title}*\n\n#Gamepulse360 #NoticiasGamer"
    await bot.send_message(
        chat_id=CHANNEL_USERNAME,
        text=message,
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        reply_markup=reply_markup,
        disable_web_page_preview=False
    )

async def send_curiosity(bot):
    global last_curiosity_sent
    curiosity = random.choice(CURIOSIDADES)
    message = f"🕹️ *Curiosidad Gamer*\n{curiosity}\n\n#Gamepulse360 #DatoGamer"
    await bot.send_message(
        chat_id=CHANNEL_USERNAME,
        text=message,
        parse_mode=telegram.constants.ParseMode.MARKDOWN,
        disable_web_page_preview=False
    )
    last_curiosity_sent = datetime.now()

async def check_feeds(bot):
    global sent_articles, last_curiosity_sent
    new_article_sent = False
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            if entry.link not in sent_articles:
                is_trailer = any(k in entry.title.lower() for k in ["tráiler","trailer"])
                await send_news(bot, entry.title, entry.link, is_trailer)
                sent_articles.add(entry.link)
                new_article_sent = True
                print(f"Enviado: {entry.title}")
                await asyncio.sleep(10)
    if not new_article_sent:
        now = datetime.now()
        if now - last_curiosity_sent > timedelta(hours=6):
            await send_curiosity(bot)

async def vote_handler(update, context):
    query = update.callback_query
    await query.answer()
    vote_type, link = query.data.split("_",1)
    if link not in votes:
        votes[link] = {"like": 0, "dislike": 0}
    votes[link][vote_type] += 1
    print(f"Votos para {link}: {votes[link]}")

async def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        # Inicializa correctamente la aplicación
        await application.initialize()

        application.add_handler(CallbackQueryHandler(vote_handler))

        # Tarea periódica en paralelo
        async def job():
            while True:
                await check_feeds(application.bot)
                await asyncio.sleep(600)  # 10 minutos

        # Arranca el bot y la tarea paralela
        await asyncio.gather(
            application.run_polling(),
            job()
        )
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")

if __name__ == "__main__":
    asyncio.run(main())
