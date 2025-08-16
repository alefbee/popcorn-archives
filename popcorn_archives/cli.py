import click
import csv
import time
from tqdm import tqdm
from click import version_option
from importlib.metadata import version
from . import database
from . import config as config_manager

@version_option(version=version("popcorn-archives"), prog_name="popcorn-archives")
@click.group()
def cli():
    """
    Popcorn Archives: A CLI tool for managing your movie watchlist.
    """
    database.init_db()

@cli.command()
def stats():
    """Displays beautiful and interesting statistics about the movie archive."""
    total_count = database.get_total_movies_count()
    if total_count == 0:
        click.echo("The archive is empty. Add some movies first!")
        return
        
    click.echo(click.style("\n🎬 Popcorn Archives Dashboard", bold=True, fg='cyan'))
    
    click.echo(click.style("\nSummary", bold=True))
    click.echo("-------")
    click.echo(f"Total Movies: {click.style(str(total_count), fg='green', bold=True)}")

    watched_stats = database.get_watched_stats()
    if watched_stats and watched_stats[0] is not None:
        watched_count, unwatched_count = watched_stats
        click.echo(f"  - Watched:   {watched_count}")
        click.echo(f"  - Unwatched: {unwatched_count}")
    
    oldest = database.get_oldest_movie()
    newest = database.get_newest_movie()
    
    if oldest and newest:
        time_span = newest[0]['year'] - oldest[0]['year']
        click.echo(f"Time Span:    Covering {click.style(str(time_span), bold=True)} years of cinema")
        click.echo(f"Oldest Movie: {oldest[0]['title']} ({oldest[0]['year']})")
        click.echo(f"Newest Movie: {newest[0]['title']} ({newest[0]['year']})")
    
    click.echo(click.style("\nDecade Distribution", bold=True))
    click.echo("-------------------")
    
    decade_dist = database.get_decade_distribution()
    if decade_dist:
        max_count = decade_dist[0]['movie_count']
        BAR_CHAR = "█"
        MAX_BAR_WIDTH = 40
        
        COLORS = ['cyan', 'magenta', 'yellow', 'blue']

        for i, row in enumerate(decade_dist):
            decade = int(row['decade'])
            count = row['movie_count']
            
            decade_label = f"{decade}s"
            formatted_label = f"{decade_label: <8}"
            
            bar_color = COLORS[i % len(COLORS)]
            bar_length = int((count / max_count) * MAX_BAR_WIDTH) if max_count > 0 else 0
            bar = BAR_CHAR * bar_length
            
            click.echo(
                f"  {click.style(formatted_label, bold=True)}"
                f"| {click.style(bar, fg=bar_color)} {count}"
            )
    else:
        click.echo("Not enough data for decade distribution.")
    
    click.echo("")


@cli.command()
@click.argument('name')
def add(name):
    """
    Adds a new movie to the archive.
    The movie name must be in "Title YYYY" format.
    
    Example: popcorn-archives add "The Kid 1921"
    """
    from . import core
    title, year = core.parse_movie_title(name)
    if not title or not year:
        click.echo(click.style(f"Error: Invalid movie format '{name}'. Must be 'Title YYYY'.", fg='red'))
        return

    if database.add_movie(title, year):
        click.echo(click.style(f"Movie '{title} ({year})' added successfully.", fg='green'))
    else:
        click.echo(click.style(f"Movie '{title} ({year})' already exists in the archive.", fg='yellow'))

def safe_echo(text):
    """A helper function to print text safely, replacing problematic characters."""
    safe_text = text.encode('utf-8', errors='replace').decode('utf-8')
    click.echo(safe_text)

