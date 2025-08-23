from click.testing import CliRunner
from popcorn_archives.cli import cli, smart_info
from unittest.mock import MagicMock


def test_genre_command_direct_filter(mocker):
    """Tests the 'genre' command in direct (non-interactive) mode."""
    runner = CliRunner()
    
    mocker.patch('popcorn_archives.database.get_movies_by_genre', return_value=[
        {'title': 'Action Movie 1', 'year': 2020, 'genre': 'Action'},
    ])
    
    result = runner.invoke(cli, ['genre', 'Action'])
    
    assert result.exit_code == 0
    assert "Movies matching genre 'Action'" in result.output
    assert "Action Movie 1" in result.output

def test_genre_command_interactive_success(mocker):
    """Tests the interactive mode with a valid user choice."""
    runner = CliRunner()
    

    mocker.patch('popcorn_archives.database.get_all_unique_genres', return_value=['Action', 'Comedy', 'Drama'])
    
    mock_get_by_genre = mocker.patch('popcorn_archives.database.get_movies_by_genre', return_value=[
        {'title': 'Comedy Movie', 'year': 2022, 'genre': 'Comedy'}
    ])
    
    result = runner.invoke(cli, ['genre'], input='2\n')
    
    assert result.exit_code == 0
    assert "Please choose a genre" in result.output
    
    mock_get_by_genre.assert_called_once_with('Comedy')
    
    assert "Movies matching genre 'Comedy'" in result.output
    assert "Comedy Movie" in result.output

def test_genre_command_interactive_invalid_input(mocker):
    """Tests interactive mode with various invalid inputs."""
    runner = CliRunner()
    
    mocker.patch('popcorn_archives.database.get_all_unique_genres', return_value=['Action', 'Comedy', 'Drama'])

    result_bad_str = runner.invoke(cli, ['genre'], input='abc\n')
    assert result_bad_str.exit_code == 0
    assert "Invalid input. Please enter a number." in result_bad_str.output

    result_bad_num = runner.invoke(cli, ['genre'], input='99\n')
    assert result_bad_num.exit_code == 0
    assert "Invalid choice. Please enter a valid number." in result_bad_num.output

def test_genre_command_no_genres_available(mocker):
    """Tests interactive mode when the database has no genres."""
    runner = CliRunner()
    mocker.patch('popcorn_archives.database.get_all_unique_genres', return_value=[])
    
    result = runner.invoke(cli, ['genre'])
    
    assert result.exit_code == 0
    assert "No genres found in the database." in result.output

def test_smart_info_precise_query_found_locally(mocker):
    """Tests `info Title YYYY` when the movie exists in the local DB."""
    # Mock the database to return a full movie object
    mock_movie = {'title': 'The Matrix', 'year': 1999, 'plot': 'A plot.', 'director': 'The Wachowskis', 'genre': 'Sci-Fi', 'tmdb_score': '82%', 'runtime': 136, 'cast': 'Keanu Reeves', 'collection': 'The Matrix Collection', 'imdb_id': 'tt0133093'}
    mocker.patch('popcorn_archives.database.get_movie_details', return_value=mock_movie)
    
    runner = CliRunner()
    result = runner.invoke(cli, ['info', 'The Matrix 1999'])
    
    assert result.exit_code == 0
    assert "The Wachowskis" in result.output
    assert "Keanu Reeves" in result.output

def test_smart_info_partial_query_one_local_match(mocker):
    """Tests `info Title` when exactly one match is found locally."""
    # Mock the partial search
    mocker.patch('popcorn_archives.database.search_movie', return_value=[{'title': 'John Wick: Chapter 4', 'year': 2023}])
    # Mock the full details lookup for the found movie
    mock_movie = {'title': 'John Wick: Chapter 4', 'year': 2023, 'plot': 'John Wick uncovers a path...'}
    mocker.patch('popcorn_archives.database.get_movie_details', return_value=mock_movie)

    runner = CliRunner()
    result = runner.invoke(cli, ['info', 'John Wick'])

    assert result.exit_code == 0
    assert "Found one match: John Wick: Chapter 4 (2023)" in result.output
    assert "John Wick uncovers a path..." in result.output

def test_smart_info_partial_query_multiple_local_matches(mocker):
    """Tests `info Title` when multiple matches are found locally and the user chooses one."""
    mocker.patch('popcorn_archives.database.search_movie', return_value=[
        {'title': 'Terminator 2: Judgment Day', 'year': 1991},
        {'title': 'The Terminator', 'year': 1984}
    ])
    mock_movie = {'title': 'The Terminator', 'year': 1984, 'plot': 'A human soldier is sent...'}
    mocker.patch('inquirer.prompt', return_value={'choice': 'The Terminator (1984)'})
    
    runner = CliRunner()
    # No need for 'input' anymore, as we've mocked the prompt
    result = runner.invoke(cli, ['info', 'Terminator'])

    assert result.exit_code == 0
    assert "Found multiple matches" in result.output
    assert "A human soldier is sent..." in result.output


