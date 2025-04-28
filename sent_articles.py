import sqlite3

DB_FILE = 'sent_articles.db'

def init_db():
    """Inicializar la base de datos si no existe."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_article(url):
    """Guardar un nuevo artículo."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO articles (url) VALUES (?)', (url,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Ya existe
    conn.close()

def is_article_saved(url):
    """Comprobar si el artículo ya fue guardado."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM articles WHERE url = ?', (url,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def delete_old_articles(days=30):
    """Eliminar artículos guardados hace más de X días."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM articles WHERE created_at <= datetime("now", ?)', (f'-{days} days',))
    conn.commit()
    conn.close()

def get_all_articles():
    """Obtener todos los artículos guardados (solo URL)."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT url FROM articles')
    articles = [row[0] for row in cursor.fetchall()]
    conn.close()
    return articles
