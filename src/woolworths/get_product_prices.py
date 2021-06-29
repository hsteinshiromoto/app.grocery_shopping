#!/usr/bin/env python3
#-*- coding: utf8 -*-

"""Scrape products from Woolworths

Returns:
    (dict): Prices, product name, datetime

References:
    [1] https://github.com/nguyenhailong253/grosaleries-web-scrapers
"""

import argparse
from datetime import datetime
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


def woolworths_scrapping(container_soup, category):  
    
    products_list = []
    
    for container in container_soup:
        # get the product name
        product_name = container.find("span", {"class": "sr-only"}).text.strip()
        # initial product is available
        availability = True
        unit_availability = True
        # get the date and time of the scrapping time
        date_now = datetime.now()        

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
            "availability": availability,
            "brand": None,
            "category": category,
            "datetime": date_now,
            "name": product_name,
            "pic": None,
            "price": price,
            "quantity": None,
            "unit_price": unit_price,
        }

        #return all the items in the page
        products_list.append(obj)

    yield from products_list


def coles_scrapping(container_soup, category):
    
    arr = []
    
    for container in container_soup:
        # get the product name
        product_name = container.find("span", {"class": "product-name"}).text.strip()
        product_brand = container.find("span", {"class": "product-brand"}).text.strip()
        package_sizes = container.find_all("span", {"class": "accessibility-inline"})
        pattern = re.compile(r"\d+\W{0,1}\w+", re.IGNORECASE)
        valid_sizes = [re.search(pattern, i.text.rstrip()) for i in package_sizes]
        product_quantity = [x for x in valid_sizes if x is not None]
        try:
            product_quantity = product_quantity[0].group(0)

        except IndexError:
            product_quantity = None
        # initial product is available
        availability = True
        # get the date and time of the scrapping time
        date_now = datetime.datetime.now()        

        # check price and availability of each item
        if (container.find('span', {'class': 'dollar-value'})) :
            price = container.find('span', {'class': 'dollar-value'}).text.strip() + container.find('span', {'class': 'cent-value'}).text.strip()
        else:
            price = np.nan
            availability = False

        obj = {
            "availability": availability,
            "brand": product_brand,
            "category": category,
            "datetime": date_now,
            "name": product_name,
            "pic": None,
            "price": price,
            "quantity": product_quantity,
            "unit_price": None,
        }

        #return all the items in the page
        arr.append(obj)

    yield from arr


def make_url_header(product_categories: list[str], supermarket: str) -> list[str]:
    supermarket_url_map = {"woolworths": [f'https://www.woolworths.com.au/shop/search/products?searchTerm={item}&pageNumber=' for item in product_categories]
                            ,"coles": [f'https://shop.coles.com.au/a/national/everything/search/{item}?pageNumber=' for item in product_categories]
                        }

    try:
        yield from supermarket_url_map[supermarket.lower()]

    except KeyError:
        msg = f"Expected supermarket to be either {supermarket_url_map.keys()}."\
              f"Got {supermarket.lower()}"
        raise ValueError(msg)


def main(product_categories: list[str], driver, supermarket: str, 
        save_html: bool=False):

    product_info_supermarket_dict = {"woolworths": ('div', {'class': 'shelfProductTile-information'})
                                    ,"coles": ('header', {'class': 'product-header'})
                                    }

    supermarket = supermarket.lower()

    if supermarket not in product_info_supermarket_dict.keys():
        msg = f"Expected supermarket to be in {product_info_supermarket_dict.keys()}. Got {supermarket}."
        raise ValueError(msg)
    
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

            container_soup = page_soup.findAll(*product_info_supermarket_dict[supermarket])

            n_items = len(container_soup)
            print(f'Total items in this page: {n_items}')
            print('')

            if (n_items != 0) & (supermarket == "woolworths"):
                pattern = '“([^"]*)”'
                category = page_soup.find(
                    'h1', {'class': 'searchContainer-title'}).text.strip()
                products_list = woolworths_scrapping(container_soup, re.findall(pattern, category)[0])
            
            elif (supermarket == "coles"):
                pattern = re.compile(r"https://shop.coles.com.au/a/national/everything/search/(.*)\WpageNumber=", re.IGNORECASE)
                products_list = coles_scrapping(container_soup, re.search(pattern, url).group(1))

            else:
                continue

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