def test_smart_info_not_found_locally_fetch_and_add(mocker):
    """Tests `info Title YYYY` when not found locally, fetches online, and user confirms add."""
    # 1. Mock all external dependencies
    mocker.patch('popcorn_archives.database.get_movie_details', return_value=None)
    mocker.patch('popcorn_archives.database.search_movie', return_value=[])
    
    mock_api_response = { "genre": "Sci-Fi", "director": "Cameron", "plot": "A plot." }
    mocker.patch('popcorn_archives.core.fetch_movie_details_from_api', return_value=mock_api_response)
    
    mocker.patch('inquirer.prompt', return_value={'confirm': True})
    
    mock_add = mocker.patch('popcorn_archives.database.add_movie', return_value=True)
    mock_update = mocker.patch('popcorn_archives.database.update_movie_details')
    
    runner = CliRunner()
    result = runner.invoke(cli, ['info', 'Avatar 2009'])
    
    assert result.exit_code == 0
    assert "Movie 'Avatar (2009)' added" in result.output

def test_smart_info_partial_query_multiple_local_matches(mocker):
    """Tests choosing from a local ambiguous result."""
    mocker.patch('popcorn_archives.database.search_movie', return_value=[
        {'title': 'Terminator 2: Judgment Day', 'year': 1991},
        {'title': 'The Terminator', 'year': 1984}
    ])
    mock_movie_details = {'title': 'The Terminator', 'year': 1984, 'plot': 'A human soldier is sent...'}
    # CRITICAL: Mock the get_movie_details that is called *after* the choice.
    mocker.patch('popcorn_archives.database.get_movie_details', return_value=mock_movie_details)
    
    # FIX: Mock inquirer to return the user's choice.
    mocker.patch('inquirer.prompt', return_value={'choice': 'The Terminator (1984)'})
    
    runner = CliRunner()
    result = runner.invoke(cli, ['info', 'Terminator'])

    assert result.exit_code == 0
    assert "Found multiple matches" in result.output
    assert "A human soldier is sent..." in result.output

def test_smart_info_not_found_locally_multiple_online_matches(mocker):
    """Tests choosing from an online ambiguous result and confirming the add."""
    mocker.patch('popcorn_archives.database.search_movie', return_value=[])
    
    mock_api_multi = {"MultipleResults": [{'title': 'Alien', 'year': '1979'}, {'title': 'Aliens', 'year': '1986'}]}
    mock_api_details = {"genre": "Horror, Sci-Fi", "director": "James Cameron"}
    mocker.patch('popcorn_archives.core.fetch_movie_details_from_api', side_effect=[mock_api_multi, mock_api_details])
    
    mocker.patch('popcorn_archives.database.add_movie', return_value=True)
    mocker.patch('popcorn_archives.database.update_movie_details')
    mocker.patch('popcorn_archives.database.get_movie_details', return_value=None) # It's a new movie

    mocker.patch('inquirer.prompt', side_effect=[
        {'choice': 'Aliens (1986)'},
        {'confirm': True}
    ])

    runner = CliRunner()
    result = runner.invoke(cli, ['info', 'Alien'])

    assert result.exit_code == 0
    assert "Found multiple potential matches online" in result.output
    assert "James Cameron" in result.output
    assert "Movie 'Aliens (1986)' added" in result.output

def test_delete_command(mocker):
    """Tests the 'delete' command."""
    runner = CliRunner()
    
    mock_delete = mocker.patch('popcorn_archives.database.delete_movie', return_value=True)
    
    result = runner.invoke(cli, ['delete', 'Old Movie 1980'], input='y\n')
    
    assert result.exit_code == 0
    assert "Movie 'Old Movie (1980)' was successfully deleted." in result.output
    
    mock_delete.assert_called_once_with("Old Movie", 1980)

def test_delete_command_not_found(mocker):
    """Tests deleting a movie that doesn't exist."""
    runner = CliRunner()
    
    mocker.patch('popcorn_archives.database.delete_movie', return_value=False)
    
    result = runner.invoke(cli, ['delete', 'Ghost Movie 2000'], input='y\n')
    
    assert result.exit_code == 0
    assert "Movie 'Ghost Movie (2000)' not found in the archive." in result.output

