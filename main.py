from sent_articles import init_db, save_article, is_article_saved, get_all_articles
import os
import feedparser
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ApplicationBuilder
from datetime import datetime, timedelta, time
import random
import requests
from bs4 import BeautifulSoup
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

init_db()

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
    'https://nintenduo.com/category/noticias/feed/',
    'https://www.xataka.com/tag/nintendo/rss',
    'https://www.xataka.com/tag/playstation/rss',
    'https://www.laps4.com/feed/',
    'https://areajugones.sport.es/feed/',
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
    "Halo fue pensado originalmente como un juego de estrategia en tiempo real. ⚔️",
    "La saga Pokémon es la franquicia más rentable del mundo. 🧢",
    "Crash Bandicoot fue desarrollado para rivalizar contra Mario. 🏁",
    "El primer videojuego de la historia es considerado 'Tennis for Two' de 1958. 🎾",
    "El control de la Xbox original se apodaba 'The Duke' por su tamaño. 🎮",
    "Metroid fue uno de los primeros juegos en presentar una protagonista femenina. 🚀",
    "Sega dejó de fabricar consolas tras el fracaso de Dreamcast. 🌀",
    "La consola Wii de Nintendo se llamaba inicialmente 'Revolution'. 🔥",
    "PlayStation 5 agotó su stock en Amazon en menos de 12 segundos. ⚡",
    "Breath of the Wild fue lanzado junto a la Nintendo Switch y redefinió los mundos abiertos. 🌎",
    "GTA V recaudó más de 800 millones de dólares en su primer día. 💵",
    "The Last of Us Part II ganó más de 300 premios de Juego del Año. 🏆",
    "Red Dead Redemption 2 tardó 8 años en desarrollarse. 🐎",
    "Cyberpunk 2077 vendió 13 millones de copias en sus primeras tres semanas. 🤖",
    "Animal Crossing: New Horizons fue el fenómeno social de 2020. 🏝️",
    "Call of Duty: Modern Warfare 3 fue el juego más vendido de 2011. 🎯",
    "El primer tráiler de Elden Ring tardó 2 años en publicarse tras su anuncio. 🕯️",
]



proximos_lanzamientos = []
last_curiosity_sent = datetime.now() - timedelta(hours=6)

