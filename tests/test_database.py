import pytest
import sqlite3
from popcorn_archives import database

@pytest.fixture
def db_connection(monkeypatch):
    """
    A fixture that sets up a complete in-memory database for testing.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    
    conn.execute('''
        CREATE TABLE movies (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            watched INTEGER NOT NULL DEFAULT 0,
            genre TEXT,
            director TEXT,
            plot TEXT,
            tmdb_score TEXT,
            imdb_id TEXT,
            runtime INTEGER,
            "cast" TEXT,
            keywords TEXT,
            collection TEXT,
            user_rating INTEGER, 
            UNIQUE(title, year)
        )
    ''')
    
    # Add one piece of sample data for tests to use.
    conn.execute("INSERT INTO movies (title, year) VALUES (?, ?)", ("Test Movie", 2020))
    conn.commit()

    # --- Monkeypatch the database connection function ---
    # This is the key: we tell our app's code to use THIS connection
    # for the duration of the test, instead of creating its own.
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(database, 'get_db_connection', lambda: conn)

    yield conn  # Provide the connection to the test function

    conn.close() # Clean up after the test is done.

def test_add_movie(db_connection):
    """Tests adding a new movie and a duplicate movie."""
    # The fixture already added one movie.
    assert database.add_movie("New Movie", 2021) is True
    
    # Verify it was added
    cursor = db_connection.execute("SELECT * FROM movies WHERE title = ?", ("New Movie",))
    assert cursor.fetchone() is not None

    # Test adding a duplicate
    assert database.add_movie("Test Movie", 2020) is False

def test_watched_status(db_connection):
    """Tests setting and checking the watched status of a movie."""
    # Fetch the initial state of our sample movie.
    details = database.get_movie_details("Test Movie", 2020)
    assert details['watched'] == 0  # Should be unwatched by default.

    # Mark the movie as watched.
    assert database.set_movie_watched_status("Test Movie", 2020, watched_status=True) is True
    
    # Verify the change.
    details_updated = database.get_movie_details("Test Movie", 2020)
    assert details_updated['watched'] == 1

def test_user_rating(db_connection):
    """
    Tests setting a valid rating, an invalid rating, and for a non-existent movie.
    """
    # Test setting a valid rating
    success, msg = database.set_user_rating("Test Movie", 2020, 8)
    assert success is True
    
    # Verify the rating was saved correctly
    details = database.get_movie_details("Test Movie", 2020)
    assert details['user_rating'] == 8

    # Test setting an invalid rating (e.g., 11)
    success, msg = database.set_user_rating("Test Movie", 2020, 11)
    assert success is False
    assert "must be between 1 and 10" in msg

    # Test setting a rating for a movie that doesn't exist
    success, msg = database.set_user_rating("Ghost Movie", 2025, 5)
    assert success is False
    assert "Movie not found" in msg

def test_get_highest_rated_movie(db_connection):
    """Tests finding the highest-rated movie."""
    # Add some more movies with ratings
    database.add_movie("Good Movie", 2021)
    database.add_movie("Great Movie", 2022)
    database.set_user_rating("Test Movie", 2020, 7)
    database.set_user_rating("Good Movie", 2021, 9)
    database.set_user_rating("Great Movie", 2022, 9) # Two movies with the same top rating

    movie, rating = database.get_highest_rated_movie()
    
    assert rating == 9
    # The result could be either of the two movies with a 9/10 rating
    assert movie['title'] in ["Good Movie", "Great Movie"]