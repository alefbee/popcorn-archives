# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.2] - 2025-08-14

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