async def send_news(context, entry):
    # Filtrar noticias recientes (últimas 3 horas)
    if hasattr(entry, 'published_parsed'):
        published = datetime(*entry.published_parsed[:6])
        if datetime.now() - published > timedelta(hours=3):
            return
    # Permitimos todas las noticias, sin filtrar por fecha de publicación

    # Filtro: excluir noticias de cine o series que no estén relacionadas con videojuegos
    title_lower = entry.title.lower()
    summary_lower = (entry.summary if hasattr(entry, 'summary') else "").lower()

    if any(keyword in title_lower for keyword in ["película", "serie", "actor", "cine", "temporada", "episodio", "manga", "anime"]) and not any(
        related in title_lower for related in ["juego", "videojuego", "expansión", "dlc", "adaptación", "game"]
    ):
        return

    if any(keyword in summary_lower for keyword in ["película", "serie", "actor", "cine", "temporada", "episodio", "manga", "anime"]) and not any(
        related in summary_lower for related in ["juego", "videojuego", "expansión", "dlc", "adaptación", "game"]
    ):
        return

    # Filtro adicional para ignorar noticias relacionadas con Wordle
    if "wordle" in title_lower or "wordle" in summary_lower:
        return

    link = entry.link.lower()
    # Mejorada: detección precisa de Nintendo Switch 2 (requiere "nintendo" y "switch 2" en título o resumen)
    if (("nintendo" in title_lower or "nintendo" in summary_lower) and ("switch 2" in title_lower or "switch 2" in summary_lower)):
        platform_label = 'NINTENDO SWITCH 2'
        icon = '🍄'
        tag = '#NintendoSwitch2'
    elif 'playstation' in link:
        platform_label = 'PLAYSTATION'
        icon = '🎮'
        tag = '#PlayStation'
    elif 'switch' in link and ('switch' in title_lower or 'switch' in summary_lower):
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

    link_lower = entry.link.lower()

    special_tags = []
    emoji_special = ''

    # Clasificación especial avanzada
    if any(kw in title_lower for kw in ["direct", "evento especial", "showcase", "game awards", "presentation", "conference", "wholesome direct"]):
        special_tags.insert(0, "#EventoEspecial")
        emoji_special = '🎬'
        # Añadir evento especial a la lista de próximos lanzamientos con fecha si está disponible
        if 'published' in locals():
            fecha_evento = published.strftime('%d/%m/%Y')
            proximos_lanzamientos.append(f"- EVENTO: {entry.title} ({fecha_evento})")

    if any(kw in title_lower for kw in ["tráiler", "trailer", "gameplay", "avance"]):
        if not any(neg in title_lower for neg in ["no debería", "no tendrá", "sin tráiler", "sin trailer", "no tiene tráiler", "no hay tráiler", "no hay trailer"]):
            special_tags.append("#TrailerOficial")
            emoji_special = '🎥'

    if any(kw in title_lower for kw in ["códigos", "código", "code", "giftcode"]):
        if not any(kw in title_lower for kw in ["error", "problema", "fallo", "solucionar", "solución"]):
            special_tags.append("#CodigosGamer")
            emoji_special = '🔑'

    if any(kw in title_lower for kw in [
        "guía", "como encontrar", "cómo encontrar", "cómo derrotar", "como derrotar", 
        "localizar", "localización", "walkthrough", "cómo resolver", "todas las ubicaciones", 
        "como conseguir", "cómo conseguir", "dónde encontrar", "como desbloquear", "cómo desbloquear"
    ]):
        special_tags.append("#GuiaGamer")
        emoji_special = '📖'

    if any(kw in title_lower for kw in ["rebaja", "descuento", "precio reducido", "promoción", "baja de precio", "por solo", "al mejor precio", "de oferta", "está por menos de", "bundle", "mejores ofertas"]) \
        or "mejores ofertas" in title_lower:
        special_tags.append("#OfertaGamer")
        if not emoji_special:
            emoji_special = '💸'

    # Detección de retrasos de lanzamiento
    if any(kw in title_lower for kw in ["retrasa", "retraso", "se retrasa", "aplazado", "postergado"]):
        special_tags.append("#LanzamientoRetrasado")
        if not emoji_special:
            emoji_special = '⏳'

    # Detección de análisis de Laps4 como ReviewGamer
    if "laps4.com" in link_lower and "análisis" in title_lower:
        special_tags.append("#ReviewGamer")
        if not emoji_special:
            emoji_special = '📝'

    # Evento especial detection (redundant with advanced classification but kept for backward compatibility)
    if any(kw in title_lower for kw in ["state of play", "nintendo direct", "showcase", "summer game fest", "game awards", "evento especial", "presentation", "conference", "presentación"]):
        if "#EventoEspecial" not in special_tags:
            special_tags.insert(0, "#EventoEspecial")
            if not emoji_special:
                emoji_special = '🎬'
            # Añadir evento especial a la lista de próximos lanzamientos con fecha si está disponible
            if 'published' in locals():
                fecha_evento = published.strftime('%d/%m/%Y')
                proximos_lanzamientos.append(f"- EVENTO: {entry.title} ({fecha_evento})")

    # Nueva detección de ofertas o rebajas (already handled above, but here to adjust platform_label if generic)
    if "#OfertaGamer" in special_tags:
        # Si es oferta/rebaja, ajustar platform_label si es genérico
        if platform_label == 'NOTICIAS GAMER':
            # Intentar detectar plataforma en título o resumen para asignar plataforma correcta
            if (("nintendo" in title_lower or "nintendo" in summary_lower) and ("switch 2" in title_lower or "switch 2" in summary_lower)):
                platform_label = 'NINTENDO SWITCH 2'
                icon = '🍄'
                tag = '#NintendoSwitch2'
            elif any(kw in title_lower for kw in ["switch"]) or any(kw in summary_lower for kw in ["switch"]):
                platform_label = 'NINTENDO SWITCH'
                icon = '🍄'
                tag = '#NintendoSwitch'
            elif any(kw in title_lower for kw in ["playstation"]) or any(kw in summary_lower for kw in ["playstation"]):
                platform_label = 'PLAYSTATION'
                icon = '🎮'
                tag = '#PlayStation'
            elif any(kw in title_lower for kw in ["xbox"]) or any(kw in summary_lower for kw in ["xbox"]):
                platform_label = 'XBOX'
                icon = '🟢'
                tag = '#Xbox'

    # Free game detection
    if any(kw in title_lower for kw in ["gratis", "free", "regalo"]):
        special_tags.append("#JuegoGratis")
        if not emoji_special:
            emoji_special = '🎁'
    # Free game detection (extended)
    if any(kw in title_lower for kw in ["gratis", "free", "regalo", "hazte con", "obtener gratis", "puedes conseguir"]):
        special_tags.append("#JuegoGratis")
        if not emoji_special:
            emoji_special = '🎁'
    # Filtro para descartar artículos no relacionados con videojuegos
    if not any(word in summary_lower + title_lower for word in [
        "videojuego", "juego", "consola", "ps5", "xbox", "switch", "gaming", "nintendo", "playstation",
        "dlc", "expansión", "demo", "tráiler", "skins", "jugabilidad", "personaje", "mapa", "nivel", "gamer"
    ]):
        return

    # Proximo lanzamiento detection (mejorada para evitar falsos positivos)
    if any(kw in title_lower for kw in ["anuncia", "anunciado", "confirmado", "confirmada", "lanzamiento", "próximo", "proximo", "sale", "disponible", "estrena", "estreno", "estrenará", "fecha confirmada", "open beta", "demo", "early access", "llegará", "fecha prevista", "se lanzará"]) and "retrasa" not in title_lower and "retraso" not in title_lower:
        if not any(block in title_lower for block in ["mantenimiento", "servidores", "online", "downtime", "actualización", "patch notes"]):
            if not any(false_positive in title_lower for false_positive in ["mejor lanzamiento", "ya disponible", "ha enamorado", "lanzado", "el lanzamiento de", "ya está", "ya se encuentra", "notas de metacritic"]):
                special_tags.append("#ProximoLanzamiento")
                if not emoji_special:
                    emoji_special = '🎉'

    if "#ProximoLanzamiento" in special_tags:
        fecha_publicacion = published.strftime('%d/%m/%Y') if 'published' in locals() else "Próximamente"
        proximos_lanzamientos.append(f"- {entry.title} ({fecha_publicacion})")

    # Review detection
    if any(kw in title_lower for kw in ["análisis", "review", "reseña", "comparativa"]):
        if "reseñas extremadamente positivas" not in title_lower:
            if "#ReviewGamer" not in special_tags:
                special_tags.append("#ReviewGamer")
            if not emoji_special:
                emoji_special = '📝'

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

    if not photo_url:
        try:
            r = requests.get(entry.link, timeout=5)
            soup = BeautifulSoup(r.text, 'html.parser')
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                photo_url = og_image.get('content')
        except Exception as e:
            print(f"Error obteniendo imagen por scraping: {e}")

    # Ajustar caption para eliminar "NOTICIAS GAMER" si es oferta/rebaja o categoría específica
    if platform_label == 'NOTICIAS GAMER' and ("#OfertaGamer" in special_tags or any(tag in special_tags for tag in ["#EventoEspecial", "#TrailerOficial", "#JuegoGratis", "#ProximoLanzamiento", "#ReviewGamer", "#CodigosGamer", "#GuiaGamer"])):
        # En este caso, no usar "NOTICIAS GAMER" genérico
        platform_label = ''
        icon = ''
        tag = ''

    hashtags = " ".join(special_tags + ([tag] if tag else []))

    # Determinar si es una categoría especial y asignar el título especial correspondiente
    special_title = ""
    # Prioridad: Evento, Tráiler, Códigos, Guía, Oferta, Lanzamiento, Retrasado
    if "#EventoEspecial" in special_tags:
        special_title = "*🎬 EVENTO ESPECIAL*"
    elif "#TrailerOficial" in special_tags:
        special_title = "*🎥 NUEVO TRÁILER*"
    elif "#CodigosGamer" in special_tags:
        special_title = "*🔑 CÓDIGOS DISPONIBLES*"
    elif "#GuiaGamer" in special_tags:
        special_title = "*📖 GUÍA GAMER*"
    elif "#OfertaGamer" in special_tags:
        special_title = "*💸 OFERTA GAMER*"
    elif "#ProximoLanzamiento" in special_tags:
        special_title = "*🎉 PRÓXIMO LANZAMIENTO*"
    elif "#LanzamientoRetrasado" in special_tags:
        special_title = "*⏳ RETRASADO*"

    if special_title:
        caption = (
            f"{icon} {special_title}\n\n"
            f"{emoji_special} *{entry.title}*\n\n"
            f"{hashtags}"
        ).strip()
    elif platform_label:
        caption = (
            f"{icon} *{platform_label}*\n\n"
            f"*{entry.title}*\n\n"
            f"{hashtags}"
        ).strip()
    else:
        caption = (
            f"*{entry.title}*\n\n"
            f"{hashtags}"
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
                disable_web_page_preview=False,
                reply_markup=button
            )
        # Guardar el artículo solo si el mensaje se envió correctamente
        if hasattr(entry, 'published_parsed'):
            published = datetime(*entry.published_parsed[:6])
        else:
            published = datetime.now()
        save_article(entry.link, published)
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
        for entry in feed.entries:
            if is_article_saved(entry.link):
                continue
            await send_news(context, entry)
            new_article_sent = True

    # Revisión de eventos especiales detectados hoy
    today = datetime.now().date()
    articles_today = [link for link in get_all_articles() if datetime.now().date() == today]

    eventos_detectados = False
    for article in articles_today:
        if any(keyword in article.lower() for keyword in ["state of play", "nintendo direct", "showcase", "summer game fest", "game awards", "evento especial", "presentation", "conference", "presentación"]):
            eventos_detectados = True
            break

    if eventos_detectados:
        try:
            evento_texto = "🎬 *¡Hoy hay eventos especiales en el mundo gamer!*\n\nPrepárate para seguir todas las novedades. 👾🔥"
            await context.bot.send_message(
                chat_id=CHANNEL_USERNAME,
                text=evento_texto,
                parse_mode=telegram.constants.ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
        except Exception as e:
            print(f"Error al enviar mensaje de eventos especiales: {e}")

    if not new_article_sent:
        if datetime.now().weekday() == 6:  # Domingo
            await send_launch_summary(context)
        now = datetime.now()
        if now - last_curiosity_sent > timedelta(hours=6):
            await send_curiosity(context)
            last_curiosity_sent = now

async def send_launch_summary(context):
    if not proximos_lanzamientos:
        return
    resumen = "🚀 *Próximos lanzamientos detectados:*\n\n" + "\n".join(proximos_lanzamientos)
    try:
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=resumen,
            parse_mode=telegram.constants.ParseMode.MARKDOWN,
            disable_web_page_preview=False
        )
        proximos_lanzamientos.clear()
    except Exception as e:
        print(f"Error al enviar resumen de lanzamientos: {e}")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    job_queue = application.job_queue
    job_queue.run_repeating(check_feeds, interval=600, first=10)

    # Enviar resumen diario todos los días a las 22:00
    job_queue.run_daily(send_launch_summary, time=time(hour=22, minute=0))

    # Importar mensajes antiguos y reenviar los no publicados recientes
    application.job_queue.run_once(import_existing_links, when=0)

    print("Bot iniciado correctamente.")
    application.run_polling()





