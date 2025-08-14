import os
import csv
import re
import requests
from tqdm import tqdm
from . import config as config_manager

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
    
    try:
        dirs_to_scan = [entry.name for entry in os.scandir(path) if entry.is_dir()]
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

BASE_URL = "https://api.themoviedb.org/3"

def fetch_movie_details_from_api(title, year):
    """
    Fetches detailed movie information directly from the TMDb API using requests.
    """
    api_key = config_manager.get_api_key()
    if not api_key:
        return {"Error": "API key not configured. Use 'poparch config --key YOUR_KEY' to set it."}

    headers = {"accept": "application/json"}
    
    try:
        search_params = {'api_key': api_key, 'query': title, 'year': year}
        search_response = requests.get(f"{BASE_URL}/search/movie", params=search_params, headers=headers, timeout=5)
        search_response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        search_data = search_response.json()

        if not search_data.get('results'):
            return {"Error": f"Movie '{title}' ({year}) not found on TMDb."}
        
        movie_id = search_data['results'][0]['id']

        details_params = {'api_key': api_key, 'append_to_response': 'credits'}
        details_response = requests.get(f"{BASE_URL}/movie/{movie_id}", params=details_params, headers=headers, timeout=5)
        details_response.raise_for_status()
        details = details_response.json()

        director = next((p['name'] for p in details.get('credits', {}).get('crew', []) if p.get('job') == 'Director'), "N/A")
        
        return {
            "Genre": ", ".join([g['name'] for g in details.get('genres', [])]),
            "Director": director,
            "Plot": details.get('overview', 'N/A'),
            "imdbRating": f"{details.get('vote_average', 0):.1f}/10"
        }
    except requests.exceptions.Timeout:
        return {"Error": "Request to TMDb API timed out after 5 seconds."}
    except requests.exceptions.RequestException as e:
        return {"Error": f"Network/API Error: {e}"}
    except Exception as e:
        return {"Error": f"An unexpected error occurred: {e}"}