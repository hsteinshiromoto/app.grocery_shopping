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

    data["Product Price"] = pd.to_numeric(data["Product Price"], errors='coerce')
    data["Unit Price"] = pd.to_numeric(data["Unit Price"], errors='coerce')

    return data


def get_most_frequent(data: pd.DataFrame, category: str="Category"
                    ,unit_quantity: str="Unit Quantity"):
    
    grouped = data.groupby([category, unit_quantity]).count().iloc[:, 0].to_frame("Count")
    grouped.reset_index(inplace=True)

    # Get index of the original for which `Count` is higher
    idx = grouped.groupby([category])['Count'].transform(max) == grouped['Count']

    # Get most common `unit_quantity`
    return grouped.loc[idx, :]


def make_comparison(data, most_frequent):

    mask = (data["Category"].isin(most_frequent["Category"].values)) & \
            (data["Unit Quantity"].isin(most_frequent["Unit Quantity"].values))
    subset = data[mask]

    grouped = subset.groupby(["Category", "Supermarket"])["Unit Price"].mean().to_frame(name="Average Unit Price")
    grouped["Median Unit Price"] = subset.groupby(["Category", "Supermarket"])["Unit Price"].median()
    grouped.reset_index(inplace=True)
    grouped.merge(subset[["Category", "Supermarket", "Unit Quantity"]], how="left", on=["Category", "Supermarket"]).drop_duplicates()
    grouped = grouped.merge(most_frequent[["Category", "Unit Quantity"]], how="left", on="Category")

    return grouped


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

    # Agregate to grocery list
    most_frequent = get_most_frequent(data)
    comparison_df = make_comparison(data, most_frequent)

    # Agregate to grocery list
    comparison_df.to_csv(str(DATA / "processed" / "data.csv"), index=False)

    return comparison_df


if __name__ == "__main__":
    product_categories = ["full cream milk", "eggs", "banana", "nappies", "sourcream", "yogurt", "penne", "tomato sauce", "carrots", "tomatoes"]
    data = pd.read_csv(str(PROJECT_ROOT / 'data' / "interim" / "data.csv"))
    data=None
    main(product_categories, data=data)
