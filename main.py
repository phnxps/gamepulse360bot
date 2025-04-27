import os
import feedparser
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, JobQueue
from datetime import datetime, timedelta
import random

# Map short numeric IDs to article URLs
news_map = {}
next_id = 0

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

RSS_FEEDS = [
    'https://vandal.elespanol.com/rss/',
    'https://www.3djuegos.com/rss/',
    'https://www.hobbyconsolas.com/categoria/novedades/rss',
    'https://www.vidaextra.com/feed',
    'https://www.nintenderos.com/feed',
    'https://as.com/meristation/portada/rss.xml',
    'https://blog.es.playstation.com/',
    'https://www.nintendo.com/es-es/Noticias/Noticias-y-novedades-11145.html?srsltid=AfmBOoq7KUJIK6DdMAFbXGy8xQLj5qbGrlvhLHxfxYkM-2AgoKvKLvvW',
    'https://news.xbox.com/es-latam/',
    

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

async def send_news(context, entry):
    global next_id
    # assign a short ID for this article
    news_id = str(next_id)
    next_id += 1
    news_map[news_id] = entry.link

    # determine if it's a trailer
    is_trailer = any(kw in entry.title.lower() for kw in ["tráiler", "trailer", "gameplay trailer"])
    # try to extract an image
    photo_url = None
    if entry.get("media_content"):
        photo_url = entry.media_content[0].get("url")
    elif entry.get("enclosures"):
        photo_url = entry.enclosures[0].get("url")

    # build buttons using the short news_id
    buttons = [
        [InlineKeyboardButton("📖 Leer noticia", url=entry.link)],
        [
          InlineKeyboardButton(f"👍 {votes.get(news_id,{}).get('like',0)}", callback_data=f"like|{news_id}"),
          InlineKeyboardButton(f"👎 {votes.get(news_id,{}).get('dislike',0)}", callback_data=f"dislike|{news_id}")
        ]
    ]
    if is_trailer:
        buttons.insert(1, [InlineKeyboardButton("🎬 Ver Tráiler Oficial", url=entry.link)])

    reply_markup = InlineKeyboardMarkup(buttons)
    caption = f"🎮 *{entry.title}*\n\n{entry.summary[:200]}...\n\n#Gamepulse360 #NoticiasGamer"

    try:
        if photo_url:
            await context.bot.send_photo(
                chat_id=CHANNEL_USERNAME,
                photo=photo_url,
                caption=caption,
                parse_mode=telegram.constants.ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_message(
                chat_id=CHANNEL_USERNAME,
                text=caption,
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
                await send_news(context, entry)
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
    vote_type, news_id = query.data.split("|", 1)
    if news_id not in votes:
        votes[news_id] = {"like": 0, "dislike": 0}
    votes[news_id][vote_type] += 1
    print(f"Votos para {news_map.get(news_id)}: {votes[news_id]}")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CallbackQueryHandler(vote_handler))

    job_queue = application.job_queue
    job_queue.run_repeating(check_feeds, interval=600, first=10)  # cada 10 minutos

    print("Bot iniciado correctamente.")
    application.run_polling()

if __name__ == "__main__":
    main()
