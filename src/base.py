import argparse
from datetime import datetime
from enum import Enum, auto


class SupermarketNames(Enum):
    """Supermarket

    Args:
        Enum ([type]): [description]

    Returns:
        [type]: [description]
    """

    woolworths = auto()
    coles = auto()
    aldi = auto()
    iga = auto()


def str_to_supermarketnames(supermarket: str) -> SupermarketNames:
    if supermarket.lower() == "woolworths":
        return SupermarketNames.woolworths

    elif supermarket.lower() == "coles":
        return SupermarketNames.coles

    elif supermarket.lower() == "aldi":
        return SupermarketNames.aldi

    elif supermarket.lower() == "iga":
        return SupermarketNames.iga

    else:
        msg = f"Expected supermarket name to be either Woolworths, Coles, "\
            f"Aldi or IGA. Got {supermarket}."
        raise NotImplementedError(msg)


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