@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False))
def scan(path):
    """Scans a directory for movie folders to add."""
    from . import core
    valid_movies, invalid_folders = core.scan_movie_folders(path)

    if invalid_folders:
        click.echo(click.style("\nWarning: The following folders could not be parsed and will be skipped:", fg='yellow'))
        for folder in invalid_folders:
            safe_echo(f"  - {folder}")
    
    if not valid_movies:
        click.echo("\nNo movies with a valid format were found.")
        return

    click.echo(click.style(f"\nFound {len(valid_movies)} valid movies:", bold=True))
    for title, year in valid_movies[:5]:
        safe_echo(f"  - {title} ({year})")
    if len(valid_movies) > 5:
        click.echo("  ...")

    if click.confirm("\nDo you want to add these movies to the archive?"):
        added_count = 0
        skipped_count = 0
        for title, year in tqdm(valid_movies, desc="Adding to database"):
            if database.add_movie(title, year):
                added_count += 1
            else:
                skipped_count += 1
        
        click.echo(click.style("\nOperation complete:", bold=True))
        click.echo(click.style(f"  {added_count} new movies added successfully.", fg='green'))
        if skipped_count > 0:
            click.echo(click.style(f"  {skipped_count} movies were already in the archive.", fg='yellow'))
    else:
        click.echo(click.style("Operation cancelled. No movies were added to the archive.", fg='red'))


@cli.command(name='import')
@click.argument('filepath', type=click.Path(exists=True, dir_okay=False))
def import_csv(filepath):
    """Imports movies from a CSV file."""
    from . import core
    movies_to_add = core.read_csv_file(filepath)
    if not movies_to_add:
        click.echo("No movies found to import in the CSV file.")
        return

    click.echo(f"Found {len(movies_to_add)} movies in the CSV file.")
    if click.confirm("Do you want to add these movies to the archive?"):
        count = 0
        for title, year in tqdm(movies_to_add, desc="Importing CSV"):
            if database.add_movie(title, year):
                count += 1
        click.echo(click.style(f"{count} new movies imported successfully from the CSV file.", fg='green'))

@cli.command()
@click.argument('query')
def search(query):
    """Searches for a movie in the archive."""
    results = database.search_movie(query)
    if results:
        click.echo("Found results:")
        for title, year in results:
            click.echo(f"- {title} ({year})")
    else:
        click.echo("No movie found with that query.")

@cli.command()
@click.option('--unwatched', is_flag=True, help="Suggest a random movie you haven't watched yet.")
def random(unwatched):
    """Suggests a random movie from the archive."""
    if unwatched:
        movie = database.get_random_unwatched_movie()
        if not movie:
            click.echo("You've watched all the movies in your archive! 🎉")
            return
    else:
        movie = database.get_random_movie()

    if movie:
        title, year = movie
        click.echo("Today's random movie suggestion:")
        click.echo(click.style(f"-> {title} ({year})", fg='cyan', bold=True))
    else:
        click.echo("The archive is empty. Add some movies first.")

@cli.command()
@click.argument('year', type=int)
def year(year):
    """Lists all movies from a specific year."""
    results = database.get_movies_by_year(year)
    if results:
        click.echo(f"Movies from {year}:")
        for title, _ in results:
            safe_echo(f"- {title}")
    else:
        click.echo(f"No movies found for the year {year}.")

@cli.command()
@click.argument('decade', type=int)
def decade(decade):
    """Lists all movies from a specific decade."""
    if not (1800 <= decade <= 2100 and decade % 10 == 0):
        click.echo(click.style("Error: Decade must be a valid start of a decade (e.g., 1980, 1990, 2020).", fg='red'))
        return
        
    results = database.get_movies_by_decade(decade)
    if results:
        click.echo(f"Movies from the {decade}s:")
        for title, yr in results:
            safe_echo(f"- {title} ({yr})")
    else:
        click.echo(f"No movies found for the {decade}s decade.")

@cli.command()
@click.argument('name')
def delete(name):
    """
    Deletes a specific movie from the archive.
    Movie format: "Title YYYY" or "Title (YYYY)"
    """
    from . import core
    title, year = core.parse_movie_title(name)
    if not title or not year:
        click.echo(click.style(f"Error: Invalid movie format for '{name}'.", fg='red'))
        return

    prompt_message = f"Are you sure you want to delete '{title} ({year})'?"
    if click.confirm(prompt_message):
        if database.delete_movie(title, year):
            click.echo(click.style(f"Movie '{title} ({year})' was successfully deleted.", fg='green'))
        else:
            click.echo(click.style(f"Movie '{title} ({year})' not found in the archive.", fg='yellow'))

