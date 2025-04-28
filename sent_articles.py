import sqlite3
import os

DB_PATH = 'sent_articles.db'

# Crear la base de datos si no existe
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                url TEXT PRIMARY KEY
            )
        ''')
        conn.commit()
        conn.close()

# Añadir un enlace a la base de datos
def save_article(url):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO articles (url) VALUES (?)', (url,))
        conn.commit()
    except sqlite3.IntegrityError:
        # Ya existe, no pasa nada
        pass
    conn.close()

# Verificar si ya existe un enlace
def is_article_saved(url):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM articles WHERE url = ?', (url,))
    result = cursor.fetchone()
    conn.close()
    return result is not None
