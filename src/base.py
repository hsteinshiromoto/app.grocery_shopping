import argparse
from datetime import datetime

from selenium import webdriver


def make_webdriver(user_agent: str="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"):
    # adding webdriver options
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--no-sandbox')
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--user-data-dir=~/.config/google-chrome')
    return webdriver.Chrome(options=options)


def convert_datetime(o):
    # convert datetime format to fit json
    if isinstance(o, datetime):
        return o.__str__()


def argparse_dtype_converter(a: str) -> bool:
    """Convert string to boolean

    Args:
        a (str): Variable to be converted to boolean

    Raises:
        argparse.ArgumentTypeError: Invalid variable

    Returns:
        bool: Boolean value
    """
    if isinstance(a, bool):
        return a
    
    elif a.lower() in ("yes", "y", "true", "t", "1"):
        return True

    elif a.lower() in ("no", "n", "false", "f", "0"):
        return False

    else:
        raise argparse.ArgumentTypeError(f"Expected boolean value. Got {a}.")