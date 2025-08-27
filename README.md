# Popcorn Archives 🍿

[![Run Python Tests](https://github.com/alefbee/popcorn-archives/actions/workflows/ci.yml/badge.svg)](https://github.com/alefbee/popcorn-archives/actions/workflows/ci.yml)
[![GitHub License](https://img.shields.io/github/license/alefbee/popcorn-archives)](https://github.com/alefbee/popcorn-archives/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Note:** As of version 2.0.0, the command has been renamed from `popcorn-archives` to `poparch`!

A simple and powerful command-line tool to manage your personal movie watchlist, built with Python and Click.

## Why Popcorn Archives?

As a movie enthusiast, I found myself with a large personal archive and a growing problem: managing it all in a spreadsheet was becoming slow and cumbersome.

I wanted a simple, fast, and powerful command-line tool to quickly search which movies I already own and which ones I don’t, with all the rich details available at my fingertips. I couldn't find exactly what I was looking for, so I decided to build it.

This project is the result: a personal movie archive manager built for speed and simplicity. I'm sharing it in the hope that it helps other movie lovers too.

## In Action: A Typical Workflow

Take a tour of a typical user session in this single demonstration. The animation showcases a common workflow, from populating your archive to managing and exploring your personal movie collection.

![Popcorn Archives Live Demo](assets/popcorn-archives-v3.1-demo.apng)

**In this demo, you can see the following sequence of actions:**

1.  **Building the Archive (`scan` & `add`):**
    The session begins by populating the archive. First, `poparch scan` quickly imports an entire directory of local movie folders. Immediately after, a single movie is added manually with `poparch add "The Matrix 1999"`.

2.  **Enriching the Data (`update`):**
    With movies now in the database, `poparch update` is run. The tool finds all movies with incomplete information and automatically fetches their rich metadata (genre, cast, director, etc.) from TMDb.

3.  **Getting Insights (`stats`):**
    After the update, the user runs `poparch stats` to see the beautiful, personalized dashboard. This provides an instant overview of the collection and reveals interesting patterns about their movie taste.

4.  **Managing a Specific Movie (`watch` & `rate`):**
    The user then manages the movie added earlier, marking it as seen with `poparch watch "The Matrix 1999"` and giving it a perfect 10-star personal rating using `poparch rate "The Matrix 1999" 10`.

5.  **Viewing the Final Result (`info`):**
    Finally, `poparch info "The Matrix 1999"` is used to view the complete details for that movie. The output now shows the fully enriched data from the API, as well as the user's personal rating and watched status, all in one clean card.

> **Tech Note:** The animation above is a high-quality **APNG** (Animated PNG), not a GIF. This modern format is supported by GitHub and allows for perfect color reproduction and better compression.

## Features

### 🗂️ Collection Management
-   **Flexible Importing**: Seamlessly build your collection by **scanning** directories of movie folders, **importing** from standard CSV files, or migrating your entire history from a **Letterboxd** ZIP export.
-   **Personal Ratings & Watched Status**: Keep track of what you've seen with `watch`/`unwatch` and rate movies on a 1-10 scale with the `rate` command. Your Letterboxd ratings are imported automatically!
-   **Keep Your Archive Rich**: Use the `update` command to fetch rich metadata for your entire collection at once. The process is robust and provides a detailed summary of successes and failures.

### 🔎 Discovery & Exploration
-   **Smart & Interactive Info**: The powerful `info` command acts as your gateway to movie knowledge. It intelligently finds movies both locally and online, with interactive menus for ambiguous queries.
-   **Advanced Search & Filtering**: Instantly search your local archive with a rich `search` command that can filter by title, `--actor`, `--director`, `--keyword`, `--year`, `--decade` and `--collection`.
-   **Personalized Stats Dashboard**: Uncover insights into your collection and personal taste with the beautiful `stats` dashboard, which analyzes your top genres, favorite directors, and more.
-   **Interactive Genre Filtering**: Use the `genre` command without arguments to get a dynamic, numbered list of all genres in your archive to choose from.

### 🔧 Under the Hood
-   **Rich Movie Details**: Fetches comprehensive movie information—including cast, runtime, collection, and IMDb links—from TMDb and caches it locally.
-   **Robust & User-Friendly**: The application is designed to be resilient. It gracefully handles errors (like unparsable folder names) and provides clear, helpful feedback.
-   **Persistent & Safe Storage**: Uses a standard user data directory for its SQLite database, ensuring your archive is safe and independent of the project folder.

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

For a quick reference, see the table below. For a complete guide with detailed examples for all commands, please see the **[Full Usage Manual](USAGE.md)**.

Here is a summary of the available commands:

| Command | Description | Example |
| :--- | :--- | :--- |
| **Management** | | |
| `add` | Adds a new movie to the archive. | `poparch add "The Kid 1921"` |
| `scan` | Scans a directory for movie folders. | `poparch scan /path/to/movies` |
| `import`| Imports movies from a CSV file. | `poparch import movies.csv` |
| `export`| Exports the archive to a CSV. | `poparch export backup.csv` |
| `delete`| Deletes a specific movie. | `poparch delete "The Matrix 1999"` |
| `clear` | Clears the entire movie archive. | `poparch clear` |
| `rate` | Rates a movie in your archive | `poparch rate "The Matrix 1999" 10` |
| **Information & Search** | | |
| `info` | Smartly finds a movie locally or online. | `poparch info "Pulp Fiction"` |
| `search`| Advanced search with filters. | `poparch search -d "Nolan"` |
| `random`| Suggests a random movie. | `poparch random --unwatched` |
| `genre` | Lists movies by genre (interactive). | `poparch genre` |
| `stats` | Displays archive statistics. | `poparch stats` |
| **Watched Status** | | |
| `watch` | Marks a movie as watched. | `poparch watch "The Matrix 1999"` |
| `unwatch`| Marks a movie as unwatched. | `poparch unwatch "The Matrix 1999"` |
| **Configuration & Maintenance** | | |
| `config`| Sets the TMDb API key. | `poparch config --key <your_key>` |
| `update`| Fetches missing details for all movies. | `poparch update --force` |
| `log` | Interact with the log file. | `poparch log view` |

## 🚀 Roadmap: Future Features

Popcorn Archives is actively being developed. Here's a look at some of the exciting features planned for future releases. Contributions are welcome!

### Core Enhancements & Power Features
-   [x] **Advanced Search & Filtering**:
    -   Implement a powerful `search` command that can filter by multiple criteria at once (e.g., by actor, director, keyword).
-   [x] **Personalized Stats Dashboard**:
    -   Enhance the `stats` command to provide insights into the user's movie taste, such as top favorite genres and most frequent topics (by processing keywords).
-   [ ] **JSON Output for Scripting**:
    -   Add a `--json` flag to commands like `info`, `search`, and `stats` to output data in a machine-readable JSON format, allowing `poparch` to be used in scripts.
-   [ ] **Advanced Configuration**:
    -   Expand the `config` command to allow users to customize aspects of the application, such as default output formats or color schemes.
-   [ ] **Combined Filtering**:
    -   Allow combining multiple filters in the `search` command for even more powerful queries.
    -   Example: `poparch search --decade 1990 --genre "Action"`

### New Commands & Features
-   [ ] **Smart Recommendations**:
    -   Create a new `poparch recommend <'Title YYYY'>` command that uses the TMDb API to suggest similar movies.
-   [x] **Personal Ratings**:
    -   Add a `poparch rate <'Title YYYY'> <score>` command to allow users to add their personal ratings.
-   [ ] **Personal Notes**:
    -   Implement a `poparch note <'Title YYYY'>` command that opens the system's default text editor for writing personal notes.
-   [ ] **Playlists / Custom Lists**:
    -   Introduce a full-featured list management system (`list create`, `list add`, `list show`) to organize movies into custom collections.
-   [x] **Import from Letterboxd**:
    -   Add a powerful importer to read a user's exported CSV from **Letterboxd**, including their ratings and watched status.
-   [ ] **Smart Add from Filename**:
    -   Create a command like `poparch add --from-file <path/to/movie.mkv>` that intelligently parses the movie title from a filename and adds it to the archive.
-   [ ] **TV Show Support**:
    -   Expand the application's scope to include tracking and managing TV series in addition to movies.

### UI/UX Improvements
-   [ ] **Shell Completion**:
    -   Implement shell completion for commands and options (e.g., `poparch s<TAB>`), making the tool faster to use for power users.
-   [ ] **Full Data Export/Import**:
    -   Add a `--full` flag to the `export` command to save all movie details.
    -   Make the `import` command smart enough to detect and import these full backups.

### 🌱 Project & Community
-   [ ] **Advanced Documentation**:
    -   Create a full documentation website using GitHub Pages and a tool like MkDocs or Sphinx.
    -   Build out the GitHub Wiki with more in-depth guides.
-   [x] **Contribution Guide**:
    -   Create a `CONTRIBUTING.md` file to explain how other developers can contribute to the project, report bugs, and suggest features.
-   [ ] **Publish to PyPI**:
    -   The final step: publish the project to the official Python Package Index (PyPI) so users worldwide can install it simply with `pip install popcorn-archives`.

## Testing & Quality Assurance

This project includes a comprehensive test suite built with `pytest`. To run the tests locally, set up the development environment, then run:
```bash
pytest
```
We also use **GitHub Actions** for Continuous Integration. Every push and pull request is automatically tested against multiple Python versions to ensure code quality and stability.

## Uninstalling

If you wish to completely remove Popcorn Archives and all its data, please follow these steps carefully.

**Step 1: Locate the Data Directory**
First, find out where your data is stored using the built-in `config` command:
```bash
poparch config --show-paths
```
Copy or take note of the directory path shown.

**Step 2: Uninstall the Application**
-   **If you installed with `pipx`:** `pipx uninstall popcorn-archives`
-   **If you installed for development:** Simply delete the project folder.

**Step 3: Remove the User Data**
Using the path you found in Step 1, manually delete the application's data directory. **This action is irreversible.**

## 🤝 Contributing

Contributions are the lifeblood of open source, and any help you can provide is **greatly appreciated**. This project is intended to be a safe, welcoming space for collaboration, and all contributors are expected to adhere to our **[Code of Conduct](CODE_OF_CONDUCT.md)**.

There are many ways to contribute, from reporting bugs to writing code.

### How You Can Help
-   **🐛 Found a bug?** Please open a [new issue](https://github.com/alefbee/popcorn-archives/issues/new/choose) using the "Bug Report" template.
-   **🚀 Have a feature idea?** We'd love to hear it! Please open a [new issue](https://github.com/alefbee/popcorn-archives/issues/new/choose) using the "Feature Request" template.
-   **💻 Want to write code?** That's fantastic! Please read our **[Contributing Guide](CONTRIBUTING.md)** to learn how to set up your development environment, run tests, and submit a pull request.

*(Don't forget to give the project a star ⭐ if you find it useful! Thank you!)*

## About This Project

`poparch` began as a personal solution to a common problem for movie lovers: how to effectively manage a large, personal film archive beyond a simple spreadsheet. It has since evolved into a powerful, feature-rich command-line tool built on a clear and robust architectural philosophy.

### Core Philosophy: API as the Single Source of Truth

The central design principle of `poparch` is to treat **The Movie Database (TMDb) as the single source of truth** for movie metadata. Unlike other tools that might rely on potentially inconsistent local filenames, `poparch` uses the API to fetch the **canonical title, year, and details** for any movie before adding it to the local archive. This ensures the user's database is always clean, consistent, and accurate.

This "API-first" approach solves common problems like:
-   Minor differences in titles (e.g., `"Mission Impossible"` vs. `"Mission: Impossible"`).
-   Incorrect year information from filenames.
-   Inconsistent capitalization.

### Technical Architecture

The project is built on a clean, multi-layered architecture based on the **Separation of Concerns** principle. This makes the codebase maintainable, testable, and easy to extend.

-   **CLI Layer (`cli.py`):** The user-facing layer, built with **Click** and **Inquirer**. It is responsible for parsing commands and displaying data, but contains no business logic.
-   **Core Logic Layer (`core.py`):** The "brain" of the application. It handles all interactions with the external TMDb API, processes user queries, and formats data. It knows nothing about the database or the UI.
-   **Data Access Layer (`database.py`):** The only part of the application that communicates with the **SQLite** database. It abstracts all SQL queries into simple Python functions.
-   **Configuration & Logging (`config.py`, `logger.py`):** These modules handle cross-cutting concerns like managing the API key and recording application events.

### A Modern Development Showcase

This project also serves as a showcase for modern software development best practices:
-   **Automated Testing & CI/CD:** A comprehensive test suite using **pytest** and **pytest-mock** ensures code reliability. This suite is run automatically on every push via a **GitHub Actions** workflow.
-   **Community Ready:** With a full `USAGE.md` manual, `CONTRIBUTING.md` guide, and Issue/PR templates, the project is structured to welcome collaboration.
-   **AI-Assisted Development:** This project was built with significant assistance from AI tools, demonstrating a modern workflow that combines human-driven architectural decisions with AI-powered acceleration for implementation and debugging.