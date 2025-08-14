# tests/test_database.py

import pytest
import sqlite3
from popcorn_archives import database

@pytest.fixture
def db_connection():
    """
    A fixture that sets up an in-memory SQLite database for testing.
    It creates the necessary table and yields a connection object.
    """
    # Use an in-memory database for complete isolation.
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row # Important for accessing columns by name
    
    # Create the full table schema needed for the tests.
    conn.execute('''
        CREATE TABLE movies (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            watched INTEGER NOT NULL DEFAULT 0,
            genre TEXT,
            director TEXT,
            plot TEXT,
            imdb_rating TEXT,
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