import os
import csv
import re
from tqdm import tqdm

def parse_movie_title(name):
    """
    Parses the movie title and year from a string.
    Supports "Title YYYY" and "Title (YYYY)" formats, ignoring trailing metadata.
    """
    name = name.strip()

    match = re.match(r'^(.*) \((\d{4})\)', name)
    if match:
        title = match.group(1).strip()
        year = int(match.group(2))
        if 1800 < year < 2100:
            return title, year

    try:
        parts = name.split(' ')
        if len(parts) > 1:
            year = int(parts[-1])
            if 1800 < year < 2100:
                title = ' '.join(parts[:-1]).strip()
                return title, year
    except (ValueError, IndexError):
        pass

    return None, None

def scan_movie_folders(path):
    """
    Scans a directory for movie folders.
    Returns a tuple of two lists: (valid_movies, invalid_folders).
    """
    valid_movies = []
    invalid_folders = []
    
    dirs_to_scan = []
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    dirs_to_scan.append(entry.name)
    except OSError:
        return [], []

    for dir_name in tqdm(dirs_to_scan, desc="Scanning for movies"):
        title, year = parse_movie_title(dir_name)
        if title and year:
            valid_movies.append((title, year))
        else:
            invalid_folders.append(dir_name)
            
    return valid_movies, invalid_folders

def read_csv_file(filepath):
    """Reads a CSV file and returns a list of movies."""
    movie_list = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            try:
                next(reader)
            except StopIteration:
                return []

            for row in reader:
                if row:
                    title, year = parse_movie_title(row[0])
                    if title and year:
                        movie_list.append((title, year))
    except FileNotFoundError:
        return None
    return movie_list