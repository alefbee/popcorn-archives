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

## Installation & Setup

Follow these steps to get Popcorn Archives running on your local machine.

**Prerequisites:** You need `git` and `python3` installed on your system.

**1. Clone the Repository**

First, clone the project from GitHub to your local machine:

```bash
git clone https://github.com/alefbee/popcorn-archives.git
```

**2. Navigate to the Project Directory**

```bash
cd popcorn-archives
```

**3. Create and Activate a Virtual Environment**

It's a best practice to create a virtual environment to keep project dependencies isolated. This prevents conflicts with other projects or system-wide Python packages.

```bash
# Create a virtual environment named .venv
python3 -m venv .venv
```

Now, activate it:

```bash
# For Linux and macOS
source .venv/bin/activate
```

> **Note for Windows users:** Use the following command in Command Prompt or PowerShell:
> ```powershell
> .\.venv\Scripts\Activate
> ```

After activation, you should see `(.venv)` at the beginning of your command prompt.

**4. Install the Project**

With the virtual environment active, install the project in editable mode (`-e`). This command reads the `setup.py` file, installs all required dependencies (like `Click`), and makes the `popcorn-archives` command available.

```bash
pip install -e .
```

**You're all set!** You can now run the application. To see all available commands, type:

```bash
popcorn-archives --help
```

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