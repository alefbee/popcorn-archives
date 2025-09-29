# 🍿 Poparch: Full Usage Manual & Guide

Welcome to the comprehensive user guide for Popcorn Archives (`poparch`). This document provides detailed explanations and examples for every command and feature.

## Table of Contents
1.  [Core Concepts](#core-concepts)
2.  [Configuration](#configuration)
3.  [Finding & Viewing Movies](#finding--viewing-movies)
4.  [Managing Your Archive](#managing-your-archive)
5.  [Maintenance & Bulk Operations (Scan, Import, Export)](#maintenance--bulk-operations)
6.  [Tracking Watched Status](#tracking-watched-status)
7.  [Managing Your Watchlist](#managing-your-watchlist)  
8.  [Logging](#logging)
9.  [Power User Features](#power-user-features)

---

## Core Concepts

### The Local Archive vs. Online Search
`poparch` works with two sources of information:
-   **Your Local Archive:** A personal database on your computer where you store movies that you own or want to watch. Commands like `add`, `scan`, and `search` work with this local archive.
-   **Online Search (TMDb):** When you need information about a movie you *don't* have, `poparch` can look it up online using The Movie Database (TMDb). The `info` command is the primary way to do this.

### Movie Name Format
Most commands expect a movie name in the format `"Title YYYY"` or `"Title (YYYY)"`. This helps the application to be precise. The `info` and `search` commands are smarter and can also handle partial names.

---

## Configuration

### `config`
This command manages your application settings.

-   **Setting your API Key (Required for online features):**
    To use commands that fetch data from the internet (`info`, `update`), you need a free API key from TMDb.
    ```bash
    # Get your key from themoviedb.org, then save it:
    poparch config --key YOUR_TMDB_API_KEY
    ```
-   **Enabling/Disabling Logging:**
    Logging is disabled by default. You must enable it to start recording events.
    ```bash
    # To enable logging
    poparch config --logging on

    # To disable logging
    poparch config --logging off
    ```
-   **Finding Your Data Paths:**
    To see the exact location of your configuration, database, and log files:
    ```bash
    poparch config --show-paths
    ```

---

## Finding & Viewing Movies

### `info <query>`
This is the most powerful command for discovery. It intelligently finds a movie and displays its rich details.

-   **Workflow:**
    1.  It first searches your local archive.
    2.  If it finds one or more matches, it will display the result(s) or ask you to choose from a menu.
    3.  If it finds **no** local matches, it automatically searches online.
    4.  If an online result is found, it will display the details and **ask for confirmation** before adding it to your archive.

-   **Examples:**
    ```bash
    # Look up a movie with its full name (precise)
    poparch info "Pulp Fiction 1994"

    # Find a movie with a partial name (may trigger an interactive menu)
    poparch info "Terminator"
    ```

### `search [TITLE] [OPTIONS...]`
Performs an advanced, filtered search of your **local archive only**. This is the most powerful way to query and explore your existing collection. You can search by a partial movie `TITLE` and/or **combine multiple filters**.

-   **Interactive Mode:** If you run `poparch search` without any arguments or options, it will launch an **interactive menu** of all genres in your database, allowing you to easily browse your collection.

-   **Available Filters:**
    -   `--actor, -a <name>`
    -   `--director, -d <name>`
    -   `--writer, -w <name>`
    -   `--company, -p <name>` (production company)
    -   `--dop <name>` (director of photography)
    -   `--keyword, -k <word>`
    -   `--collection, -c <name>`
    -   `--genre, -g <name>`
    -   `--year, -y <yyyy>`
    -   `--decade, -D <yyyy>` (e.g., 1990)

-   **Examples:**
    ```bash
    # Launch the interactive genre finder
    poparch search

    # Find all movies directed by Christopher Nolan from the 2010s
    poparch search -d "Nolan" -D 2010

    # Find all Action movies starring Tom Cruise
    poparch search --genre "Action" -a "Tom Cruise"
    
    # Intelligently find movies from a specific year from the query
    poparch search "The Matrix 1999"
    ```

## Managing Your Archive

### `add <'Title YYYY'>`
Manually adds a new movie to your archive. This is the quickest way to add a movie if you know its exact title and year.
-   **Example:** `poparch add "The Kid 1921"`

### `delete <'Title YYYY'>`
Removes a specific movie from your archive after asking for confirmation.
-   **Example:** `poparch delete "The Matrix 1999"`

### `clear`
**Danger!** Permanently deletes **ALL** movies from your archive. It requires double confirmation for safety.
-   **Example:** `poparch clear`

---

## Rating Your Movies

### `rate <'Title YYYY'> <rating>`
Rates a movie in your archive on a scale from 1 to 10. This helps you keep track of your favorites.
-   **Example:** `poparch rate "The Matrix 1999" 10`

Your personal rating will be displayed with stars (⭐) in the `info` command's output.

---

## Maintenance & Bulk Operations

### `scan <path>`
Scans a directory and finds all sub-folders that match a valid movie name format (`Title YYYY` or `Title (YYYY)`). It will then ask for confirmation before adding them to your archive.
-   **Example:** `poparch scan /path/to/my/movies`

### `import <filepath> [--letterboxd]`
Adds movies in bulk. This command supports two modes:

-   **Standard CSV Import:**
    By default, it imports from a simple CSV file with a `name` header.
    -   **Example:** `poparch import movies_to_add.csv`

-   **Standard Excel Import:**
    By default, it imports from a simple Excel file.
    -   **Example:** `poparch import my_movies.xlsx`

-   **Letterboxd ZIP Import:**
    Use the `--letterboxd` flag to import your entire history from a Letterboxd data export ZIP file. This will import your movies, watched status, and personal ratings. The process is fully interactive.
    -   **Example:** `poparch import --letterboxd letterboxd-export.zip`

### `export <file.csv>`
Exports your entire movie archive to a CSV file, which is useful for backups.
-   **Example:** `poparch export my_collection_backup.csv`

### `update [FILEPATH] [--force]`
Fetches missing details for movies in your archive from TMDb. This command has three distinct modes of operation.

-   **Default Mode (Most Common):**
    When run without any arguments, it smartly finds only the movies with incomplete data and fetches their details.
    ```bash
    poparch update
    ```

-   **Targeted Mode (For Retrying Failures):**
    You can provide a path to a text file. The command will then **only** update the movies listed in that file (one `'Title (YYYY)'` per line). This is perfect for retrying a list of movies that failed in a previous bulk update.
    ```bash
    # First, create a file named 'failed.txt' with the movie names
    poparch update failed.txt
    ```

-   **Cleanup Mode:** Find and merge duplicate or similar entries before updating.
    `poparch update --cleanup`

-   **Force Mode (For Refreshing All Data):**
    The `--force` flag tells the application to re-fetch details for **every single movie** in your archive, overwriting any existing data. This is useful for refreshing your entire collection with the latest information.
    ```bash
    poparch update --force
    ```

> **Note on Priority:** The command prioritizes the modes in this order: **Targeted > Force > Default**. For example, if you run `poparch update --force failed.txt`, the command will only update the movies in `failed.txt` and the `--force` flag will be ignored
---

## Tracking Watched Status

### `watch <'Title YYYY'>` & `unwatch <'Title YYYY'>`
These commands allow you to toggle the "watched" status of a movie.
-   **Example:** `poparch watch "The Matrix 1999"`
-   **Example:** `poparch unwatch "The Matrix 1999"`

### `random [--unwatched]`
Suggests a random movie from your archive.
-   Use the `--unwatched` flag to get a suggestion for a movie you haven't seen yet.
-   **Example:** `poparch random --unwatched`

## Managing Your Watchlist

The `watchlist` command group helps you manage a simple, separate list of movies you intend to watch or download, without cluttering your main archive.

### `watchlist`
When run with no options, it displays all titles currently on your watchlist.
```bash
poparch watchlist
```

### `watchlist --add <"Title">`
Adds a new title to your watchlist. The title can be anything you want.
```bash
poparch watchlist --add "The new movie everyone is talking about"
poparch watchlist --add "Dune Part Two"
```

### `watchlist --delete <"Title">`
Removes a title from your watchlist. The match is case-insensitive.
```bash
poparch watchlist --delete "dune part two"
```

## Logging

`poparch` can keep a detailed log of all major operations. Logging is **disabled by default**.

### `log`
This command group provides tools for interacting with the log file.

-   **View Recent Logs:**
    See the last 20 entries in the log file.
    ```bash
    poparch log view
    ```
-   **Clear All Logs:**
    Permanently erases all content from the log file.
    ```bash
    poparch log clear
    ```

### Enabling Logging
You must enable logging via the `config` command to start recording events.
-   **Example:**
    ```bash
    poparch config --logging on
    ```

## Power User Features

### Shell Completion
`poparch` supports shell completion for commands and options, which makes using it much faster. To enable it, you need to add a line to your shell's configuration file. This only needs to be done once.

**For Bash:**
Add the following line to your `~/.bashrc` file:
```bash
eval "$(_POPARCH_COMPLETE=bash_source poparch)"
```

**For Zsh:**
Add the following line to your `~/.zshrc` file:
```bash
eval "$(_POPARCH_COMPLETE=zsh_source poparch)"
```

**For Fish:**
Run the following command once in your terminal:
```fish
_POPARCH_COMPLETE=fish_source poparch > ~/.config/fish/completions/poparch.fish
```

After updating your config file, restart your shell for the changes to take effect. You can now type `poparch w` and press `<TAB>` to see it auto-complete to `poparch watch`.