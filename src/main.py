import subprocess
import sys
import traceback
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
DATA = PROJECT_ROOT / "data"

sys.path.append(str(PROJECT_ROOT))

import src.get_prices as gp
from src.web_api import make_webdriver


def pre_process(data: pd.DataFrame):

    data['price'] = pd.to_numeric(data['price'], errors='coerce')

    return data


def main(product_categories: list[str], supermarkets_list: list[str]=["coles", "woolworths"]):

    data = pd.DataFrame()
    driver = make_webdriver()

    for supermarket in supermarkets_list:
        try:
            shopping_list = gp.main(product_categories, driver, supermarket)

        except ValueError:
            shopping_list = pd.DataFrame()
            traceback.print_exc()
            pass

        data = pd.concat([data, shopping_list])

    data = pre_process(data)

    data.to_csv(str(DATA / "interim" / "data.csv"), index=False)

    # Agregate to grocery list
    agg_price = data.groupby(["category", "supermarket"])["price"].mean().to_frame("average price").reset_index()

    # Agregate to grocery list
    supermarket_comparison = agg_price.groupby(["supermarket"])["average price"].sum()

    return supermarket_comparison


if __name__ == "__main__":
    product_categories = ["full cream milk", "eggs", "banana", "nappies"]
    main(product_categories)
