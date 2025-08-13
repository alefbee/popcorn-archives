# Popcorn Archives 🍿

A simple and powerful command-line tool to manage your movie watchlist. Never forget a movie you wanted to watch again!

## Features

-   **Add Movies**: Manually add movies to your personal database.
-   **Bulk Import**: Import movies from a CSV file.
-   **Scan Directories**: Automatically detect and add movies by scanning your movie folders.
-   **Search**: Quickly check if a movie is already in your archive.
-   **Random Suggestion**: Get a random movie suggestion for movie night.
-   **Filter by Year/Decade**: List all movies from a specific year or decade.
-   **Persistent Storage**: Uses a local SQLite database to store your list.

## Installation

1.  Clone this repository or download the source code.
2.  Navigate to the project's root directory.
3.  Install the project in editable mode using pip:

    ```bash
    pip install -e .
    ```

This will install the `popcorn-archives` command and make it available system-wide.

## Usage

The application is straightforward to use. Here are the available commands:

### Add a Movie

The movie name must be in `"Title YYYY"` format.

```bash
popcorn-archives add "Casablanca 1942"
```

### Search for a Movie

```bash
popcorn-archives search "Casablanca"
```

### Get a Random Suggestion

```bash
popcorn-archives random
```

### List Movies by Year

```bash
popcorn-archives year 1942
```

### List Movies by Decade

```bash
popcorn-archives decade 1940
```

### Scan a Directory of Movies

If you have a folder `/path/to/movies` containing subfolders like `The Godfather 1972` and `Pulp Fiction 1994`:

```bash
popcorn-archives scan /path/to/movies
```

### Import from a CSV File

Create a `movies.csv` file with a single column `name`:

```csv
name
"The Shawshank Redemption 1994"
"Forrest Gump 1994"
```

Then run:

```bash
popcorn-archives import movies.csv
```