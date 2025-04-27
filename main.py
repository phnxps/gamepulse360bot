import os
import feedparser
import telegram
import asyncio
from datetime import datetime, timedelta
import random

# Variables de entorno
BOT_TOKEN = os.getenv("7722735338:AAHQVQxwvW7VlKjSBM74t9rvrcMbnu8iQRA")
CHANNEL_USERNAME = os.getenv("@Gamepulse360")

# Bot de Telegram
bot = telegram.Bot(token=BOT_TOKEN)

# Feeds de noticias oficiales
RSS_FEEDS = [
    'https://blog.playstation.com/feed/',
    'https://news.xbox.com/en-us/feed/',
    # Puedes añadir más feeds aquí si quieres en el futuro
]

# Curiosidades gamer
CURIOSIDADES = [
    "La PlayStation original nació tras un fallido acuerdo entre Sony y Nintendo. 🕹️",
    "El primer easter egg de los videojuegos fue en Adventure de Atari (1979). 🚀",
    "Mario iba a llamarse 'Jumpman' antes de ser 'Mario'. 🎮",
    "GTA V es el producto de entretenimiento más rentable de la historia. 💵",
    "La Nintendo 64 introdujo el primer joystick analógico en una consola. 🎮",
]

# Guardamos las últimas noticias enviadas para no repetir
sent_articles = set()
last_curiosity_sent = datetime.now() - timedelta(hours=6)

async def main():
    while True:
        for feed_url in RSS_FEEDS:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                if entry.link not in sent_articles:
                    title = entry.title
                    link = entry.link
                    message = f"🎮 *{title}*\n\n➡️ [Leer Noticia Completa]({link})\n\n#Gamepulse360 #NoticiasGamer"
                    try:
                        await bot.send_message(chat_id=CHANNEL_USERNAME, text=message, parse_mode=telegram.constants.ParseMode.MARKDOWN, disable_web_page_preview=False)
                        sent_articles.add(entry.link)
                        print(f"Enviado: {title}")
                        await asyncio.sleep(10)
                    except Exception as e:
                        print(f"Error enviando noticia: {e}")

# Si no hay noticias nuevas, mandar curiosidad cada 6 horas
now = datetime.now()
if now - last_curiosity_sent > timedelta(hours=6):
    curiosity = random.choice(CURIOSIDADES)
    global last_curiosity_sent  # <-- Pon esto aquí, justo antes de modificar la variable
    try:
        await bot.send_message(chat_id=CHANNEL_USERNAME, text=f"🕹️ *Curiosidad Gamer*\n{curiosity}\n\n#Gamepulse360 #DatoGamer", parse_mode=telegram.constants.ParseMode.MARKDOWN)
        print("Curiosidad enviada.")
    except Exception as e:
        print(f"Error enviando curiosidad: {e}")
    last_curiosity_sent = now

        await asyncio.sleep(600)  # Esperar 10 minutos antes de volver a revisar

if __name__ == "__main__":
    asyncio.run(main())
