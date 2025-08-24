import configparser
import os
import click

APP_NAME = "PopcornArchives"
APP_DIR = click.get_app_dir(APP_NAME)
CONFIG_FILE = os.path.join(APP_DIR, 'config.ini')

def save_api_key(api_key):
    """Saves the TMDb API key to the config file."""
    os.makedirs(APP_DIR, exist_ok=True)
    config = configparser.ConfigParser()
    config['TMDB'] = {'API_KEY': api_key}
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def get_api_key():
    """Reads the TMDb API key from the config file."""
    if not os.path.exists(CONFIG_FILE):
        return None
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    try:
        return config['TMDB']['API_KEY']
    except KeyError:
        return None
    
def save_logging_status(is_enabled: bool):
    """Saves the logging status to the config file."""
    os.makedirs(APP_DIR, exist_ok=True)
    config = configparser.ConfigParser()
    # Read existing config to not overwrite API key
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    if 'SETTINGS' not in config:
        config['SETTINGS'] = {}
    config['SETTINGS']['LOGGING'] = 'on' if is_enabled else 'off'
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def is_logging_enabled():
    """Checks if logging is enabled in the config file."""
    if not os.path.exists(CONFIG_FILE):
        return False
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    try:
        return config.getboolean('SETTINGS', 'LOGGING')
    except (configparser.NoSectionError, configparser.NoOptionError):
        return False # Default to off if not set