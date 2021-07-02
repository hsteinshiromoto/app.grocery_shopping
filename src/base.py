import argparse
from datetime import datetime


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