import sqlite3
import os
import click 

# مسیر استاندارد برای ذخیره داده‌های اپلیکیشن را پیدا می‌کنیم
# این مسیر در لینوکس معمولا ~/.local/share/popcorn_archives است
APP_NAME = "PopcornArchives"
APP_DIR = click.get_app_dir(APP_NAME)
DB_FILE = os.path.join(APP_DIR, 'movies.db')


def get_db_connection():
    """یک اتصال جدید به دیتابیس برقرار می‌کند."""
    # اگر پوشه برنامه وجود ندارد، آن را می‌سازیم
    os.makedirs(APP_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """جدول فیلم‌ها را در صورت عدم وجود ایجاد می‌کند."""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                year INTEGER NOT NULL,
                UNIQUE(title, year)
            )
        ''')
        conn.commit()

# ... بقیه توابع (add_movie, search_movie و غیره) بدون هیچ تغییری باقی می‌مانند ...

def add_movie(title, year):
    """یک فیلم جدید به دیتابیس اضافه می‌کند."""
    sql = "INSERT INTO movies (title, year) VALUES (?, ?)"
    try:
        with get_db_connection() as conn:
            conn.execute(sql, (title, year))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        return False

def search_movie(query):
    """فیلم‌ها را بر اساس عنوان جستجو می‌کند."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT title, year FROM movies WHERE title LIKE ?", ('%' + query + '%',))
        return cursor.fetchall()

def get_random_movie():
    """یک فیلم به صورت تصادفی برمی‌گرداند."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT title, year FROM movies ORDER BY RANDOM() LIMIT 1")
        return cursor.fetchone()

def get_movies_by_year(year):
    """تمام فیلم‌های یک سال مشخص را برمی‌گرداند."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT title, year FROM movies WHERE year = ? ORDER BY title", (year,))
        return cursor.fetchall()

def get_movies_by_decade(decade):
    """تمام فیلم‌های یک دهه مشخص را برمی‌گرداند."""
    start_year = decade
    end_year = decade + 9
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT title, year FROM movies WHERE year BETWEEN ? AND ? ORDER BY year, title", (start_year, end_year))
        return cursor.fetchall()