def test_update_command(mocker):
    """Tests the 'update' command's workflow."""
    runner = CliRunner()
    
    mocker.patch('popcorn_archives.config.get_api_key', return_value='a_fake_api_key')
    
    mocker.patch('popcorn_archives.database.get_movies_missing_details', return_value=[
        {'title': 'Movie To Update', 'year': 2023}
    ])
    
    mock_api_response = {"Genre": "Sci-Fi", "Director": "A. Director", "Plot": "A plot.", "imdbRating": "7.5/10"}
    mock_fetch = mocker.patch('popcorn_archives.core.fetch_movie_details_from_api', return_value=mock_api_response)
    
    mock_db_update = mocker.patch('popcorn_archives.database.update_movie_details')
    
    result = runner.invoke(cli, ['update'])
    
    assert result.exit_code == 0
    assert "Update Summary" in result.output
    assert "Successfully updated: 1" in result.output
    
    mock_fetch.assert_called_once_with('Movie To Update', 2023)
    mock_db_update.assert_called_once_with('Movie To Update', 2023, mock_api_response)

def test_advanced_search_by_director(mocker):
    """Tests `search --director` and the rich output format."""
    mock_results = [
        {'title': 'Inception', 'year': 2010, 'director': 'Christopher Nolan', 'cast': '...'}
    ]
    mocker.patch('popcorn_archives.database.search_movies_advanced', return_value=mock_results)
    
    runner = CliRunner()
    result = runner.invoke(cli, ['search', '--director', 'Nolan'])
    
    assert result.exit_code == 0
    assert "Found 1 movies for director 'Nolan'" in result.output
    assert "Inception" in result.output
    assert "Directed by:" in result.output
    assert "Christopher Nolan" in result.output

def test_advanced_search_no_results(mocker):
    """Tests `search` when no movies match the criteria."""
    mocker.patch('popcorn_archives.database.search_movies_advanced', return_value=[])
    
    runner = CliRunner()
    result = runner.invoke(cli, ['search', '--actor', 'Nonexistent Actor'])
    
    assert result.exit_code == 0
    assert "No movies found matching your criteria." in result.output

def test_rate_command_success(mocker):
    """Tests the 'rate' command with valid input."""
    # Mock the database function to simulate a successful update
    mock_set_rating = mocker.patch('popcorn_archives.database.set_user_rating', return_value=(True, "Success"))
    
    runner = CliRunner()
    result = runner.invoke(cli, ['rate', 'Test Movie 2020', '9'])
    
    assert result.exit_code == 0
    assert "Successfully rated 'Test Movie (2020)' as 9/10." in result.output
    
    # Verify that the database function was called with the correct arguments
    mock_set_rating.assert_called_once_with("Test Movie", 2020, 9)

def test_rate_command_invalid_rating(mocker):
    """Tests the 'rate' command with a rating outside the 1-10 range."""
    runner = CliRunner()
    # The IntRange in the command itself should catch this
    result = runner.invoke(cli, ['rate', 'Test Movie 2020', '11'])
    
    assert result.exit_code != 0 # Should exit with an error
    assert "Invalid value for 'RATING'" in result.output

def test_info_displays_user_rating(mocker):
    """Tests that the 'info' command correctly displays the user's rating."""
    # Mock a movie that has a user rating
    mock_movie = {'title': 'The Matrix', 'year': 1999, 'user_rating': 10, 'plot': 'A plot.'}
    mocker.patch('popcorn_archives.database.get_movie_details', return_value=mock_movie)
    
    runner = CliRunner()
    result = runner.invoke(cli, ['info', 'The Matrix 1999'])
    
    assert result.exit_code == 0
    # Check for the visual representation (10 stars)
    assert "Your Rating: ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐" in result.output

def test_update_command_default_workflow(mocker):
    """Tests the default 'update' command's workflow."""
    mocker.patch('popcorn_archives.cli.config_manager.get_api_key', return_value='a_fake_api_key')
    mocker.patch('popcorn_archives.database.get_movies_missing_details', return_value=[
        {'title': 'Movie To Update', 'year': 2023}
    ])
    mock_api_response = {"plot": "A new plot."}
    mock_fetch = mocker.patch('popcorn_archives.core.fetch_movie_details_from_api', return_value=mock_api_response)
    mock_db_update = mocker.patch('popcorn_archives.database.update_movie_details')
    mocker.patch('time.sleep')

    runner = CliRunner()
    result = runner.invoke(cli, ['update'])
    
    assert result.exit_code == 0
    assert "Searching for movies with missing details" in result.output
    assert "Successfully updated: 1" in result.output
    mock_fetch.assert_called_once_with('Movie To Update', 2023)
    mock_db_update.assert_called_once()

def test_update_cleanup_mode_standalone(mocker):
    """Tests that `update --cleanup` alone only performs cleanup."""
    mock_cleanup = mocker.patch('popcorn_archives.database.cleanup_duplicates', return_value=2)
    mock_missing = mocker.patch('popcorn_archives.database.get_movies_missing_details')
    
    runner = CliRunner()
    result = runner.invoke(cli, ['update', '--cleanup'])
    
    assert result.exit_code == 0
    assert "Successfully merged 2 duplicate movies." in result.output
    assert "Cleanup complete." in result.output
    mock_missing.assert_not_called()