import pytest
from unittest.mock import MagicMock
from popcorn_archives import core


def test_parse_with_parentheses():
    """Tests the 'Title (YYYY)' format."""
    title, year = core.parse_movie_title("The Matrix (1999)")
    assert title == "The Matrix"
    assert year == 1999

def test_parse_with_trailing_metadata():
    """Tests formats with extra text at the end."""
    title, year = core.parse_movie_title("Naked (1993) [BluRay] [1080p]")
    assert title == "Naked"
    assert year == 1993

def test_parse_simple_format():
    """Tests the 'Title YYYY' format."""
    title, year = core.parse_movie_title("The Kid 1921")
    assert title == "The Kid"
    assert year == 1921

def test_invalid_format_returns_none():
    """Ensures invalid formats return None, None."""
    result = core.parse_movie_title("Invalid Movie Name Without Year")
    assert result == (None, None)

def test_year_outside_range_is_invalid():
    """Ensures years outside the valid range are ignored."""
    result = core.parse_movie_title("A Fake Movie 1700")
    assert result == (None, None)


def test_scan_movie_folders(tmp_path):
    """Tests scanning a directory using a temporary file system."""
    movies_dir = tmp_path / "movies"
    movies_dir.mkdir()
    (movies_dir / "Good Movie (2020)").mkdir()
    (movies_dir / "Another Good Movie 2021").mkdir()
    (movies_dir / "Bad Movie Folder").mkdir()
    (movies_dir / "some_file.txt").touch()
    valid, invalid = core.scan_movie_folders(movies_dir)

    assert len(valid) == 2
    assert len(invalid) == 1
    assert set(valid) == {("Good Movie", 2020), ("Another Good Movie", 2021)}
    assert invalid == ["Bad Movie Folder"]


def test_read_csv_file(tmp_path):
    """Tests reading a CSV file from a temporary file system."""
    csv_file = tmp_path / "test.csv"
    csv_content = "name\nMovie One (2022)\nInvalid Movie\nMovie Two 2023"
    csv_file.write_text(csv_content)

    result = core.read_csv_file(csv_file)

    assert len(result) == 2
    assert set(result) == {("Movie One", 2022), ("Movie Two", 2023)}


def test_fetch_movie_details_success(mocker):
    """Tests a successful API call with a complete mock data payload."""
    
    # --- FINAL FIX: Use the correct path to the mocked object ---
    # The 'config_manager' name exists inside the 'core' module.
    mocker.patch('popcorn_archives.core.config_manager.get_api_key', return_value='a_fake_api_key')
    # -----------------------------------------------------------

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None

    search_json = {
        'results': [
            {'id': 680, 'popularity': 99, 'release_date': '1994-10-14'}
        ]
    }
    details_json = {
        'title': 'Pulp Fiction',
        'release_date': '1994-10-14',
        'genres': [{'name': 'Crime'}, {'name': 'Drama'}],
        'overview': 'A classic plot.',
        'vote_average': 8.4,
        'imdb_id': 'tt0110912',
        'runtime': 154,
        'belongs_to_collection': {'name': 'Pulp Fiction Collection'},
        'credits': {
            'crew': [{'job': 'Director', 'name': 'Tarantino'}],
            'cast': [{'name': 'John Travolta'}]
        },
        'keywords': {'keywords': [{'name': 'hitman'}]},
        'tagline': 'Just because you are a character doesn\'t mean you have character.',
        'production_companies': [{'name': 'Miramax'}],
        'budget': 8000000,
        'revenue': 213928762,
        'original_language': 'en',
        'poster_path': '/d5iIlFn5sCMn4VYAStA6siNz30G1r.jpg',
    }
    
    mock_response.json.side_effect = [search_json, details_json]
    mocker.patch('requests.get', return_value=mock_response)
    
    # Execution
    details = core.fetch_movie_details_from_api("Pulp Fiction", 1994)

    # Assertion
    assert "Error" not in details
    assert details['title'] == 'Pulp Fiction'
    assert details['year'] == 1994
    assert details['director'] == 'Tarantino'
    assert details['tmdb_score'] == "84%"