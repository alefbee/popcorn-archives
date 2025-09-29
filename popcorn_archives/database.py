import sqlite3
import os
import click
from collections import Counter
from . import logger as app_logger
from thefuzz import fuzz

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

        if 'imdb_rating' in existing_columns and 'tmdb_score' not in existing_columns:
            click.echo("Database migration: Renaming column 'imdb_rating' to 'tmdb_score'...")
            conn.execute('ALTER TABLE movies RENAME COLUMN imdb_rating TO tmdb_score')
            cursor = conn.execute("PRAGMA table_info(movies)")
            existing_columns = {row['name'] for row in cursor.fetchall()}

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
            "user_rating": "INTEGER",
            "tagline": "TEXT",
            "writers": "TEXT",
            "dop": "TEXT",
            "original_language": "TEXT",
            "poster_path": "TEXT",
            "budget": "INTEGER",
            "revenue": "INTEGER",
            "production_companies": "TEXT"
        }

        for col_name, col_type in expected_columns.items():
            if col_name not in existing_columns:
                click.echo(f"Database migration: Adding column '{col_name}'...")
                conn.execute(f'ALTER TABLE movies ADD COLUMN {col_name} {col_type}')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE
            )
        ''')
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
    """
    Updates the details of a movie in the database.
    
    Args:
        title (str): Original title of the movie
        year (int): Original year of the movie
        details (dict): New details to update
    """
    if "Error" in details:
        return False
        
    try:
        with get_db_connection() as conn:
            # First, verify the movie exists
            cursor = conn.execute(
                "SELECT title, year FROM movies WHERE title = ? AND year = ?",
                (title, year)
            )
            if not cursor.fetchone():
                app_logger.log_error(f"Cannot update non-existent movie: {title} ({year})")
                return False

            sql = """
                UPDATE movies SET
                    runtime = ?,
                    genre = ?,
                    director = ?,
                    plot = ?,
                    tmdb_score = ?,
                    imdb_id = ?,
                    cast = ?,
                    keywords = ?,
                    collection = ?,
                    tagline = ?,
                    writers = ?,
                    dop = ?,
                    original_language = ?,
                    poster_path = ?,
                    budget = ?,
                    revenue = ?,
                    production_companies = ?
                WHERE title = ? AND year = ?
            """
            
            conn.execute(sql, (
                details.get('runtime', None),
                details.get('genre', None),
                details.get('director', None),
                details.get('plot', None),
                details.get('tmdb_score', None),
                details.get('imdb_id', None),
                details.get('cast', None),
                details.get('keywords', None),
                details.get('collection', None),
                details.get('tagline', None),
                details.get('writers', None),
                details.get('dop', None),
                details.get('original_language', None),
                details.get('poster_path', None),
                details.get('budget', 0),
                details.get('revenue', 0),
                details.get('production_companies', None),
                title,  # WHERE clause
                year    # WHERE clause
            ))
            
            return True
            
    except Exception as e:
        app_logger.log_error(f"Database error updating {title} ({year}): {str(e)}")
        return False

def get_movies_missing_details():
    """
    Returns all movies that have NULL values (haven't been processed by API yet).
    Ignores fields that have 'N/A' as they've already been checked with the API.
    """
    with get_db_connection() as conn:
        sql = """
            SELECT title, year FROM movies WHERE
                runtime IS NULL OR
                genre IS NULL OR
                director IS NULL OR
                plot IS NULL OR
                tagline IS NULL OR
                writers IS NULL OR
                dop IS NULL OR
                poster_path IS NULL OR
                budget IS NULL OR
                revenue IS NULL OR
                production_companies IS NULL
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
    
def search_movies_advanced(title=None, director=None, actor=None, keyword=None, collection=None, year=None, decade=None, writer=None, dop=None, company=None, genre=None):
    """
    Performs an advanced search with multiple dynamic criteria.
    """
    with get_db_connection() as conn:
        base_query = 'SELECT title, year, director, "cast", collection, keywords, writers, dop, production_companies, genre FROM movies'
        conditions = []
        params = []

        # Dynamically build the WHERE clauses based on provided filters
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
        if writer:
            conditions.append("writers LIKE ? COLLATE NOCASE")
            params.append(f'%{writer}%')
        if dop:
            conditions.append("dop LIKE ? COLLATE NOCASE")
            params.append(f'%{dop}%')
        if company:
            conditions.append("production_companies LIKE ? COLLATE NOCASE")
            params.append(f'%{company}%')
        if genre:
            conditions.append("genre LIKE ? COLLATE NOCASE")
            params.append(f'%{genre}%')

        if not conditions:
            return []

        query = f"{base_query} WHERE {' AND '.join(conditions)} ORDER BY year, title"
        return conn.execute(query, tuple(params)).fetchall()
    
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

def cleanup_database(threshold=85):
    """
    Finds and interactively merges both exact (case-insensitive) and
    fuzzily similar title duplicates.
    """
    import inquirer
    
    with get_db_connection() as conn:
        # Step 1: Handle EXACT case-insensitive duplicates automatically
        sql_exact = "SELECT LOWER(title) as l_title, year FROM movies GROUP BY l_title, year HAVING COUNT(id) > 1"
        exact_duplicates = conn.execute(sql_exact).fetchall()
        
        merged_count = 0
        for group in exact_duplicates:
            records = conn.execute("SELECT id, title FROM movies WHERE LOWER(title) = ? AND year = ? ORDER BY id ASC", (group['l_title'], group['year'])).fetchall()
            record_to_keep = records[0]
            ids_to_delete = [rec['id'] for rec in records[1:]]
            if ids_to_delete:
                placeholders = ','.join('?' for _ in ids_to_delete)
                conn.execute(f"DELETE FROM movies WHERE id IN ({placeholders})", tuple(ids_to_delete))
                conn.execute("UPDATE movies SET title = ? WHERE id = ?", (record_to_keep['title'].title(), record_to_keep['id']))
                merged_count += len(ids_to_delete)
        
        if merged_count > 0:
            click.echo(click.style(f"Automatically merged {merged_count} exact duplicate entries.", fg='blue'))

        # Step 2: Find and interactively merge FUZZILY similar titles
        all_movies = conn.execute("SELECT id, title, year FROM movies").fetchall()
        potential_duplicates = {}
        # This is a bit slow (O(n^2)), but robust for typical library sizes.
        for i in range(len(all_movies)):
            for j in range(i + 1, len(all_movies)):
                m1, m2 = all_movies[i], all_movies[j]
                if m1['year'] == m2['year'] and fuzz.ratio(m1['title'].lower(), m2['title'].lower()) > threshold:
                    # Grouping by a sorted tuple of IDs to uniquely identify a pair
                    key = tuple(sorted((m1['id'], m2['id'])))
                    if key not in potential_duplicates:
                        potential_duplicates[key] = [m1, m2]
        
        if not potential_duplicates:
            if merged_count == 0: # Only say this if nothing at all was found
                click.echo("No duplicates or similar titles found.")
            return merged_count

        deleted_count = 0
        click.echo(click.style(f"\nFound {len(potential_duplicates)} groups of movies with similar titles:", bold=True))

        for key, movies in potential_duplicates.items():
            choices = [f"{m['title']} ({m['year']})" for m in movies]
            questions = [ inquirer.List('keep', message=f"Ambiguous titles found. Which version do you want to keep?", choices=choices) ]
            answers = inquirer.prompt(questions)

            if answers:
                chosen_str = answers['keep']
                record_to_keep = next((m for m in movies if f"{m['title']} ({m['year']})" == chosen_str), None)
                records_to_delete = [m for m in movies if m['id'] != record_to_keep['id']]
                
                if records_to_delete:
                    ids_to_delete = [m['id'] for m in records_to_delete]
                    placeholders = ','.join('?' for _ in ids_to_delete)
                    conn.execute(f"DELETE FROM movies WHERE id IN ({placeholders})", tuple(ids_to_delete))
                    deleted_count += len(ids_to_delete)
        
        total_merged = merged_count + deleted_count
        if total_merged > 0:
            conn.commit()
        return total_merged

def find_movie_by_normalized_title(normalized_title, year):
    """
    Finds a movie in the database by comparing its normalized title and year.
    This is used to match titles that might have platform-specific differences
    (e.g., with or without a colon ':').
    """
    from . import core # Lazy import to use the normalizer
    
    with get_db_connection() as conn:
        # We cannot use a simple SQL query here because normalization happens in Python.
        # We must fetch all potential candidates and check them one by one.
        # This is less efficient, but necessary for this kind of fuzzy matching.
        cursor = conn.execute("SELECT * FROM movies WHERE year = ?", (year,))
        
        for movie_row in cursor.fetchall():
            db_title_normalized = core.normalize_title(movie_row['title'])
            if db_title_normalized == normalized_title:
                return movie_row # Return the full row object if a match is found
    
    return None # No match found

#Functions for Watchlist Management
def get_watchlist():
    """Returns all titles from the watchlist, sorted alphabetically."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT title FROM watchlist ORDER BY title ASC")
        # Return a simple list of strings
        return [row['title'] for row in cursor.fetchall()]

def add_to_watchlist(title):
    """
    Adds a new movie title to the watchlist.
    Returns True if successful, False if it already exists.
    """
    sql = "INSERT INTO watchlist (title) VALUES (?)"
    try:
        with get_db_connection() as conn:
            # Standardize to Title Case before saving for consistency
            conn.execute(sql, (title.strip().title(),))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        # This happens if the title already exists due to the UNIQUE constraint
        return False

def remove_from_watchlist(title):
    """
    Removes a movie title from the watchlist (case-insensitive).
    Returns True if a movie was deleted, False otherwise.
    """
    sql = "DELETE FROM watchlist WHERE LOWER(title) = LOWER(?)"
    with get_db_connection() as conn:
        cursor = conn.execute(sql, (title.strip(),))
        conn.commit()
        return cursor.rowcount > 0