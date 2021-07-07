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


class EmptyDataFrameError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def pre_process(data: pd.DataFrame):

    data['price'] = pd.to_numeric(data['price'], errors='coerce')
    data['unit_price'] = pd.to_numeric(data['unit_price'], errors='coerce')

    return data


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

            data = pd.concat([data, shopping_list])

        if data.empty:
            msg = "No data was obtained."
            raise EmptyDataFrameError(msg)

    data = pre_process(data)

    data.to_csv(str(DATA / "interim" / "data.csv"), index=False)

    # Agregate to grocery list
    agg_price = data.groupby(["category", "supermarket"])["price"].mean().to_frame("average price").reset_index()

    # Agregate to grocery list
    supermarket_comparison = agg_price.groupby(["supermarket"])["average price"].sum()

    return supermarket_comparison


if __name__ == "__main__":
    product_categories = ["full cream milk", "eggs", "banana", "nappies"]
    data = pd.read_csv(str(PROJECT_ROOT / 'data' / "interim" / "data.csv"))
    main(product_categories, data=data)
