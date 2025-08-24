# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.3.1] - 2025-08-24

### Fixed
- Resolved a critical startup crash (`FileNotFoundError`) that occurred when running the application in a clean environment for the first time (e.g., in CI/CD). The logging system is now initialized lazily, ensuring the necessary directories are created before any log files are accessed.

## [3.3.0] - 2025-08-24

### Added
- **Comprehensive Logging System**: A full-featured logging system has been introduced.
    - Major events (add, delete, update, scan, import) are now recorded to a log file.
    - Logging is disabled by default and can be controlled via `poparch config --logging on/off`.
    - New `poparch log` command group with `view` and `clear` subcommands to manage the log file.

### Changed
- **Unified `search` Command**: The `show` command (previously `year` and `decade`) has been merged into the `search` command. Users can now filter by `--year` and `--decade` directly within the powerful `search` interface for a more consistent experience.

### Removed
- The separate `year` and `decade` commands have been removed in favor of the new filter options in the `search` command.

## [3.2.2] - 2025-08-23

### Fixed
- **Database Cleanup**: Resolved a critical `UNIQUE constraint failed` error in the `cleanup_duplicates` function by correcting the order of DELETE and UPDATE operations. This ensures that the cleanup process is robust and safe.

### Removed
- **`--repair` Feature**: The experimental `--repair` option has been removed from the `update` command to simplify the application's focus and reduce complexity. The core logic for finding the best movie match in the API has been improved, making this feature redundant.

## [3.2.1] - 2025-08-23

### Fixed
- **Improved API Result Selection**: The API fetching logic now sorts online search results by `popularity`. This prevents issues where an incorrect or obscure movie (like a short film) was being selected, ensuring commands like `update --repair` and `info` now fetch the most relevant movie data.
- **Test Suite Stability**: Resolved multiple failures in the test suite related to interactive commands. The tests for `update --repair` and `update --cleanup` have been rewritten with more robust mocking for `inquirer`, ensuring the CI pipeline is stable and reliable.

## [3.2.0] - 2025-08-23

### Added
- **Database Cleanup & Repair**: The `update` command now includes `--cleanup` and `--repair` options to merge duplicates and interactively fix movies with suspicious data.

### Fixed
- A critical bug where `update` would not correctly save all fetched data due to a key mismatch.
- A logic error where the `update` command would fail to identify all movies with incomplete data.
- Multiple bugs related to testing interactive commands, API calls, and database operations.


## [3.1.0] - 2025-08-23

### Changed
- **License**: The project license has been changed from the permissive MIT License to the **GNU General Public License v3.0 (or later)**. This strong copyleft license was chosen to ensure that all derivative works of this project also remain free and open source, in line with the project's philosophy.

## [3.0.0] - 2025-08-23

### Added
- **Personal Ratings**: You can now rate your movies on a 1-10 scale using the new `rate` command. Your personal rating is displayed in the `info` command and your top-rated movie is featured in `stats`.
- **Letterboxd Import**: A powerful new feature to import your entire movie history, including watched status and ratings, from a Letterboxd ZIP export. The importer is interactive and gives you full control over which movies are added or updated.

### Changed
- **Database Schema**: The database has been updated to include a `user_rating` column to store personal ratings. The migration is handled automatically.
- **Dependencies**: Added the `inquirer` library to create beautiful and user-friendly interactive menus.

## [2.3.2] - 2025-08-23

### Changed
- **Redesigned `stats` Dashboard**: The `stats` command output has been completely redesigned for a cleaner, more professional, and more readable user experience. It now uses a minimal color palette, improved spacing, and better alignment to present the archive statistics and user taste profile in a beautiful dashboard format.

## [2.3.1] - 2025-08-18

### Fixed
- Improved the visual alignment in the `search` command's output. The separator line now has a fixed width that perfectly matches the content above it, providing a cleaner and more consistent look across different terminal sizes.

## [2.3.0] - 2025-08-18

