import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
from selenium import webdriver

PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
DATA = PROJECT_ROOT / "data"

sys.path.append(str(PROJECT_ROOT))

import src.coles.get_product_prices as coles
import src.woolworths.get_product_prices as woolies

# with open(str(DATA / "raw" / "coles.json")) as json_file:
#     coles = json.load(json_file)

# with open(str(DATA / "raw" / "woolworths.json")) as json_file:
#     woolies = json.load(json_file)


def make_webdriver():
    # adding webdriver options
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--user-data-dir=~/.config/google-chrome')
    return webdriver.Chrome(options=options)


def main(product_categories, driver):

    coles_data = coles.main(product_categories, driver)
    coles_data["supermarket"] = "Coles"
    woolies_data = woolies.main(product_categories, driver)
    woolies_data["supermarket"] = "Woolworths"

    data = pd.concat([coles_data, woolies_data])
    data['price'] = pd.to_numeric(data['price'], errors='coerce')

    data.to_csv(str(DATA / "interim" / "data.csv"), index=False)

    # Agregate to grocery list
    agg_price = data.groupby(["category", "supermarket"])["price"].mean().to_frame("average price").reset_index()

    # Agregate to grocery list
    supermarket_comparison = agg_price.groupby(["supermarket"])["average price"].sum()

if __name__ == "__main__":
    product_categories = ["milk", "eggs", "banana", "nappies"]
    driver = make_webdriver()
    main(product_categories, driver)
