# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-08-13

### Added
- New `delete` command to remove a specific movie from the archive.
- New `clear` command to permanently delete all movies from the archive, with a serious confirmation prompt.
- Progress bars (`tqdm`) for `scan` and `import` commands to provide better feedback on long-running operations.

### Changed
- The `scan` command now supports the `Movie Title (YYYY)` folder name format in addition to `Movie Title YYYY`.
- Improved user feedback for the `scan` command, showing counts for added and skipped (duplicate) movies, and a clear message on cancellation.
- The database is now stored in a standard, user-specific application data directory (e.g., `~/.local/share/PopcornArchives` on Linux) instead of the project folder. This makes the data persistent and independent of the project's location.

### Fixed
- Refactored database connection handling using `with` statements to prevent `database is locked` errors and ensure connections are always closed.
- Fixed a bug where the `data` directory was created in the current working directory instead of a consistent, appropriate location.

## [0.1.0] - YYYY-MM-DD

### Added
- Initial release of Popcorn Archives.
- Core features: `add`, `search`, `random`, `year`, and `decade` commands.
- Ability to import movies from a CSV file using the `import` command.
- Ability to scan a directory of movie folders using the `scan` command.
- Basic SQLite database for persistent storage.
- Project setup with `setup.py` for installation.