### Added
- **Targeted `update` Command**: The `update` command now accepts an optional `FILEPATH` argument. This allows users to update only a specific list of movies (e.g., from a file of previously failed updates), providing much greater control over long-running operations.
- **Comprehensive User Manual (`USAGE.md`)**: A new, detailed `USAGE.md` file has been created to serve as a complete user guide with in-depth explanations and examples for all commands and features.

### Changed
- **Help System**: The manual `help` command has been removed in favor of `click`'s powerful, auto-generated help system. Docstrings for all commands have been enriched with examples to improve the output of `poparch <COMMAND> --help`.
- The main `poparch --help` output now links directly to the new online user manual.

## [2.2.0] - 2025-08-17

### Added
- **Advanced Search**: A powerful new `search` command that allows filtering by multiple criteria at once, including `--actor`, `--director`, `--keyword`, and `--collection`.
- **Rich Search Output**: The `search` command now displays results in a beautiful, easy-to-read "Info Card" format.

### Changed
- **Smart `info` Command**: The `info` command has been completely overhauled to be more user-friendly and intelligent.
    - It now handles partial movie titles without a year.
    - It searches the local archive first. If no matches are found, it automatically searches online.
    - It presents an interactive menu for ambiguous results (both locally and online).
    - It interactively asks for confirmation before adding a new movie found online.
- **Database Schema**: The database schema was updated to store a richer set of movie details, including `runtime`, `cast`, `keywords`, and `collection`.
- **API Core**: The API fetching logic was enhanced to retrieve the new, richer dataset from TMDb.

### Fixed
- **Critical Update Bug**: Fixed a bug where the `update` command would not correctly save all fetched data due to a key mismatch.
- **Robust Update Logic**: The `update` command is now smarter at finding movies with incomplete data, ensuring that legacy records are properly updated.
- **Search Input**: The `search` command now correctly handles queries with trailing whitespace.

## [2.1.3] - 2025-08-16

### Fixed
- The `update` command is now significantly more robust. It correctly identifies all movies with incomplete data, including those that were partially updated in previous versions or where the API did not return a complete dataset.


## [2.1.2] - 2025-08-16

### Fixed
- Corrected a critical bug in the `update_movie_details` function where data from the API was not being saved correctly due to a key mismatch. This ensures all fetched details are now properly stored in the database.

## [2.1.1] - 2025-08-16

### Fixed
- The `update` command now correctly identifies and fetches details for movies that were added with older versions of the application. It now uses a more reliable field (`runtime`) to detect movies with incomplete data.

## [2.1.0] - 2025-08-16

### Added
- **Rich Movie Data**: The application now fetches and stores a much richer set of movie details from TMDb, including:
    - Runtime
    - Top-billed cast members
    - Movie collection/franchise information
    - A direct link to the IMDb page (`imdb_id`)
    - *Note: Keywords are also fetched and stored for future use.*

### Changed
- **Smart `info` Command**: The `info` command has been completely overhauled to be more user-friendly and intelligent.
    - It now handles partial movie titles without a year.
    - It searches the local archive first. If no matches are found, it automatically searches online.
    - If multiple potential matches are found (either locally or online), it presents an interactive menu for the user to choose the correct movie.
    - When a movie is found online, it now interactively asks for confirmation before adding it to the local archive.
- **Database Schema**: The database schema has been significantly updated to support all the new data fields. A migration path is included to automatically and safely update existing users' databases upon first run.
- **API Core**: The API fetching logic in `core.py` was enhanced to retrieve the new, richer dataset in a single request

## [2.0.2] - 2025-08-15

### Added
- A `--version` option to the main command (`poparch --version`) to quickly display the installed version of the application.

### Changed
- Improved application startup time by implementing "lazy loading" for heavy modules like `requests`. This results in a much faster response for simple commands like `search` and `stats`.

### Fixed
- Corrected a minor inaccuracy in the documentation for the `config` command.

## [2.0.1] - 2025-08-15

### Fixed
- Fixed a crash (`sqlite3.OperationalError: duplicate column name`) that occurred on the first run of the application after a fresh installation. The database initialization logic is now fully idempotent, ensuring it handles both new installs and schema migrations without errors.