@cli.command()
@click.argument('filepath', type=click.Path(dir_okay=False, writable=True))
def export(filepath):
    """Exports the entire movie archive to a CSV file."""
    click.echo(f"Exporting archive to '{filepath}'...")
    
    all_movies = database.get_all_movies()
    if not all_movies:
        click.echo(click.style("Archive is empty. Nothing to export.", fg='yellow'))
        return

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            writer.writerow(['name'])
            
            for title, year in tqdm(all_movies, desc="Exporting"):
                writer.writerow([f"{title} {year}"])
        
        click.echo(click.style(f"Successfully exported {len(all_movies)} movies to '{filepath}'.", fg='green'))

    except IOError as e:
        click.echo(click.style(f"Error: Could not write to file at '{filepath}'.\n{e}", fg='red'))

@cli.command()
def clear():
    """
    !!! Deletes ALL movies from the archive !!!
    """
    warning = "Warning: This operation will permanently delete ALL movies from your archive."
    click.echo(click.style(warning, fg='red', bold=True))
    
    if click.confirm("Are you absolutely sure you want to do this?"):
        database.clear_all_movies()
        click.echo(click.style("The movie archive has been successfully cleared.", fg='green'))

@cli.command()
def where():
    """Displays the full path to the application's database file."""
    from . import core
    from .database import DB_FILE
    click.echo("The database file is located at:")
    click.echo(click.style(DB_FILE, fg='green'))

def _set_watched_status_by_name(name: str, status: bool):
    """Helper function to set watched status for watch/unwatch commands."""
    from . import core
    title, year = core.parse_movie_title(name)
    if not title or not year:
        click.echo(click.style(f"Error: Invalid movie format for '{name}'.", fg='red'))
        return

    if database.set_movie_watched_status(title, year, status):
        action = "watched" if status else "unwatched"
        click.echo(click.style(f"Movie '{title} ({year})' marked as {action}.", fg='green'))
    else:
        click.echo(click.style(f"Movie '{title} ({year})' not found in the archive.", fg='yellow'))

@cli.command()
@click.argument('name')
def watch(name):
    """Marks a movie as 'watched'."""
    _set_watched_status_by_name(name, status=True)

@cli.command()
@click.argument('name')
def unwatch(name):
    """Marks a movie as 'unwatched'."""
    _set_watched_status_by_name(name, status=False)

@cli.command()
@click.option('--key', help="Your TMDb API key to save to the configuration.")
def config(key):
    """Configures the application, such as setting the API key."""
    if key:
        config_manager.save_api_key(key)
        click.echo(click.style("API key saved successfully.", fg='green'))
    else:
        click.echo("Usage: poparch config --key YOUR_API_KEY")
        if config_manager.get_api_key():
            click.echo("An API key is already configured.")

