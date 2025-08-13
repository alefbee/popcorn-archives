import sqlite3
import os
import click

# Find the standard directory for application data.
# On Linux, this is typically ~/.local/share/PopcornArchives
APP_NAME = "PopcornArchives"
APP_DIR = click.get_app_dir(APP_NAME)
DB_FILE = os.path.join(APP_DIR, 'movies.db')

def get_db_connection():
    """Establishes a new connection to the database."""
    # Ensure the application directory exists before connecting.
    os.makedirs(APP_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE, timeout=10)
    # Allows accessing columns by name.
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates the movies table if it doesn't exist."""
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

def add_movie(title, year):
    """Adds a new movie to the database."""
    sql = "INSERT INTO movies (title, year) VALUES (?, ?)"
    try:
        with get_db_connection() as conn:
            conn.execute(sql, (title, year))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        # This error occurs if the movie (title, year) already exists.
        return False
    except sqlite3.OperationalError as e:
        # Handle other potential DB errors, like "database is locked".
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
        # Returns True if a row was deleted, False otherwise.
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
        # fetchone() will return a tuple like (143,)
        return cursor.fetchone()[0]

def get_oldest_movie():
    """Returns the oldest movie(s) in the database."""
    with get_db_connection() as conn:
        # Find the minimum year first
        min_year_cursor = conn.execute("SELECT MIN(year) FROM movies")
        min_year = min_year_cursor.fetchone()[0]
        if min_year is None:
            return []
        # Find all movies from that year
        cursor = conn.execute("SELECT title, year FROM movies WHERE year = ?", (min_year,))
        return cursor.fetchall()

def get_newest_movie():
    """Returns the newest movie(s) in the database."""
    with get_db_connection() as conn:
        # Find the maximum year first
        max_year_cursor = conn.execute("SELECT MAX(year) FROM movies")
        max_year = max_year_cursor.fetchone()[0]
        if max_year is None:
            return []
        # Find all movies from that year
        cursor = conn.execute("SELECT title, year FROM movies WHERE year = ?", (max_year,))
        return cursor.fetchall()

def get_most_frequent_decade():
    """Finds the decade with the most movies."""
    with get_db_connection() as conn:
        # This query calculates the decade for each year and counts them
        sql = """
            SELECT (year / 10) * 10 AS decade, COUNT(id) as movie_count
            FROM movies
            GROUP BY decade
            ORDER BY movie_count DESC
            LIMIT 1
        """
        cursor = conn.execute(sql)
        result = cursor.fetchone()
        # result will be like (1950, 25)
        return result
    
def get_all_movies():
    """Returns a list of all movies from the database, sorted by year."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT title, year FROM movies ORDER BY year, title")
        return cursor.fetchall()