## [2.0.0] - 2025-08-15

### BREAKING CHANGES
- **Command Renamed**: The main command-line executable has been renamed from `popcorn-archives` to `poparch` for a shorter and more convenient user experience. Users upgrading from v1.x.x will need to update any scripts or aliases that used the old command.

### Added
- **Movie Details Integration**: Added a new `info` command to fetch and display rich movie details (genre, director, plot, rating) from **The Movie Database (TMDb)**.
- **Watched Status Tracking**: Added `watch` and `unwatch` commands to manage viewing status. The `random` command now supports an `--unwatched` flag.
- **Bulk Update**: A new `update` command allows users to fetch details for their entire collection in one go. It provides a progress bar with a dynamic description and a final summary report, even when interrupted.
- **Interactive Genre Filter**: The `genre` command now presents an interactive menu of available genres for easy filtering if no genre is specified.
- **API Key Configuration**: A `config` command was added to allow users to securely save their personal TMDb API key.

### Changed
- **API Interaction**: Switched from `tmdbv3api` library to direct `requests` calls for more robust control over network requests, including a 5-second timeout to prevent the application from hanging.
- **Stats Dashboard**: The `stats` command now includes a breakdown of watched vs. unwatched movies.
- **Database Schema**: The database schema has been updated to include new columns for storing movie details (`genre`, `director`, etc.) and watched status. A robust migration path is included for existing users.

### Fixed
- **Test Suite**: The entire test suite has been updated to mock `requests` directly, ensuring tests are accurate and independent of the old `tmdbv3api` library.

## [1.1.0] - 2025-08-14

### Added
- **Continuous Integration (CI)**: A GitHub Actions workflow has been set up to automatically run tests on every push and pull request to the `main` branch, ensuring code quality and stability across multiple Python versions (3.10, 3.11, 3.12).
- **Automated Tests**: Introduced a test suite using `pytest` with initial unit tests for the core movie title parsing logic.
- **Build Status Badge**: A "Build Status" badge has been added to the `README.md` for immediate visual feedback on the health of the project.

## [1.0.1] - 2025-08-14

### Added
- A new `where` utility command to display the exact location of the application's database file, which helps with debugging and manual access.

## [1.0.0] - 2025-08-13

This marks the first stable, public release of Popcorn Archives. The project is now considered feature-complete, stable, and ready for general use.

### Added

-   **Stats Dashboard**: A visually appealing `stats` command that displays a summary of the archive, including total count, time span, and oldest/newest movies.
-   **Export to CSV**: An `export` command to save the entire movie collection to a user-specified CSV file.
-   **Full Data Management**: `delete` and `clear` commands to manage the archive, complete with interactive safety confirmations.
-   **Robust Scanning**: The `scan` command now intelligently handles various folder name formats and gracefully skips unparsable folders, reporting them as warnings instead of crashing.
-   **User Feedback**: Progress bars (`tqdm`) have been integrated into all long-running operations.
-   **Comprehensive Documentation**: A detailed `README.md` with installation guides, a command reference table, screenshots, and guides for updating and uninstalling.
-   **Utility Commands**: A `where` command to easily locate the application's database file.

### Changed

-   **Stats Dashboard UI**: The decade distribution chart now features a dynamic color palette and perfect alignment for a clean, professional look in the terminal.
-   **Database Location**: The database is now stored in a standard, OS-specific user data directory, making it persistent and robust.
-   **Movie Title Parsing**: The parser is now more flexible, supporting both `Title YYYY` and `Title (YYYY)` formats and correctly ignoring extra metadata.

### Fixed

-   Resolved `TypeError` in `year` and `decade` commands by aligning function parameter names.
-   Prevented `database is locked` errors by refactoring all database connections to use context managers (`with` statements).
-   Fixed `UnicodeDecodeError` for systems with non-UTF-8 locales by safely encoding all terminal output.

## [0.1.0] - 2025-08-13

### Added

-   Initial development release with core features (`add`, `search`, `random`, `year`, `decade`, `import`, `scan`).