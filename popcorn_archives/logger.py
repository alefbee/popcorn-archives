import logging
import os
import click
from . import config as config_manager

APP_NAME = "PopcornArchives"
APP_DIR = click.get_app_dir(APP_NAME)
LOG_FILE = os.path.join(APP_DIR, 'poparch.log')

# Create a custom logger
logger = logging.getLogger('poparch_logger')
logger.setLevel(logging.INFO)

# Create handlers
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)

def initialize_log_file():
    """Creates the log file with an initial message if it doesn't exist."""
    if not os.path.exists(LOG_FILE):
        initial_message = (
            "Log file created. Logging is currently disabled by default.\n"
            "To enable it, run the command: poparch config --logging on\n"
        )
        # Use a temporary handler to write the initial message
        temp_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        temp_handler.setFormatter(logging.Formatter('%(message)s'))
        temp_logger = logging.getLogger('temp_log_writer')
        temp_logger.addHandler(temp_handler)
        temp_logger.info(initial_message)
        temp_logger.removeHandler(temp_handler)

def log_info(message):
    """Logs an info message if logging is enabled."""
    if config_manager.is_logging_enabled():
        logger.info(message)

def log_error(message):
    """Logs an error message if logging is enabled."""
    if config_manager.is_logging_enabled():
        logger.error(message)

def clear_logs():
    """Clears the contents of the log file."""
    try:
        with open(LOG_FILE, 'w'):
            pass # Opening in 'w' mode and closing clears the file
        log_info("Log file cleared by user.")
        return True
    except Exception:
        return False