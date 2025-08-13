# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-14

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