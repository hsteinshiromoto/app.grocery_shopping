import subprocess
import sys
import traceback
import warnings
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
DATA = PROJECT_ROOT / "data"

sys.path.append(str(PROJECT_ROOT))

import src.get_prices as gp
from src.base import SupermarketNames
from src.features.build_features import measurement_cleaning, pre_process
from src.data.make_dataset import get_most_frequent, make_comparison


class EmptyDataFrameError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def main(product_categories: list[str]
    ,supermarkets_list: list[SupermarketNames]=[SupermarketNames.coles
                                                ,SupermarketNames.woolworths]
    ,data: pd.DataFrame=None):

    if data is None:
        data = pd.DataFrame()

        for supermarket_name in supermarkets_list:
            try:
                shopping_list = gp.main(product_categories, supermarket_name)

            except ValueError:
                shopping_list = pd.DataFrame()
                warnings.warn(str(traceback.print_exc()))
                pass

            data = pd.concat([data, shopping_list.copy()])

        if data.empty:
            msg = "No data was obtained."
            raise EmptyDataFrameError(msg)

        data.to_csv(str(DATA / "interim" / "data.csv"), index=False)

    data = pre_process(data)

    data[["Unit Quantity", "Unity Measurement"]] = pd.DataFrame(data["Unit Quantity"].apply(measurement_cleaning).tolist()
                                                    , index=data.index)

    # Agregate to grocery list
    most_frequent = get_most_frequent(data)
    comparison_df, summary = make_comparison(data, most_frequent)

    # Agregate to grocery list
    comparison_df.to_csv(str(DATA / "processed" / "data.csv"), index=False)

    return comparison_df


if __name__ == "__main__":
    product_categories = ["full cream milk", "eggs", "banana", "nappies", "sourcream", "yogurt", "penne", "tomato sauce", "carrots", "tomatoes"]
    data = pd.read_csv(str(PROJECT_ROOT / 'data' / "interim" / "data.csv"))
    # data=None
    main(product_categories, data=data)
