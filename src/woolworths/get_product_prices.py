#!/usr/bin/env python3
#-*- coding: utf8 -*-

"""Scrape products from Woolworths

Returns:
    (dict): Prices, product name, datetime

References:
    [1] https://github.com/nguyenhailong253/grosaleries-web-scrapers
"""

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path
from time import sleep

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as soup

PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
DATA = PROJECT_ROOT / "data"

sys.path.append(str(PROJECT_ROOT))

from src.base import convert_datetime, make_webdriver, argparse_dtype_converter


def scrapping(container_soup, category):  
    
    products_list = []
    
    for container in container_soup:
        # get the product name
        product_name = container.find("span", {"class": "sr-only"}).text.strip()
        # initial product is available
        availability = True
        unit_availability = True
        # get the date and time of the scrapping time
        date_now = datetime.datetime.now()        

        # check price and availability of each item
        if(container.find('span', {'class':'price-dollars'})):
            price_dollar = container.find('span',{'class':'price-dollars'})
            price_cent = container.find('span', {'class': 'price-cents'})
            price = price_dollar.text + '.' + price_cent.text

        else:
            price = np.nan
            availability = False

        if(container.find('div', {'class': 'shelfProductTile-cupPrice'})):
            unit_price = container.find('div', {'class': 'shelfProductTile-cupPrice'}).text.strip()
        
        else:
            unit_price = np.nan
            unit_availability = False

        obj = {
            "name": product_name,
            "price": price,
            "unit_price": unit_price,
            "availability": availability,
            "unit_availability": unit_availability,
            "datetime": date_now,
            "category": category,
            "pic": None
        }

        #return all the items in the page
        products_list.append(obj)

    yield from products_list


def make_url_header(product_categories: list[str], supermarket: str) -> list[str]:
    supermarket_url_map = {"woolworths": [f'https://www.woolworths.com.au/shop/search/products?searchTerm={item}&pageNumber=' for item in product_categories]}

    try:
        yield from supermarket_url_map[supermarket.lower()]

    except KeyError:
        msg = f"Expected supermarket to be either {supermarket_url_map.keys()}."\
              f"Got {supermarket.lower()}"
        raise ValueError(msg)


def main(product_categories: list[str], driver, supermarket: str, 
        save_html: bool=False):

    url_header = make_url_header(product_categories, supermarket)
    shopping_list = pd.DataFrame()

    # scrapping for each section selected in the list
    for url in url_header:
        n_items = 1
        i = 1

        while(n_items != 0):
            url = url + str(i)
            print(f"Reading page {i}: {url} ...")
            driver.get(url)
            print("Done.")

            print(f"Waiting 10 s ...")
            sleep(10)
            print("Done.")

            html = driver.page_source
            page_soup = soup(html, 'html.parser')

            if save_html:
                with open(str(DATA / "raw" / f"{url.split('/')[-1]}.html"), 'w') as f:
                    f.write(str(page_soup))

            container_soup = page_soup.findAll(
                'div', {'class': 'shelfProductTile-information'})

            n_items = len(container_soup)
            print(f'Total items in this page: {n_items}')
            print('')

            if(n_items != 0):
                pattern = '“([^"]*)”'
                category = page_soup.find(
                    'h1', {'class': 'searchContainer-title'}).text.strip()
                products_list = scrapping(container_soup, re.findall(pattern, category)[0])

                for product in products_list:
                    shopping_list = pd.concat([shopping_list, pd.DataFrame(product, index=[0])])
            i = i + 1

    shopping_list["supermarket"] = supermarket

    shopping_list.to_csv(str(DATA / "raw" / f"{supermarket}.csv"), index=False)

    return shopping_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Runs script with arguments")
    parser.add_argument("-s", "--save_html", dest="save_html", type=argparse_dtype_converter
                        ,help="Save requested html files.")
    parser.add_argument("-m", "--supermarket", dest="supermarket", type=str
                        ,help="Supermarket of choice")

    args = parser.parse_args()

    product_categories = ["milk", "eggs", "banana", "nappies"]
    driver = make_webdriver()
    main(product_categories, driver, args.supermarket, args.save_html)