async def import_existing_links(context):
    print("🔎 Importando mensajes antiguos del canal...")
    bot = context.bot
    seen_urls = set()
    offset = None
    while True:
        updates = await bot.get_updates(limit=100)
        if not updates:
            break
        for update in updates:
            # Mantener la compatibilidad con el procesamiento anterior:
            # update.message y update.message.text
            if hasattr(update, "message") and hasattr(update.message, "text") and update.message.text:
                for word in update.message.text.split():
                    clean_url = word.strip().strip('()[]<>.,!?\'"')
                    if clean_url.startswith("http"):
                        seen_urls.add(clean_url)
                        save_article(clean_url)
    print(f"✅ Se han registrado {len(seen_urls)} URLs del canal como ya enviadas.")

    # Reenviar artículos recientes que no están en el canal
    print("🔁 Reenviando artículos recientes no publicados...")
    from sent_articles import get_all_articles
    articles_in_db = get_all_articles()
    print("🧠 Comparando con artículos en base de datos...")
    for url in articles_in_db:
        if url not in seen_urls:
            # Verificar si fue publicado hace menos de 3 horas
            try:
                for feed_url in RSS_FEEDS:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries:
                        if entry.link == url and hasattr(entry, 'published_parsed'):
                            published = datetime(*entry.published_parsed[:6])
                            if datetime.now() - published <= timedelta(hours=3):
                                await send_news(context, entry)
                            break
                else:
                    print(f"❌ No se reenviará: {url} (muy antiguo o no encontrado)")
            except Exception as e:
                print(f"Error al reenviar {url}: {e}")


if __name__ == "__main__":
    main()

