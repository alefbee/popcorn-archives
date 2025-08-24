import sqlite3
import os
import click
from collections import Counter
from . import logger as app_logger

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
        # Create the base table if it doesn't exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                year INTEGER NOT NULL,
                UNIQUE(title, year)
            )
        ''')

        # --- Migration Logic ---
        cursor = conn.execute("PRAGMA table_info(movies)")
        existing_columns = {row['name'] for row in cursor.fetchall()}

        # Rename imdb_rating to tmdb_score for legacy users
        if 'imdb_rating' in existing_columns and 'tmdb_score' not in existing_columns:
            click.echo("Database migration: Renaming column 'imdb_rating' to 'tmdb_score'...")
            conn.execute('ALTER TABLE movies RENAME COLUMN imdb_rating TO tmdb_score')
            # We need to refetch columns after altering the table
            cursor = conn.execute("PRAGMA table_info(movies)")
            existing_columns = {row['name'] for row in cursor.fetchall()}

        # Define all columns that should exist in the latest version
        expected_columns = {
            "watched": "INTEGER NOT NULL DEFAULT 0",
            "genre": "TEXT",
            "director": "TEXT",
            "plot": "TEXT",
            "tmdb_score": "TEXT",
            "imdb_id": "TEXT",
            "runtime": "INTEGER",
            "cast": "TEXT",
            "keywords": "TEXT",
            "collection": "TEXT",
            "user_rating": "INTEGER"
        }

        # Add any missing columns
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
            conn.execute(sql, (title.title(), year))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.OperationalError as e:
        click.echo(f"Database error: {e}", err=True)
        return False
    app_logger.log_info(f"Added movie: {title} ({year})")

def search_movie(query, exact=False):
    """
    Searches for movies by title, case-insensitively.
    If exact is True, it looks for an exact title match.
    """
    with get_db_connection() as conn:
        if exact:
            # This is not used in the new logic but good to keep
            sql = "SELECT title, year FROM movies WHERE LOWER(title) = LOWER(?)"
            params = (query,)
        else:
            # Use LIKE for partial matches
            sql = "SELECT title, year FROM movies WHERE title LIKE ? COLLATE NOCASE"
            params = (f'%{query}%',)
            
        cursor = conn.execute(sql, params)
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
    app_logger.log_info(f"Deleted movie: {title} ({year})")

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
    """Retrieves all details for a specific movie, case-insensitively."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM movies WHERE LOWER(title) = LOWER(?) AND year = ?",
            (title, year)
        )
        return cursor.fetchone()

def update_movie_details(title, year, details):
    """Updates a movie record with details fetched from an API."""
    sql = """
        UPDATE movies SET
            genre = ?, director = ?, plot = ?, tmdb_score = ?, imdb_id = ?,
            runtime = ?, "cast" = ?, keywords = ?, collection = ?
        WHERE title = ? AND year = ?
    """
    with get_db_connection() as conn:
        conn.execute(sql, (
            details.get('genre'),
            details.get('director'),
            details.get('plot'),
            details.get('tmdb_score'),
            details.get('imdb_id'),
            details.get('runtime'),
            details.get('cast'),
            details.get('keywords'),
            details.get('collection'),
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
    """
    Returns all movies that are missing one or more key details.
    This also handles cases where a default 'N/A' value was stored.
    """
    with get_db_connection() as conn:
        # A movie is considered incomplete if ANY of these key fields are NULL
        # OR if they contain our default placeholder 'N/A'.
        sql = """
            SELECT title, year FROM movies WHERE
            runtime IS NULL OR
            genre IS NULL OR genre = 'N/A' OR
            director IS NULL OR director = 'N/A' OR
            plot IS NULL OR plot = 'N/A'
        """
        cursor = conn.execute(sql)
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
    
def search_movies_advanced(title=None, director=None, actor=None, keyword=None, collection=None, year=None, decade=None):
    """
    Performs an advanced search with multiple optional criteria.
    All text-based searches are case-insensitive and partial.
    """
    with get_db_connection() as conn:
        base_query = 'SELECT title, year, director, "cast", collection, keywords FROM movies'
        conditions = []
        params = []

        if title:
            conditions.append("title LIKE ? COLLATE NOCASE")
            params.append(f'%{title}%')
        if director:
            conditions.append("director LIKE ? COLLATE NOCASE")
            params.append(f'%{director}%')
        if actor:
            conditions.append('"cast" LIKE ? COLLATE NOCASE')
            params.append(f'%{actor}%')
        if keyword:
            conditions.append("keywords LIKE ? COLLATE NOCASE")
            params.append(f'%{keyword}%')
        if collection:
            conditions.append("collection LIKE ? COLLATE NOCASE")
            params.append(f'%{collection}%')
        if year:
            conditions.append("year = ?")
            params.append(year)
        if decade:
            conditions.append("year BETWEEN ? AND ?")
            params.extend([decade, decade + 9])
        if not conditions:
            # If no filters are provided, it's better to return an empty list.
            return []

        # Join the conditions with ' AND '
        query = f"{base_query} WHERE {' AND '.join(conditions)} ORDER BY year, title"

        cursor = conn.execute(query, tuple(params))
        return cursor.fetchall()
    
def get_movies_by_name_list(name_list):
    """
    Takes a list of 'Title (YYYY)' strings and returns the corresponding
    movie records from the database.
    """
    with get_db_connection() as conn:
        # This is a bit complex: we need to parse the names and create a
        # dynamic query.
        movies_to_find = []
        from .core import parse_movie_title # Avoid circular import
        for name in name_list:
            title, year = parse_movie_title(name)
            if title and year:
                movies_to_find.append((title, year))

        if not movies_to_find:
            return []
        
        # Create placeholders for the query: e.g., "(?, ?) OR (?, ?)"
        placeholders = " OR ".join(["(LOWER(title) = LOWER(?) AND year = ?)"] * len(movies_to_find))
        # Flatten the list of tuples for the parameters
        params = [item for t in movies_to_find for item in t]
        
        sql = f"SELECT title, year FROM movies WHERE {placeholders}"
        cursor = conn.execute(sql, tuple(params))
        return cursor.fetchall()
    
def get_top_items_from_column(column_name, limit=5):
    """
    A generic function to get the most common items from a comma-separated column.
    Used for genres, directors, cast, and keywords.
    """
    with get_db_connection() as conn:
        # We need to fetch all non-empty rows for the given column.
        sql = f'SELECT "{column_name}" FROM movies WHERE "{column_name}" IS NOT NULL'
        cursor = conn.execute(sql)
        
        # Counter is a powerful tool for counting items in a list.
        item_counter = Counter()
        
        for row in cursor.fetchall():
            # Split the comma-separated string into individual items.
            items = [item.strip() for item in row[column_name].split(',')]
            # Update the counter with the items from this row.
            item_counter.update(items)
            
        # Return the N most common items and their counts.
        return item_counter.most_common(limit)

def get_extreme_runtime_movies():
    """Finds the movies with the minimum and maximum runtime."""
    with get_db_connection() as conn:
        # We can do this in a single query for efficiency.
        sql = """
            SELECT title, year, runtime FROM movies
            WHERE runtime = (SELECT MIN(runtime) FROM movies WHERE runtime > 0) OR
                  runtime = (SELECT MAX(runtime) FROM movies)
            ORDER BY runtime ASC
        """
        cursor = conn.execute(sql)
        results = cursor.fetchall()
        
        if len(results) == 0:
            return None, None
        elif len(results) == 1: # Happens if the shortest and longest are the same movie
            return results[0], results[0]
        else:
            return results[0], results[-1] # Shortest is first, longest is last

def get_top_decade():
    """Finds the single decade with the most movies."""
    with get_db_connection() as conn:
        sql = """
            SELECT (year / 10) * 10 AS decade, COUNT(id) as movie_count
            FROM movies
            GROUP BY decade
            ORDER BY movie_count DESC
            LIMIT 1
        """
        cursor = conn.execute(sql)
        return cursor.fetchone()

def set_user_rating(title, year, rating):
    """Sets a user's personal rating (1-10) for a specific movie."""
    if not 1 <= rating <= 10:
        return False, "Rating must be between 1 and 10."

    sql = "UPDATE movies SET user_rating = ? WHERE LOWER(title) = LOWER(?) AND year = ?"
    with get_db_connection() as conn:
        cursor = conn.execute(sql, (rating, title, year))
        conn.commit()
        if cursor.rowcount > 0:
            return True, "Rating updated."
        else:
            return False, "Movie not found in archive."

def get_highest_rated_movie():
    """Finds the user's highest-rated movie(s)."""
    with get_db_connection() as conn:
        # Find the max rating value first
        max_rating_cursor = conn.execute("SELECT MAX(user_rating) FROM movies")
        max_rating = max_rating_cursor.fetchone()[0]

        if not max_rating or max_rating == 0:
            return None, None # No ratings given yet

        # Find all movies with that rating
        cursor = conn.execute(
            "SELECT title, year FROM movies WHERE user_rating = ?",
            (max_rating,)
        )
        # We only return the first one if there are multiple
        return cursor.fetchone(), max_rating

def cleanup_duplicates():
    """
    Finds and merges duplicate movies (same title, same year, different case).
    Returns the number of duplicates that were merged.
    """
    with get_db_connection() as conn:
        # Find groups of potential duplicates (case-insensitive)
        sql_find = "SELECT LOWER(title) as l_title, year FROM movies GROUP BY l_title, year HAVING COUNT(id) > 1"
        cursor = conn.execute(sql_find)
        duplicate_groups = cursor.fetchall()

        total_merged = 0
        for group in duplicate_groups:
            # For each group, get all the individual records, ordered by ID
            sql_get_records = "SELECT id, title FROM movies WHERE LOWER(title) = ? AND year = ? ORDER BY id ASC"
            records = conn.execute(sql_get_records, (group['l_title'], group['year'])).fetchall()

            if not records: continue

            # The first record is the one we want to keep. The rest will be deleted.
            record_to_keep = records[0]
            ids_to_delete = [rec['id'] for rec in records[1:]]
            
            if ids_to_delete:
                # 1. Delete the redundant records
                placeholders = ','.join('?' for _ in ids_to_delete)
                conn.execute(f"DELETE FROM movies WHERE id IN ({placeholders})", tuple(ids_to_delete))
                total_merged += len(ids_to_delete)

            # 2. Now that duplicates are gone, safely update the remaining record to the standard case
            conn.execute("UPDATE movies SET title = ? WHERE id = ?", (record_to_keep['title'].title(), record_to_keep['id']))
        
        conn.commit()
        return total_merged
