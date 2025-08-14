from click.testing import CliRunner
from popcorn_archives.cli import cli

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

def test_info_command_with_mock_api(mocker):
    """Tests the info command's workflow with mocked API and DB."""
    mocker.patch('popcorn_archives.config.get_api_key', return_value='a_fake_api_key')

    db_side_effects = [
        {'title': 'Pulp Fiction', 'year': 1994, 'plot': None},
        {'title': 'Pulp Fiction', 'year': 1994, 'plot': 'The plot.', 'genre': 'Crime', 'director': 'Tarantino', 'imdb_rating': '8.9/10'}
    ]
    mocker.patch('popcorn_archives.database.get_movie_details', side_effect=db_side_effects)

    mock_api_response = {"Genre": "Crime", "Director": "Tarantino", "Plot": "The plot.", "imdbRating": "8.9/10"}
    mocker.patch('popcorn_archives.core.fetch_movie_details_from_api', return_value=mock_api_response)
    mocker.patch('popcorn_archives.database.update_movie_details', return_value=None)

    runner = CliRunner()
    result = runner.invoke(cli, ['info', 'Pulp Fiction 1994'])

    assert result.exit_code == 0
    assert "Fetching details from TMDb API..." in result.output
    assert "Tarantino" in result.output

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