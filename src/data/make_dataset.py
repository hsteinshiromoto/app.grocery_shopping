import subprocess
import sys
import traceback
import warnings
from pathlib import Path

import pandas as pd
import yaml
from typeguard import typechecked

PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
DATA = PROJECT_ROOT / "data"

sys.path.append(str(PROJECT_ROOT))

import src.data.get_prices as gp
from src.base import SupermarketNames
from src.features.build_features import measurement_cleaning, pre_process


class EmptyDataFrameError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


@typechecked
def read_shopping_list(basename: str="shopping_list.yml", path: Path=DATA / "raw") -> pd.DataFrame:
    """Read shopping list from a yaml file.

    Args:
        basename (str, optional): Shopping list filename. Defaults to "shopping_list.yml".
        path (Path, optional): Path to load filename. Defaults to DATA/"raw".

    Returns:
        (pd.DataFrame): Shopping list
    """

    with open(str(path / basename), 'r') as stream:
        shopping_list = pd.DataFrame.from_dict(yaml.safe_load(stream))
    
    return shopping_list.T.reset_index().rename(columns={"index": "product"})


@typechecked
def get_most_frequent(data: pd.DataFrame, category: str="Category"
                    ,unit_quantity: str="Unit Quantity"):
    
    grouped = data.groupby([category, unit_quantity]).count().iloc[:, 0].to_frame("Count")
    grouped.reset_index(inplace=True)

    # Get index of the original for which `Count` is higher
    idx = grouped.groupby([category])["Count"].transform(max) == grouped["Count"]

    # Get most common `unit_quantity`
    return grouped.loc[idx, :]


@typechecked
def make_comparison(data: pd.DataFrame, most_frequent: pd.DataFrame):

    mask = (data["Category"].isin(most_frequent["Category"].values)) & \
            (data["Unit Quantity"].isin(most_frequent["Unit Quantity"].values))
    subset = data[mask]

    comparison = subset.groupby(["Category", "Supermarket"])["Unit Price"].mean().to_frame(name="Average Unit Price")
    comparison["Median Unit Price"] = subset.groupby(["Category", "Supermarket"])["Unit Price"].median()
    comparison.reset_index(inplace=True)
    comparison = comparison.merge(most_frequent[["Category", "Unit Quantity"]], how="left", on=["Category"]).drop_duplicates()

    return comparison, comparison.groupby("Supermarket")["Average Unit Price"].sum()


@typechecked
def main(product_categories: list[str]
    ,supermarkets_list: list[SupermarketNames]=[SupermarketNames.coles
                                                ,SupermarketNames.woolworths
                                                ,SupermarketNames.harris_farm]
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
    product_categories = ["full cream milk", "eggs", "banana", "nappies", "sourcream", "yogurt", "penne", "tomato sauce", "carrots", "tomatoes", "mince"]
    # data = pd.read_csv(str(PROJECT_ROOT / 'data' / "interim" / "data.csv"))
    # data=None
    main(product_categories)
