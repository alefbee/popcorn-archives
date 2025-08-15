import sqlite3
import os
import click

APP_NAME = "PopcornArchives"
APP_DIR = click.get_app_dir(APP_NAME)
DB_FILE = os.path.join(APP_DIR, 'movies.db')

def get_db_connection():
    """Establishes a new connection to the database."""
    os.makedirs(APP_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes and migrates the database schema. This function is safe to run
    multiple times and handles both new and old database versions.
    """
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                year INTEGER NOT NULL,
                UNIQUE(title, year)
            )
        ''')


        cursor = conn.execute("PRAGMA table_info(movies)")
        existing_columns = {row['name'] for row in cursor.fetchall()}

        expected_columns = {
            "watched": "INTEGER NOT NULL DEFAULT 0",
            "genre": "TEXT",
            "director": "TEXT",
            "plot": "TEXT",
            "imdb_rating": "TEXT"
        }

        for col_name, col_type in expected_columns.items():
            if col_name not in existing_columns:
                click.echo(f"Database migration: Adding column '{col_name}'...")
                conn.execute(f'ALTER TABLE movies ADD COLUMN {col_name} {col_type}')
        
        conn.commit()

def add_movie(title, year):
    """Adds a new movie to the database."""
    sql = "INSERT INTO movies (title, year) VALUES (?, ?)"
    try:
        with get_db_connection() as conn:
            conn.execute(sql, (title, year))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.OperationalError as e:
        click.echo(f"Database error: {e}", err=True)
        return False

def search_movie(query):
    """Searches for movies by their title."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT title, year FROM movies WHERE title LIKE ?", ('%' + query + '%',))
        return cursor.fetchall()

def get_random_movie():
    """Returns a single random movie from the database."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT title, year FROM movies ORDER BY RANDOM() LIMIT 1")
        return cursor.fetchone()

def get_movies_by_year(year):
    """Returns all movies from a specific year."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT title, year FROM movies WHERE year = ? ORDER BY title", (year,))
        return cursor.fetchall()

def get_movies_by_decade(decade):
    """Returns all movies from a specific decade."""
    start_year = decade
    end_year = decade + 9
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT title, year FROM movies WHERE year BETWEEN ? AND ? ORDER BY year, title", (start_year, end_year))
        return cursor.fetchall()    

def delete_movie(title, year):
    """Deletes a specific movie by its title and year."""
    sql = "DELETE FROM movies WHERE title = ? AND year = ?"
    with get_db_connection() as conn:
        cursor = conn.execute(sql, (title, year))
        conn.commit()
        return cursor.rowcount > 0

def clear_all_movies():
    """Deletes all movies from the database."""
    sql = "DELETE FROM movies"
    with get_db_connection() as conn:
        conn.execute(sql)
        conn.commit()

def get_total_movies_count():
    """Returns the total number of movies in the database."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT COUNT(id) FROM movies")
        return cursor.fetchone()[0]

def get_oldest_movie():
    """Returns the oldest movie(s) in the database."""
    with get_db_connection() as conn:
        min_year_cursor = conn.execute("SELECT MIN(year) FROM movies")
        min_year = min_year_cursor.fetchone()[0]
        if min_year is None:
            return []
        cursor = conn.execute("SELECT title, year FROM movies WHERE year = ?", (min_year,))
        return cursor.fetchall()

def get_newest_movie():
    """Returns the newest movie(s) in the database."""
    with get_db_connection() as conn:
        max_year_cursor = conn.execute("SELECT MAX(year) FROM movies")
        max_year = max_year_cursor.fetchone()[0]
        if max_year is None:
            return []
        cursor = conn.execute("SELECT title, year FROM movies WHERE year = ?", (max_year,))
        return cursor.fetchall()

def get_most_frequent_decade():
    """Finds the decade with the most movies."""
    with get_db_connection() as conn:
        sql = """
            SELECT (year / 10) * 10 AS decade, COUNT(id) as movie_count
            FROM movies
            GROUP BY decade
            ORDER BY movie_count DESC
            LIMIT 1
        """
        cursor = conn.execute(sql)
        result = cursor.fetchone()
        return result
    
def get_all_movies():
    """Returns a list of all movies from the database, sorted by year."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT title, year FROM movies ORDER BY year, title")
        return cursor.fetchall()

def get_decade_distribution(limit=5):
    """
    Finds the top N decades with the most movies.
    Returns a list of tuples, e.g., [(1950, 25), (1970, 22), ...].
    """
    with get_db_connection() as conn:
        sql = """
            SELECT (year / 10) * 10 AS decade, COUNT(id) as movie_count
            FROM movies
            GROUP BY decade
            ORDER BY movie_count DESC, decade DESC
            LIMIT ?
        """
        cursor = conn.execute(sql, (limit,))
        return cursor.fetchall()

def set_movie_watched_status(title, year, watched_status: bool):
    """Sets the watched status for a specific movie."""
    status_int = 1 if watched_status else 0
    sql = "UPDATE movies SET watched = ? WHERE title = ? AND year = ?"
    with get_db_connection() as conn:
        cursor = conn.execute(sql, (status_int, title, year))
        conn.commit()
        return cursor.rowcount > 0

def get_watched_stats():
    """Returns the count of watched and unwatched movies."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT SUM(watched), COUNT(id) - SUM(watched) FROM movies")
        return cursor.fetchone()

def get_random_unwatched_movie():
    """Returns a single random unwatched movie."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT title, year FROM movies WHERE watched = 0 ORDER BY RANDOM() LIMIT 1")
        return cursor.fetchone()
    
def get_movie_details(title, year):
    """Retrieves all details for a specific movie from the database."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM movies WHERE title = ? AND year = ?",
            (title, year)
        )
        return cursor.fetchone()

def update_movie_details(title, year, details):
    """Updates a movie record with details fetched from an API."""
    sql = """
        UPDATE movies SET
        genre = ?, director = ?, plot = ?, imdb_rating = ?
        WHERE title = ? AND year = ?
    """
    with get_db_connection() as conn:
        conn.execute(sql, (
            details.get('Genre'),
            details.get('Director'),
            details.get('Plot'),
            details.get('imdbRating'),
            title,
            year
        ))
        conn.commit()

def get_movies_by_genre(genre_query):
    """Finds all movies that match a specific genre."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT title, year, genre FROM movies WHERE genre LIKE ?",
            (f'%{genre_query}%',)
        )
        return cursor.fetchall()

def get_movies_missing_details():
    """Returns all movies that haven't had their details fetched yet (genre is NULL)."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT title, year FROM movies WHERE genre IS NULL")
        return cursor.fetchall()
    
def get_all_unique_genres():
    """
    Returns a sorted list of all unique genres present in the database.
    Handles genres stored as comma-separated strings.
    """
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT DISTINCT genre FROM movies WHERE genre IS NOT NULL")
        
        all_genres = set()
        for row in cursor.fetchall():
            # Split genres like "Action, Adventure, Sci-Fi" into individual items
            genres = [g.strip() for g in row['genre'].split(',')]
            all_genres.update(genres)
            
        return sorted(list(all_genres))