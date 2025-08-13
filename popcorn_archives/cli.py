import click
from tqdm import tqdm 
from . import database
from . import core

@click.group()
def cli():
    """
    Popcorn Archives: A CLI tool for managing your movie watchlist.
    """
    database.init_db()

@cli.command()
@click.argument('name')
def add(name):
    """
    Adds a new movie to the archive.
    The movie name must be in "Title YYYY" format.
    
    Example: popcorn-archives add "The Kid 1921"
    """
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
    valid_movies, invalid_folders = core.scan_movie_folders(path)

    # First, display warnings for folders that could not be parsed.
    if invalid_folders:
        click.echo(click.style("\nWarning: The following folders could not be parsed and will be skipped:", fg='yellow'))
        for folder in invalid_folders:
            safe_echo(f"  - {folder}")
    
    # Now, handle the valid movies.
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
    movies_to_add = core.read_csv_file(filepath)
    if not movies_to_add:
        click.echo("No movies found to import in the CSV file.")
        return

    click.echo(f"Found {len(movies_to_add)} movies in the CSV file.")
    if click.confirm("Do you want to add these movies to the archive?"):
        count = 0
        # Add a progress bar to the loop
        for title, year in tqdm(movies_to_add, desc="Importing CSV"):
            if database.add_movie(title, year):
                count += 1
        click.echo(click.style(f"{count} new movies imported successfully from the CSV file.", fg='green'))


@cli.command()
@click.argument('name')
def delete(name):
    """
    Deletes a specific movie from the archive.
    Movie format: "Title YYYY" or "Title (YYYY)"
    """
    title, year = core.parse_movie_title(name)
    if not title or not year:
        click.echo(click.style(f"Error: Invalid movie format for '{name}'.", fg='red'))
        return

    # Get confirmation from the user
    prompt_message = f"Are you sure you want to delete '{title} ({year})'?"
    if click.confirm(prompt_message):
        if database.delete_movie(title, year):
            click.echo(click.style(f"Movie '{title} ({year})' was successfully deleted.", fg='green'))
        else:
            click.echo(click.style(f"Movie '{title} ({year})' not found in the archive.", fg='yellow'))


@cli.command()
def clear():
    """
    !!! Deletes ALL movies from the archive !!!
    """
    # Get serious confirmation from the user
    warning = "Warning: This operation will permanently delete ALL movies from your archive."
    click.echo(click.style(warning, fg='red', bold=True))
    
    if click.confirm("Are you absolutely sure you want to do this?"):
        database.clear_all_movies()
        click.echo(click.style("The movie archive has been successfully cleared.", fg='green'))


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
def random():
    """Suggests a random movie from the archive."""
    movie = database.get_random_movie()
    if movie:
        title, year = movie
        click.echo("Today's random movie suggestion:")
        click.echo(click.style(f"-> {title} ({year})", fg='cyan', bold=True))
    else:
        click.echo("The archive is empty. Add some movies first.")

@cli.command()
@click.argument('year', type=int)
def year(year_num):
    """Lists all movies from a specific year."""
    results = database.get_movies_by_year(year_num)
    if results:
        click.echo(f"Movies from {year_num}:")
        for title, _ in results:
            click.echo(f"- {title}")
    else:
        click.echo(f"No movies found for the year {year_num}.")

@cli.command()
@click.argument('decade', type=int)
def decade(decade_num):
    """Lists all movies from a specific decade."""
    if not (1800 <= decade_num <= 2100 and decade_num % 10 == 0):
        click.echo(click.style("Error: Decade must be a valid start of a decade (e.g., 1980, 1990, 2020).", fg='red'))
        return
        
    results = database.get_movies_by_decade(decade_num)
    if results:
        click.echo(f"Movies from the {decade_num}s:")
        for title, year in results:
            click.echo(f"- {title} ({year})")
    else:
        click.echo(f"No movies found for the {decade_num}s decade.")

if __name__ == '__main__':
    cli()