import os
import csv

def parse_movie_title(name):
    """
    Parses the movie title and year from a string (format: The Kid 1921).
    """
    try:
        parts = name.strip().split(' ')
        year = int(parts[-1])
        # Ensure the last part is a valid year (e.g., between 1800 and 2100)
        if 1800 < year < 2100:
            title = ' '.join(parts[:-1])
            return title, year
    except (ValueError, IndexError):
        return None, None
    return None, None

def scan_movie_folders(path):
    """
    Scans a directory to find movie folders and returns a list of movies.
    """
    movie_list = []
    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            title, year = parse_movie_title(dir_name)
            if title and year:
                movie_list.append((title, year))
        # We only scan the top-level directories
        break
    return movie_list

def read_csv_file(filepath):
    """
    Reads a CSV file and returns a list of movies.
    """
    movie_list = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            for row in reader:
                if row:
                    title, year = parse_movie_title(row[0])
                    if title and year:
                        movie_list.append((title, year))
    except FileNotFoundError:
        return None
    return movie_list