import pytest
from unittest.mock import MagicMock
from popcorn_archives import core
from thefuzz import fuzz


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
    
    # Mock the config manager
    mocker.patch('popcorn_archives.core.config_manager.get_api_key', return_value='a_fake_api_key')
    
    # Mock the fuzz.ratio function to return high similarity for our test cases
    mocker.patch('popcorn_archives.core.fuzz.ratio', side_effect=lambda x, y: 
        95 if ('pulp' in x.lower() and 'fic' in x.lower()) else 60
    )
    
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    
    # Update search results to include more fields needed for sorting
    search_json = {
        'results': [
            {
                'id': 680,
                'title': 'Pulp Fiction',
                'popularity': 99,
                'release_date': '1994-10-14',
                'overview': 'A classic plot.'
            }
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
            'crew': [
                {'job': 'Director', 'name': 'Tarantino'},
                {'department': 'Writing', 'name': 'Quentin Tarantino'},
                {'job': 'Director of Photography', 'name': 'Andrzej Sekula'}
            ],
            'cast': [{'name': 'John Travolta'}, {'name': 'Samuel L. Jackson'}]
        },
        'keywords': {'keywords': [{'name': 'hitman'}, {'name': 'crime'}]},
        'tagline': 'Just because you are a character doesn\'t mean you have character.',
        'production_companies': [{'name': 'Miramax'}, {'name': 'A Band Apart'}],
        'budget': 8000000,
        'revenue': 213928762,
        'original_language': 'en',
        'poster_path': '/d5iIlFn5sCMn4VYAStA6siNz30G1r.jpg'
    }
    
    # Setup the mock to return same response for both API calls
    mock_response.json.side_effect = [search_json, details_json] * 2  # Times 2 for both test cases
    mocker.patch('requests.get', return_value=mock_response)
    
    # Test 1: Exact title match
    details = core.fetch_movie_details_from_api("Pulp Fiction", 1994)
    
    # Assert no errors
    assert "Error" not in details
    
    # Assert original title is preserved
    assert details['title'] == "Pulp Fiction"
    
    # Assert other fields are correctly parsed
    assert details['year'] == 1994
    assert details['director'] == "Tarantino"
    assert details['genre'] == "Crime, Drama"
    assert details['tmdb_score'] == "84%"
    assert details['writers'] == "Quentin Tarantino"
    assert details['dop'] == "Andrzej Sekula"
    assert details['cast'] == "John Travolta, Samuel L. Jackson"
    assert details['keywords'] == "hitman, crime"
    assert details['collection'] == "Pulp Fiction Collection"
    assert details['production_companies'] == "Miramax, A Band Apart"
    
    # Test 2: Fuzzy matching with slightly different title
    details = core.fetch_movie_details_from_api("Pulp Ficton", 1994)  # Intentional typo
    assert "Error" not in details
    assert details['title'] == "Pulp Ficton"  # Original title should be preserved
    assert details['year'] == 1994  # Other details should still be correct
    assert details['director'] == "Tarantino"