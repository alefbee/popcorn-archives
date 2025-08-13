import click
import csv
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
    # We import DB_FILE directly from the database module to ensure we get the correct path
    from .database import DB_FILE
    click.echo("The database file is located at:")
    click.echo(click.style(DB_FILE, fg='green'))

if __name__ == '__main__':
    cli()