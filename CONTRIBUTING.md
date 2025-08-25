# Contributing to Popcorn Archives

Thank you for your interest in contributing to Popcorn Archives! We welcome contributions from everyone. By participating in this project, you agree to abide by our code of conduct.

## How to Contribute
There are several ways you can contribute:
-   **Reporting Bugs:** If you find a bug, please open an issue and provide as much detail as possible, including steps to reproduce it.
-   **Suggesting Features:** Have a great idea? Open an issue and describe your feature suggestion.
-   **Submitting Pull Requests:** If you want to fix a bug or implement a new feature, you can submit a pull request.

## Setting Up a Development Environment
To get started with development, follow these steps:

1.  **Fork & Clone:** Fork the repository on GitHub and then clone your fork locally.
    ```bash
    git clone https://github.com/alefbee/popcorn-archives.git
    cd popcorn-archives
    ```

2.  **Create a Virtual Environment:** We strongly recommend using a virtual environment.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies:** Install the project in "editable" mode along with the development dependencies (like `pytest`).
    ```bash
    # Install main and development dependencies
    pip install -e .
    pip install -r requirements-dev.txt
    ```

4.  **Set Up a Test API Key:** To test features that interact with the API, you will need a free TMDb API key. Set it up using the `config` command.

## Running Tests
This project uses `pytest` for automated testing. Before submitting any changes, please make sure all tests pass.
```bash
pytest
```
New features should be accompanied by new tests.

## Submitting a Pull Request
1.  Create a new branch for your feature or bug fix (`git checkout -b feature/my-new-feature`).
2.  Make your changes and commit them with a clear, descriptive message.
3.  Ensure all tests pass.
4.  Push your branch to your fork (`git push origin feature/my-new-feature`).
5.  Open a pull request from your fork to the main `popcorn-archives` repository.

## Code Style
This project uses the **Black** code style. Please ensure your code is formatted with Black before submitting a pull request.

Thank you for helping make Popcorn Archives better!