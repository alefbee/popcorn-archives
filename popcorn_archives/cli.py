# popcorn_archives/cli.py

import click
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

@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False))
def scan(path):
    """Scans a directory for movie folders to add."""
    movies_to_add = core.scan_movie_folders(path)
    if not movies_to_add:
        click.echo("No valid movie folders found in this directory.")
        return

    click.echo("The following movies were found:")
    for title, year in movies_to_add:
        click.echo(f"- {title} ({year})")
    
    if click.confirm("Do you want to add these movies to the archive?"):
        count = 0
        for title, year in movies_to_add:
            if database.add_movie(title, year):
                count += 1
        click.echo(click.style(f"{count} new movies added successfully.", fg='green'))

@cli.command(name='import')
@click.argument('filepath', type=click.Path(exists=True, dir_okay=False))
def import_csv(filepath):
    """Imports movies from a CSV file."""
    movies_to_add = core.read_csv_file(filepath)
    if movies_to_add is None:
        click.echo(click.style(f"Error: File not found at '{filepath}'.", fg='red'))
        return
        
    if not movies_to_add:
        click.echo("No movies found to import in the CSV file.")
        return

    count = 0
    for title, year in movies_to_add:
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