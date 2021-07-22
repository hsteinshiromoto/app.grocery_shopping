import re

import pandas as pd
from typeguard import typechecked


@typechecked
def pre_process(data: pd.DataFrame):

    data["Product Price"] = pd.to_numeric(data["Product Price"], errors='coerce')
    data["Unit Price"] = pd.to_numeric(data["Unit Price"], errors='coerce')

    return data


@typechecked
def measurement_cleaning(x: str): 

    if not isinstance(x, str):
        return []

    quantity = float(re.match(r"\d+", x).group())
    measument = re.findall(r"[a-zA-z]+", x)[0]

    measuments_dict = {"g": "kg"
                    ,"ml": "l"
                    ,"ea": "each", "each": "each"
                    } 

    if measument.lower() in ["kg", "l"]:
        return [quantity, measument.lower()]

    elif measument.lower() in ["g", "ml"]:
        return [quantity/1000, measuments_dict[measument.lower()]]

    elif measument.lower() in ["ea", "each"]:
        return [quantity, measuments_dict[measument.lower()]]

    else:
        return [quantity, measument]
