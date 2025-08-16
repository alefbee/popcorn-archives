# Popcorn Archives 🍿

[![Run Python Tests](https://github.com/alefbee/popcorn-archives/actions/workflows/ci.yml/badge.svg)](https://github.com/alefbee/popcorn-archives/actions/workflows/ci.yml)

> **Note:** As of version 2.0.0, the command has been renamed from `popcorn-archives` to `poparch`!

A simple and powerful command-line tool to manage your personal movie watchlist, built with Python and Click.

## In Action: A Typical Workflow

Take a tour of a typical user session in this single demonstration. The animation showcases how several key commands work together to manage and explore your movie collection.

![Popcorn Archives Live Demo](assets/popcorn-archives2-demo.apng)

**In this demo, you can see the following sequence of actions:**

1.  **Populating the Archive (`scan` & `add`):** The session begins by using `poparch scan` to quickly import an entire directory of movie folders. A single movie is then added manually with `poparch add`.
2.  **Checking the Dashboard (`stats`):** Immediately after, the user runs `poparch stats` to see a beautiful, colorful dashboard summarizing the newly populated archive.
3.  **Enriching the Data (`update`):** With the movies added, the `poparch update` command is run. It automatically finds all movies with missing details and fetches their genre, plot, and rating information from the OMDb API.
4.  **Viewing Movie Details (`info`):** To see the newly fetched data, the user runs `poparch info` on a specific movie, displaying its detailed information card.
5.  **Getting a Recommendation (`random --unwatched`):** Finally, looking for a movie to watch, the user runs `poparch random --unwatched` to get a suggestion for a great film they haven't seen yet.
## Features

-   🌐 **Rich Movie Details**: Fetch detailed movie information—including genre, director, plot, and ratings—from **The Movie Database (TMDb)**.
-   📝 **Watched Status Tracking**: Keep track of which movies you've seen with the `watch` and `unwatch` commands. Get random suggestions just from your unwatched list!
-   🔄 **Bulk Updates**: Fetch details for your entire collection at once. The process is robust, provides detailed progress, and gives a final summary of successes and failures.
-   🏷️ **Interactive Genre Filtering**: Use the `genre` command without arguments to get a dynamic, numbered list of all genres in your archive to choose from.
-   ✅ **Flexible Movie Detection**: Intelligently scans your movie directories using common naming formats.
-   ✨ **Robust Error Handling**: Gracefully skips unparsable folders and handles network timeouts without crashing.

## Installation & Configuration

### Option 1: As a System-Wide Command (Recommended for Users)

If you just want to use the application, the best way is to install it with `pipx`. This installs the tool in an isolated environment but makes the command available everywhere in your system.

**1. Install `pipx`**
If you don't have it, install `pipx` using your system's package manager (e.g., `sudo apt install pipx`, `brew install pipx`). Then, ensure its path is configured:
```bash
pipx ensurepath
```
*(You may need to restart your terminal for this change to take effect.)*

**2. Install Popcorn Archives**
Clone the repository and install directly from the local path:
```bash
git clone https://github.com/alefbee/popcorn-archives.git
cd popcorn-archives
pipx install .```
The `poparch` command is now ready to use!

### Option 2: For Development

If you want to modify or contribute to the code, set it up in a local virtual environment.

**1. Clone the Repository**
```bash
git clone https://github.com/alefbee/popcorn-archives.git
cd popcorn-archives
```
**2. Create and Activate a Virtual Environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
**3. Install Dependencies and the Project**
Install all dependencies (including development tools like `pytest`) and the project in editable mode:
```bash
pip install -r requirements-dev.txt
pip install -e .
```

### Step 3: Configure Your API Key (Required for Movie Details)

To fetch movie details, you need a free API key from **The Movie Database (TMDb)**.

1.  **Get a free API key**:
    -   Sign up at [themoviedb.org](https://www.themoviedb.org/signup) and request a key from your account **Settings → API**.
2.  **Set the key in the app**:
    Run the `config` command once to save your key:
    ```bash
    poparch config --key YOUR_TMDB_API_KEY
    ```

## Updating

To update Popcorn Archives to the latest version, navigate to the project directory and run:

```bash
# Get the latest changes from GitHub
git pull origin main

# Re-install to apply updates
# If using pipx:
pipx install --force .

# If using a virtual environment:
pip install -e .
```

## Usage

Here is a summary of the available commands:

| Command | Description | Example |
| :--- | :--- | :--- |
| **Management** | | |
| `add` | Adds a new movie to the archive. | `poparch add "The Kid 1921"` |
| `scan` | Scans a directory for movie folders. | `poparch scan /path/to/movies` |
| `import` | Imports movies from a CSV file. | `poparch import movies.csv` |
| `export` | Exports the entire archive to a CSV. | `poparch export backup.csv` |
| `delete` | Deletes a specific movie. | `poparch delete "The Matrix 1999"` |
| `clear` | Clears the entire movie archive. | `poparch clear` |
| **Information & Details** | | |
| `info` | Fetches and displays details for a movie. | `poparch info "Pulp Fiction 1994"` |
| `search` | Searches for a movie by title. | `poparch search "Casablanca"` |
| `random` | Suggests a random movie. | `poparch random --unwatched` |
| `year` | Lists movies from a specific year. | `poparch year 1942` |
| `decade` | Lists movies from a specific decade. | `poparch decade 1940` |
| `genre` | Lists movies by genre (interactive menu). | `poparch genre` |
| `stats` | Displays archive statistics. | `poparch stats` |
| **Watched Status** | | |
| `watch` | Marks a movie as watched. | `poparch watch "The Matrix 1999"` |
| `unwatch` | Marks a movie as unwatched. | `poparch unwatch "The Matrix 1999"` |
| **Configuration & Maintenance** | | |
| `config` | Sets the TMDb API key. | `poparch config --key <your_key>` |
| `update` | Fetches missing details for all movies. | `poparch update` |
| `where` | Displays the location of the database. | `poparch where` |

## 🚀 Roadmap: Future Features

Popcorn Archives is actively being developed. Here's a look at some of the exciting features planned for future releases. Contributions are welcome!

### Core Enhancements
-   [ ] **Advanced Search & Filtering**:
    -   Implement a powerful `search` command that can filter by multiple criteria at once.
    -   Examples:
        -   `poparch search --actor "Tom Hanks"`
        -   `poparch search --director "Christopher Nolan"`
        -   `poparch search --keyword "time travel"`
        -   `poparch search --collection "The Matrix Collection"`
-   [ ] **Full Data Export/Import**:
    -   Add a `--full` flag to the `export` command to save all movie details (including genre, plot, cast, etc.) to the CSV.
    -   Make the `import` command smart enough to detect and import these full backups, skipping redundant API calls.

### New Commands & Features
-   [ ] **Smart Recommendations**:
    -   Create a new `poparch recommend <'Title YYYY'>` command that uses the TMDb API to suggest similar movies.
-   [ ] **Personal Ratings & Notes**:
    -   Add a `poparch rate <'Title YYYY'> <score>` command to allow users to add their personal ratings.
    -   Implement a `poparch note <'Title YYYY'>` command that opens the system's default text editor for writing personal notes.
-   [ ] **Playlists / Custom Lists**:
    -   Introduce a full-featured list management system (`list create`, `list add`, `list show`) to allow users to organize movies into custom collections like "Sci-Fi Classics" or "Oscar Winners".

### UI/UX Improvements
-   [ ] **Comprehensive Help Command**:
    -   Create a master `poparch help` command that displays a beautifully formatted guide with examples for all commands and their options.
-   [ ] **Configuration Improvements**:
    -   Merge the `where` command into `poparch config --show-path` for a more unified configuration experience.

## Testing & Quality Assurance

This project includes a comprehensive test suite built with `pytest`. To run the tests locally, set up the development environment, then run:
```bash
pytest
```
We also use **GitHub Actions** for Continuous Integration. Every push and pull request is automatically tested against multiple Python versions to ensure code quality and stability.

## Uninstalling

If you wish to completely remove Popcorn Archives and all its data, please follow these steps carefully.

**Step 1: Locate the Data Directory**
First, find out where your data is stored using the built-in `where` command:
```bash
poparch where
```
Copy or take note of the directory path shown.

**Step 2: Uninstall the Application**
-   **If you installed with `pipx`:** `pipx uninstall popcorn-archives`
-   **If you installed for development:** Simply delete the project folder.

**Step 3: Remove the User Data**
Using the path you found in Step 1, manually delete the application's data directory. **This action is irreversible.**

## About This Project

This project was developed as a personal learning journey to create a useful, real-world command-line application in Python. It was an opportunity to practice key software development concepts, including:

-   Building a robust CLI with `Click`.
-   Database management with `SQLite`.
-   Creating an installable package with `setuptools`.
-   Following best practices for project structure and documentation.
-   Implementing version control with Git and GitHub.

This project was built with significant assistance from AI tools like Google's Gemini.