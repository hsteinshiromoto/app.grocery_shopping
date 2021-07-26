import re
from typing import Union

import numpy as np
import pandas as pd
from typeguard import typechecked


@typechecked
def pre_process(data: pd.DataFrame):

    data["Product Price"] = pd.to_numeric(data["Product Price"], errors='coerce')
    data["Unit Price"] = pd.to_numeric(data["Unit Price"], errors='coerce')

    return data


@typechecked
def measurement_cleaning(x: Union[str, float]): 

    if not isinstance(x, str):
        return []

    try:
        quantity = float(re.match(r"\d+", x).group())

    except AttributeError as err:
        traceback_msg = getattr(err, 'message', str(err))

        if "object has no attribute 'group'" in traceback_msg:
            return []

        raise err

    try:
        measurement = re.findall(r"[a-zA-z]+", x)[0]

    except IndexError as err:
        return []

    measurements_dict = {"g": "kg"
                    ,"ml": "l"
                    ,"ea": "each", "each": "each"
                    } 

    if measurement.lower() in ["kg", "l", "litre", "litres"]:
        return [quantity, measurement.lower()]

    elif measurement.lower() in ["g", "ml"]:
        return [quantity/1000, measurements_dict[measurement.lower()]]

    elif measurement.lower() in ["ea", "each"]:
        return [quantity, measurements_dict[measurement.lower()]]

    else:
        return [quantity, measurement]
