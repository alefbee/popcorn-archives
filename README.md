### README.md
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

There are two ways to install Popcorn Archives, depending on your goal.

### Option 1: As a System-Wide Command (Recommended for Users)

If you just want to use the application, the best way is to install it with `pipx`. This installs the tool in an isolated environment but makes the command available everywhere in your system, without needing to activate a virtual environment.

**1. Install pipx**
If you don't have `pipx`, install it using your system's package manager. For example:
-   **On Debian/Ubuntu:** `sudo apt install pipx`
-   **On Fedora/CentOS:** `sudo dnf install python3-pipx`
-   **On macOS:** `brew install pipx`

After installing, ensure its path is configured by running:
```bash
pipx ensurepath
```
*(You may need to restart your terminal for the changes to take effect.)*

**2. Install Popcorn Archives**
Clone the repository and install directly from the local path using `pipx`:

```bash
git clone https://github.com/alefbee/popcorn-archives.git
cd popcorn-archives
pipx install .
```

The `popcorn-archives` command is now ready to use from any terminal!

### Option 2: For Development

If you want to modify or contribute to the code, you should set it up in a local virtual environment.

**1. Clone the Repository**
```bash
git clone https://github.com/alefbee/popcorn-archives.git
cd popcorn-archives
```

**2. Create and Activate a Virtual Environment**
```bash
# Create a virtual environment named .venv
python3 -m venv .venv

# Activate it (on Linux/macOS)
source .venv/bin/activate
```
> **Note for Windows users:** Use `.venv\Scripts\Activate` in PowerShell.

**3. Install in Editable Mode**
This installs the project and its dependencies. The `-e` flag allows your code changes to be reflected immediately without reinstalling.
```bash
pip install -e .
```
Now you can run the application using the `popcorn-archives` command from within the activated environment.

## Updating

To update Popcorn Archives to the latest version, navigate to the cloned project directory and run the following commands:

```bash
# Get the latest changes from GitHub
git pull origin main

# Re-install the package to apply the updates
# If you installed with pipx:
pipx install --force .

# If you installed for development:
pip install -e .
```

## Usage

The application is straightforward to use. Here are the available commands:

### Add a Movie

The movie name must be in `"Title YYYY"` format.

```bash
popcorn-archives add "Casablanca 1942"
```

### View Archive Statistics

Get a quick overview of your movie collection, including total counts and other interesting facts.

```bash
popcorn-archives stats
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

Automatically finds movies in a directory. It supports two common folder naming formats: `Movie Title YYYY` and `Movie Title (YYYY)`.

```bash
# Example: Scanning a folder containing "The Godfather (1972)" and "Pulp Fiction 1994"
popcorn-archives scan /path/to/your/movies
```

### Import from a CSV File

Create a `movies.csv` file with a `name` header:

```csv
name
The Shawshank Redemption 1994
Forrest Gump 1994
```

Then run:

```bash
popcorn-archives import movies.csv
```

### Export to CSV

Save your entire archive to a CSV file. This is useful for creating backups or sharing your list with others. The output file will be compatible with the `import` command.

```bash
popcorn-archives export my_movies_backup.csv
```

### Delete a Movie

Removes a specific movie from the archive. It will ask for confirmation before deleting.

```bash
popcorn-archives delete "The Matrix 1999"
```

### Clear the Entire Archive

Permanently deletes **all** movies from your archive. This command requires double confirmation for safety.

```bash
popcorn-archives clear
```