import os
import feedparser
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder
from datetime import datetime, timedelta
import random

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

RSS_FEEDS = [
    'https://vandal.elespanol.com/rss/',
    'https://www.3djuegos.com/rss/',
    'https://www.hobbyconsolas.com/categoria/novedades/rss',
    'https://www.vidaextra.com/feed',
    'https://www.nintenderos.com/feed',
    'https://as.com/meristation/portada/rss.xml',
    'https://blog.es.playstation.com/feed/',
    'https://www.nintendo.com/es/news/rss.xml',
    'https://news.xbox.com/es-mx/feed/',
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

async def send_news(context, entry):
    link = entry.link.lower()
    if 'playstation' in link:
        platform_label = 'PLAYSTATION'
        icon = '🎮'
        tag = '#PlayStation'
    elif 'switch 2' in link or 'switch-2' in link:
        platform_label = 'NINTENDO SWITCH 2'
        icon = '🍄'
        tag = '#NintendoSwitch2'
    elif 'switch' in link:
        platform_label = 'NINTENDO SWITCH'
        icon = '🍄'
        tag = '#NintendoSwitch'
    elif 'xbox' in link:
        platform_label = 'XBOX'
        icon = '🟢'
        tag = '#Xbox'
    else:
        platform_label = 'NOTICIAS GAMER'
        icon = '🎮'
        tag = '#NoticiasGamer'

    title_lower = entry.title.lower()
    if any(kw in title_lower for kw in ["anunci", "lanzamiento", "próximo", "proximo", "sale", "disponible", "estrena", "estreno", "estrenará"]):
        special_tag = "#ProximoLanzamiento"
    else:
        special_tag = ""

    photo_url = None
    if entry.get("media_content"):
        for m in entry.media_content:
            if m.get("type", "").startswith("image/"):
                photo_url = m.get("url")
                break
    if not photo_url and entry.get("enclosures"):
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image/"):
                photo_url = enc.get("url")
                break

    caption = (
        f"{icon} *{platform_label}*\n\n"
        f"*{entry.title}*\n\n"
        f"{special_tag} {tag}"
    ).strip()

    button = InlineKeyboardMarkup([[InlineKeyboardButton("📰 Leer noticia completa", url=entry.link)]])

    try:
        if photo_url:
            await context.bot.send_photo(
                chat_id=CHANNEL_USERNAME,
                photo=photo_url,
                caption=caption,
                parse_mode=telegram.constants.ParseMode.MARKDOWN,
                reply_markup=button
            )
        else:
            await context.bot.send_message(
                chat_id=CHANNEL_USERNAME,
                text=caption,
                parse_mode=telegram.constants.ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=button
            )
    except Exception as e:
        print(f"Error al enviar noticia: {e}")

async def send_curiosity(context):
    curiosity = random.choice(CURIOSIDADES)
    message = f"🕹️ *Curiosidad Gamer*\n{curiosity}\n\n#Gamepulse360 #DatoGamer"
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
                await send_news(context, entry)
                sent_articles.add(entry.link)
                new_article_sent = True

    if not new_article_sent:
        now = datetime.now()
        if now - last_curiosity_sent > timedelta(hours=6):
            await send_curiosity(context)
            last_curiosity_sent = now

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    job_queue = application.job_queue
    job_queue.run_repeating(check_feeds, interval=600, first=10)

    print("Bot iniciado correctamente.")
    application.run_polling()

if __name__ == "__main__":
    main()