@cli.command(name='info')
@click.argument('query')
def smart_info(query):
    """
    Smartly finds a movie and displays its details.
    Searches your local archive first, then online. Handles ambiguity.
    """
    from . import core
    import textwrap

    def _display_and_add_flow(title, year):
        """Helper to display details and ask to add a movie."""
        details = core.fetch_movie_details_from_api(title, year)
        if details.get("Error"):
            click.echo(click.style(f"Error fetching details: {details['Error']}", fg='red'))
            return

        display_details = {'title': title, 'year': year, **details}
        display_movie_details(display_details)

        if not details.get('in_archive') and click.confirm("\nDo you want to add this movie to your archive?", default=True):
            if database.add_movie(title, year):
                database.update_movie_details(title, year, details)
                click.echo(click.style(f"Movie '{title} ({year})' added.", fg='green'))
            else:
                click.echo(click.style(f"Movie '{title} ({year})' already exists.", fg='yellow'))
        elif not details.get('in_archive'):
            click.echo("Movie was not added to the archive.")

        # --- Step 1: Handle if user provides a full name like "Title YYYY" ---
    title, year = core.parse_movie_title(query)
    if title and year:
        movie_row = database.get_movie_details(title, year)
        if not movie_row:
            click.echo(f"Movie not found locally. Searching online for '{title} ({year})'...")
            _display_and_add_flow(title, year)
        else:
            # --- FIX: Convert sqlite3.Row to a dict before displaying ---
            display_movie_details(dict(movie_row))
        return

    # --- Step 2: Handle partial names (no year provided) ---
    click.echo(f"Searching local archive for movies matching '{query}'...")
    local_results = database.search_movie(query)

    if len(local_results) == 1:
        movie_row = local_results[0]
        click.echo(f"Found one match: {movie_row['title']} ({movie_row['year']}).")
        # --- FIX: Convert sqlite3.Row to a dict before displaying ---
        full_details = database.get_movie_details(movie_row['title'], movie_row['year'])
        display_movie_details(dict(full_details))
        return
    
    if len(local_results) > 1:
        click.echo("Found multiple matches in your archive. Please choose one:")
        for i, movie_row in enumerate(local_results, 1):
            click.echo(f"  {i}. {movie_row['title']} ({movie_row['year']})")
        
        try:
            choice_str = click.prompt("\nEnter the number of your choice", type=str)
            choice_idx = int(choice_str) - 1
            if 0 <= choice_idx < len(local_results):
                chosen_movie_row = local_results[choice_idx]
                full_details = database.get_movie_details(chosen_movie_row['title'], chosen_movie_row['year'])
                # --- FIX: Convert sqlite3.Row to a dict before displaying ---
                display_movie_details(dict(full_details))
            else:
                click.echo(click.style("Invalid choice.", fg='red'))
        except (ValueError, IndexError):
            click.echo(click.style("Invalid input.", fg='red'))
        return

    # --- Step 3: If nothing found locally, search online ---
    click.echo("No local matches found. Searching online on TMDb...")
    online_results = core.fetch_movie_details_from_api(query)

    if online_results.get("Error"):
        click.echo(click.style(online_results["Error"], fg='red'))
        return
    
    if online_results.get("MultipleResults"):
        click.echo("Found multiple potential matches online. Which one did you mean?")
        choices = online_results["MultipleResults"]
        for i, movie in enumerate(choices, 1):
            click.echo(f"  {i}. {movie['title']} ({movie['year']})")

        try:
            choice_str = click.prompt("\nEnter the number of your choice", type=str)
            choice_idx = int(choice_str) - 1
            if 0 <= choice_idx < len(choices):
                chosen_movie = choices[choice_idx]
                _display_and_add_flow(chosen_movie['title'], chosen_movie['year'])
            else:
                click.echo(click.style("Invalid choice.", fg='red'))
        except (ValueError, IndexError):
            click.echo(click.style("Invalid input.", fg='red'))
        return
    
    # If we get here, it means the API returned a single, unambiguous result.
    _display_and_add_flow(query, online_results.get('year'))

def display_movie_details(movie):
    """A helper function to consistently display movie details."""
    import textwrap
    click.echo(click.style(f"\n🎬 {movie['title']} ({movie['year']})", bold=True, fg='cyan'))
    click.echo("-" * (len(movie['title']) + len(str(movie['year'])) + 5))

    runtime_str = f"{movie.get('runtime')} min" if movie.get('runtime') else "N/A"
    score_str = movie.get('tmdb_score') or "N/A"
    click.echo(f"  {'TMDb Score:':<15} {score_str:<15} | {'Runtime:':<10} {runtime_str}")
    click.echo(f"  {'Genre:':<15} {movie.get('genre', 'N/A')}")
    click.echo(f"  {'Director:':<15} {movie.get('director', 'N/A')}")
    click.echo(f"  {'Cast:':<15} {movie.get('cast', 'N/A')}")
    if movie.get('collection'):
        click.echo(f"  {'Collection:':<15} {movie.get('collection')}")
    if movie.get('imdb_id'):
        imdb_link = f"https://www.imdb.com/title/{movie.get('imdb_id')}/"
        click.echo(f"  {'IMDb Page:':<15} {imdb_link}")
    if movie.get('plot'):
        click.echo(click.style("\nPlot:", bold=True))
        plot_wrapped = '\n'.join(textwrap.wrap(movie['plot'], width=70, initial_indent='  ', subsequent_indent='  '))
        click.echo(plot_wrapped)
    click.echo("")

