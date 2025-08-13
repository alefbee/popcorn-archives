import os
import csv
import re
from tqdm import tqdm

def parse_movie_title(name):
    """
    Parses the movie title and year from a string.
    Supports two formats: "Title YYYY" and "Title (YYYY)".
    """
    name = name.strip()

    # Attempt to find the "Title (YYYY)" format
    # Example: "A Clockwork Orange (1971)"
    match = re.match(r'^(.*) \((\d{4})\)$', name)
    if match:
        title = match.group(1).strip()
        year = int(match.group(2))
        if 1800 < year < 2100:
            return title, year

    # If the above format is not found, attempt the "Title YYYY" format
    # Example: "The Kid 1921"
    try:
        parts = name.split(' ')
        if len(parts) > 1:
            year = int(parts[-1])
            if 1800 < year < 2100:
                title = ' '.join(parts[:-1]).strip()
                return title, year
    except (ValueError, IndexError):
        # If converting to a number fails, simply pass
        pass

    return None, None

def scan_movie_folders(path):
    """
    Scans a directory for movie folders and returns a list of movies.
    """
    movie_list = []
    
    # First, collect the list of directories to be able to show a progress bar
    dirs_to_scan = []
    try:
        # Use os.scandir for better performance on large directories
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    dirs_to_scan.append(entry.name)
    except OSError:
        # Handle potential permission errors
        return []

    # Use tqdm for a progress bar, as scanning can take time
    for dir_name in tqdm(dirs_to_scan, desc="Scanning for movies"):
        title, year = parse_movie_title(dir_name)
        if title and year:
            movie_list.append((title, year))
            
    return movie_list

def read_csv_file(filepath):
    """Reads a CSV file and returns a list of movies."""
    movie_list = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            try:
                next(reader)  # Skip the header row
            except StopIteration:
                return []  # The file is empty

            for row in reader:
                if row:
                    title, year = parse_movie_title(row[0])
                    if title and year:
                        movie_list.append((title, year))
    except FileNotFoundError:
        return None
    return movie_list