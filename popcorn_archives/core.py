import os
import csv
import re
import requests
from tqdm import tqdm
from . import config as config_manager
import zipfile
from . import logger as app_logger

def parse_movie_title(name):
    """
    Parses the movie title and year from a string.
    Supports "Title YYYY" and "Title (YYYY)" formats, ignoring trailing metadata.
    Returns (None, None) if no valid year is found.
    """
    name = name.strip()
    # This regex is more robust and handles both formats
    match = re.match(r'^(.*?)[\s\(](\d{4})[\)]?.*$', name)
    if match:
        title = match.group(1).strip().title()
        year = int(match.group(2))
        if 1800 < year < 2100:
            return title, year
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

def fetch_movie_details_from_api(title, year=None, ignore_year_in_search=False):
    """
    Fetches a rich and comprehensive set of movie details from TMDb.
    """
    api_key = config_manager.get_api_key()
    if not api_key:
        return {"Error": "API key not configured."}
    
    headers = {"accept": "application/json"}
    
    try:
        # Step 1: Search for the movie
        search_params = {'api_key': api_key, 'query': title}
        if year and not ignore_year_in_search:
            search_params['year'] = year
            
        search_response = requests.get(f"{BASE_URL}/search/movie", params=search_params, headers=headers, timeout=10)
        search_response.raise_for_status()
        search_data = search_response.json()

        if not search_data.get('results'):
            return {"Error": f"Movie '{title}' not found on TMDb."}

        # Step 2: Intelligently find the best match from the results
        sorted_results = sorted(search_data['results'], key=lambda r: r.get('popularity', 0), reverse=True)
        
        best_match = sorted_results[0] # Default to the most popular result
        if year:
            # If a year was provided, try to find a perfect year match within the popular results.
            # If not found, we still stick with the most popular one overall.
            year_match = next((r for r in sorted_results if str(year) in r.get('release_date', '')), None)
            if year_match:
                best_match = year_match
        
        # If the search was broad (no year) and returned multiple results, let the user choose.
        if len(sorted_results) > 1 and not year:
             return {"MultipleResults": [{'title': r.get('title'), 'year': r.get('release_date', 'N/A')[:4]} for r in sorted_results[:5]]}
        
        movie_id = best_match['id']

        # Step 3: Get full details for the chosen movie ID
        details_params = {'api_key': api_key, 'append_to_response': 'credits,keywords'}
        details_response = requests.get(f"{BASE_URL}/movie/{movie_id}", params=details_params, headers=headers, timeout=10)
        details_response.raise_for_status()
        details = details_response.json()

        # Step 4: Process and format all data
        crew = details.get('credits', {}).get('crew', [])
        directors = [p['name'] for p in crew if p.get('job') == 'Director']
        writers = ", ".join(sorted(list(set(p['name'] for p in crew if p.get('department') == 'Writing'))))
        dop = next((p['name'] for p in crew if p.get('job') == 'Director of Photography'), "N/A")
        
        cast = ", ".join([p['name'] for p in details.get('credits', {}).get('cast', [])[:7]])
        keywords = ", ".join([k['name'] for k in details.get('keywords', {}).get('keywords', [])])
        tmdb_score = f"{int(details.get('vote_average', 0) * 10)}%"
        collection_info = details.get('belongs_to_collection')
        companies = ", ".join([c['name'] for c in details.get('production_companies', [])[:3]])
        
        final_title = details.get('title', title)
        final_year = int(details.get('release_date', '0-0-0')[:4])

        app_logger.log_info(f"Successfully fetched details for '{final_title}' from API.")

        return {
            "title": final_title,
            "year": final_year,
            "genre": ", ".join([g['name'] for g in details.get('genres', [])]),
            "director": ", ".join(directors) if directors else "N/A",
            "plot": details.get('overview', 'N/A'),
            "tmdb_score": tmdb_score,
            "imdb_id": details.get('imdb_id'),
            "runtime": details.get('runtime'),
            "cast": cast, "keywords": keywords,
            "collection": collection_info['name'] if collection_info else None,
            "tagline": details.get('tagline'),
            "writers": writers,
            "dop": dop,
            "original_language": details.get('original_language'),
            "poster_path": details.get('poster_path'),
            "budget": details.get('budget'),
            "revenue": details.get('revenue'),
            "production_companies": companies
        }
    
    except requests.exceptions.Timeout:
        return {"Error": "Request to TMDb API timed out."}
    except requests.exceptions.RequestException as e:
        app_logger.log_error(f"Network/API Error for '{title} ({year})': {e}")
        return {"Error": f"Network/API Error"}
    except Exception as e:
        app_logger.log_error(f"An unexpected error occurred for '{title} ({year})': {e}")
        return {"Error": f"An unexpected error occurred"}
    
def process_letterboxd_zip(filepath):
    """
    Processes a Letterboxd ZIP export and categorizes movies.
    Returns three lists: (movies_to_update, movies_to_add, not_found_list)
    """
    from . import database # Lazy load

    try:
        with zipfile.ZipFile(filepath, 'r') as zf:
            # Check for ratings.csv first, as it contains the most info
            if 'ratings.csv' not in zf.namelist():
                return None, None, {"Error": "ratings.csv not found in the ZIP file."}
            
            with zf.open('ratings.csv') as csv_file:
                # We need to decode the bytes to text for the csv reader
                content = csv_file.read().decode('utf-8')
                reader = csv.DictReader(content.splitlines())
                
                movies_to_update = []
                movies_to_add = []

                for row in reader:
                    title, year = row.get('Name'), row.get('Year')
                    rating = row.get('Rating')
                    if not title or not year: continue
                    
                    movie_data = {
                        'title': title,
                        'year': int(year),
                        'rating': int(float(rating) * 2) if rating else None, # Convert 0.5-5 to 1-10
                        'watched': True # If it has a rating, it's been watched
                    }

                    # Check if the movie exists in our local database
                    if database.get_movie_details(title, int(year)):
                        movies_to_update.append(movie_data)
                    else:
                        movies_to_add.append(movie_data)
        
        return movies_to_update, movies_to_add, None
    except Exception as e:
        return None, None, {"Error": f"Failed to process ZIP file: {e}"}