@cli.command()
@click.argument('genre_name', required=False)
def genre(genre_name):
    """
    Lists movies by genre. If no genre is provided, it shows an
    interactive list of available genres to choose from.
    """
    
    if genre_name:
        results = database.get_movies_by_genre(genre_name)
        if not results:
            click.echo(f"No movies found with the genre '{genre_name}'.")
            return
    else:
        available_genres = database.get_all_unique_genres()
        if not available_genres:
            click.echo(click.style("No genres found in the database.", fg='yellow'))
            click.echo("Run 'poparch update' to fetch movie details first.")
            return

        click.echo(click.style("Please choose a genre from the list:", bold=True))
        for i, g_name in enumerate(available_genres, 1):
            click.echo(f"  {i}. {g_name}")

        try:
            choice_str = click.prompt("\nEnter the number of your choice", type=str)
            choice_index = int(choice_str) - 1

            if 0 <= choice_index < len(available_genres):
                selected_genre = available_genres[choice_index]
                results = database.get_movies_by_genre(selected_genre)
            else:
                click.echo(click.style("Invalid choice. Please enter a valid number.", fg='red'))
                return
        except (ValueError, IndexError):
            click.echo(click.style("Invalid input. Please enter a number.", fg='red'))
            return

    display_genre = genre_name if genre_name else selected_genre
    click.echo(click.style(f"\nMovies matching genre '{display_genre}':", bold=True))
    for row in results:
        safe_echo(f"  - {row['title']} ({row['year']})")

@cli.command()
@click.option('--force', is_flag=True, help="Force update for all movies, even those with existing details.")
def update(force):
    """
    Fetches details (genre, plot, etc.) for movies from TMDb.
    By default, it only fetches for movies with missing details.
    """
    from . import core
    if not config_manager.get_api_key():
        click.echo(click.style("Error: API key not configured. Use 'poparch config --key YOUR_KEY' to set it.", fg='red'))
        return

    if force:
        movies_to_update = database.get_all_movies()
        click.echo("Fetching details for all movies in the archive (force update)...")
    else:
        movies_to_update = database.get_movies_missing_details()
        click.echo("Searching for movies with missing details to update...")

    if not movies_to_update:
        click.echo(click.style("All movies are already up-to-date.", fg='green'))
        return

    updated_count = 0
    failed_movies = []
    
    try:
        with tqdm(total=len(movies_to_update), desc="Updating movies") as pbar:
            for movie in movies_to_update:
                title, year = movie['title'], movie['year']
                
                pbar.set_description(f"Fetching: {title[:30]}")
                
                details = core.fetch_movie_details_from_api(title, year)
                
                if not details.get("Error"):
                    database.update_movie_details(title, year, details)
                    updated_count += 1
                else:
                    failed_movies.append((f"{title} ({year})", details['Error']))
                
                pbar.update(1)
                time.sleep(0.1) 
    except KeyboardInterrupt:
        click.echo(click.style("\n\nOperation aborted by user.", fg='yellow'))
    finally:
        total_processed = pbar.n if 'pbar' in locals() else 0
        click.echo(click.style(f"\n--- Update Summary ---", bold=True))
        click.echo(click.style(f"  Processed:    {total_processed}/{len(movies_to_update)}", fg='cyan'))
        click.echo(click.style(f"  Successfully updated: {updated_count}", fg='green'))
        
        if failed_movies:
            failed_count = len(failed_movies)
            click.echo(click.style(f"  Failed to update:   {failed_count}", fg='red'))
            click.echo(click.style("\nFailed items (please check title/year or network connection):", bold=True))
            for movie_name, error_reason in failed_movies:
                if "not found" in error_reason:
                    error_display = "Not found on TMDb"
                elif "timed out" in error_reason:
                    error_display = "Network timeout"
                else:
                    error_display = "API Error"
                
                click.echo(f"  - {movie_name:<40} | Reason: {error_display}")


if __name__ == '__main__':
    cli()