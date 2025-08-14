# Popcorn Archives 🍿

[![Run Python Tests](https://github.com/alefbee/popcorn-archives/actions/workflows/ci.yml/badge.svg)](https://github.com/alefbee/popcorn-archives/actions/workflows/ci.yml)


A simple and powerful command-line tool to manage your personal movie watchlist, built with Python and Click.

## In Action: A Typical Workflow

Take a tour of a typical user session in this single demonstration. The animation showcases some of the most common commands you'll use with Popcorn Archives.

![Popcorn Archives Live Demo](popcorn-archives-demo.apng)

**In this demo, you can see the following sequence of actions:**

1.  **Viewing the Dashboard:** The session starts by running `popcorn-archives stats` to get a quick, colorful overview of the current movie collection.
2.  **Scanning a New Folder:** Next, `popcorn-archives scan` is used on a directory. Notice how the app reports unparsable folders as warnings and then adds the valid movies to the archive.
3.  **Getting a Random Suggestion:** For a movie night recommendation, the `popcorn-archives random` command instantly provides a suggestion from the updated collection.
4.  **Exporting for Backup:** Finally, the entire archive is safely exported to a CSV file for backup using the `popcorn-archives export` command.

## Features

-   ✅ **Flexible Movie Detection**: Intelligently scans your movie directories using two common naming formats: `Movie Title YYYY` and `Movie Title (YYYY)`.
-   ✨ **Robust Error Handling**: Gracefully skips folders it cannot parse and provides a clear warning list, instead of crashing.
-   📥 **Bulk Import & Export**: Easily import your existing collection from a CSV file, or export your entire archive for backup and sharing.
-   📊 **Archive Statistics**: Use the `stats` command for a quick overview, including total movie count, oldest/newest movies, and the most populated decade.
-   🔎 **Powerful Search & Filtering**: Instantly search for any movie in your archive, or filter your collection by a specific year or decade.
-   🗑️ **Full Data Management**: Add, delete individual movies, or clear the entire archive with interactive, safety-first confirmation prompts.
-   ⚙️ **Persistent & Safe Storage**: Uses a local SQLite database stored in a standard user data directory, ensuring your archive is safe even if you move or delete the project folder.

## Installation

There are two ways to install Popcorn Archives, depending on your goal.

### Option 1: As a System-Wide Command (Recommended for Users)

If you just want to use the application, the best way is to install it with `pipx`. This installs the tool in an isolated environment but makes the command available everywhere in your system.

**1. Install pipx**
If you don't have `pipx`, install it using your system's package manager (e.g., `sudo apt install pipx`, `brew install pipx`). Then, ensure its path is configured:
```bash
pipx ensurepath
```

**2. Install Popcorn Archives**
Clone the repository and install directly from the local path using `pipx`:
```bash
git clone https://github.com/alefbee/popcorn-archives.git
cd popcorn-archives
pipx install .```
The `popcorn-archives` command is now ready to use from any terminal!

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

**3. Install in Editable Mode**
This installs the project and its dependencies, allowing your code changes to be reflected immediately.
```bash
pip install -e .
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

Here are the available commands:

| Command | Description | Example |
| :--- | :--- | :--- |
| `add` | Adds a new movie to the archive. | `popcorn-archives add "The Kid 1921"` |
| `scan` | Scans a directory for movie folders. | `popcorn-archives scan /path/to/movies` |
| `import` | Imports movies from a CSV file. | `popcorn-archives import movies.csv` |
| `export` | Exports the entire archive to a CSV. | `popcorn-archives export backup.csv` |
| `search` | Searches for a movie by title. | `popcorn-archives search "Casablanca"` |
| `random` | Suggests a random movie. | `popcorn-archives random` |
| `year` | Lists movies from a specific year. | `popcorn-archives year 1942` |
| `decade` | Lists movies from a specific decade. | `popcorn-archives decade 1940` |
| `stats` | Displays archive statistics. | `popcorn-archives stats` |
| `delete` | Deletes a specific movie. | `popcorn-archives delete "The Matrix 1999"` |
| `clear` | Clears the entire movie archive. | `popcorn-archives clear` |
| `where` | Displays the location of the database. | `popcorn-archives where` |

## Uninstalling

If you wish to completely remove Popcorn Archives and all its data from your system, please follow these steps carefully in order.

**Step 1: Locate the Data Directory (Important!)**

First, before uninstalling the application, you must find out where it stores your data. The easiest way to do this is with the built-in `where` command.

Run the following in your terminal:
```bash
popcorn-archives where
```

The output will show you the exact path to the database. For example:
```
The database file is located at:
/home/alef/.config/popcornarchives/movies.db
```
**Copy or take note of the directory path** (e.g., `/home/alef/.config/popcornarchives`). You will need this path in Step 3.

**Step 2: Uninstall the Application**

Now you can remove the command-line tool itself.

-   **If you installed with `pipx`:**
    ```bash
    pipx uninstall popcorn-archives
    ```
-   **If you installed for development (with `pip`):**
    Simply delete the project folder. If you created a virtual environment inside it, that will be removed as well.

**Step 3: Remove the User Data and Database**

This is the final step and will delete your movie database. **This action is irreversible.**

Using the path you found in **Step 1**, manually delete the application's data directory.

-   **On Linux and macOS:**
    Use the `rm -rf` command with the path you noted. For example, if the path was `/home/alef/.config/popcornarchives`, the command would be:
    ```bash
    rm -rf /home/alef/.config/popcornarchives
    ```

-   **On Windows:**
    Open File Explorer. Paste the full directory path you found in Step 1 into the address bar and press Enter. Then, delete the contents of that folder.

## About This Project

This project was developed as a personal learning journey to create a useful, real-world command-line application in Python. It was an opportunity to practice key software development concepts, including:

-   Building a robust CLI with `Click`.
-   Database management with `SQLite`.
-   Creating an installable package with `setuptools`.
-   Following best practices for project structure and documentation.
-   Implementing version control with Git and GitHub.

This project was built with significant assistance from AI tools like Google's Gemini.