import sqlite3
import os

# مسیر فایل دیتابیس را مشخص می‌کنیم
DB_FOLDER = 'data'
DB_FILE = os.path.join(DB_FOLDER, 'movies.db')

def init_db():
    """جدول فیلم‌ها را در صورت عدم وجود ایجاد می‌کند."""
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            UNIQUE(title, year)
        )
    ''')
    conn.commit()
    conn.close()

def add_movie(title, year):
    """یک فیلم جدید به دیتابیس اضافه می‌کند."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO movies (title, year) VALUES (?, ?)", (title, year))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # در صورتی که فیلم از قبل وجود داشته باشد
        return False

def search_movie(query):
    """فیلم‌ها را بر اساس عنوان جستجو می‌کند."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT title, year FROM movies WHERE title LIKE ?", ('%' + query + '%',))
    results = cursor.fetchall()
    conn.close()
    return results

def get_random_movie():
    """یک فیلم به صورت تصادفی برمی‌گرداند."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT title, year FROM movies ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result

def get_movies_by_year(year):
    """تمام فیلم‌های یک سال مشخص را برمی‌گرداند."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT title, year FROM movies WHERE year = ? ORDER BY title", (year,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_movies_by_decade(decade):
    """تمام فیلم‌های یک دهه مشخص را برمی‌گرداند."""
    start_year = decade
    end_year = decade + 9
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT title, year FROM movies WHERE year BETWEEN ? AND ? ORDER BY year, title", (start_year, end_year))
    results = cursor.fetchall()
    conn.close()
    return results