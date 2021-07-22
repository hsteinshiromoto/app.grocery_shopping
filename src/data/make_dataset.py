import pandas as pd
from typeguard import typechecked


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
