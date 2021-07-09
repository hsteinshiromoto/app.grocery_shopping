import argparse
from datetime import datetime
from enum import Enum, auto
from typing import Union

class SupermarketNames(Enum):
    """Supermarket

    Args:
        Enum ([type]): [description]

    Returns:
        [type]: [description]
    """

    woolworths = auto()
    coles = auto()
    harris_farm = auto()


def str_supermarketnames_map(supermarket: Union[str, SupermarketNames]
                        ,invert: bool=False) -> Union[str, SupermarketNames]:
    """Convert supermarket objects

    Args:
        supermarket (Union[str, SupermarketNames]): Supermarket name of or name object
        invert (bool, optional): Returns string. Defaults to False.

    Raises:
        NotImplementedError: Not available supermarket

    Returns:
        Union[str, SupermarketNames]: Name object
    """
    supermarket_name_obj_map = {"woolworths": SupermarketNames.woolworths
                            ,"coles": SupermarketNames.coles
                            ,"harris_farm": SupermarketNames.harris_farm
                            }

    supermarket_obj_name_map = {obj: supermarket for supermarket, obj in supermarket_name_obj_map.items()}

    try:
        if invert:
            return supermarket_obj_name_map[supermarket]

        return supermarket_name_obj_map[supermarket.lower()]

    except KeyError:
        msg = f"Expected supermarket name to be {supermarket_name_obj_map.keys()}. Got {supermarket}."
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
