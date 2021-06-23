#!/usr/bin/env python3
#-*- coding: utf8 -*-

"""Scrape products from Woolworths

Returns:
    (dict): Prices, product name, datetime

References:
    [1] https://github.com/nguyenhailong253/grosaleries-web-scrapers
"""

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
from selenium import webdriver

PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
DATA = PROJECT_ROOT / "data"

sys.path.append(str(PROJECT_ROOT))


def scrapping(container_soup, category):
    
    containers = container_soup
    print('Total items in this page: ' + str(len(containers)))
    print('')
    
    arr = []
    
    for container in containers:
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
            "brand": product_brand,
            "name": product_name,
            "price": price,
            "quantity": product_quantity,
            "availability": availability,
            "datetime": date_now,
            "category": category,
            "pic": None
        }

        #return all the items in the page
        arr.append(obj)
    return arr, len(containers)


# convert datetime format to fit json
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


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


def make_url_header(product_categories: list[str]):
    return [f'https://shop.coles.com.au/a/national/everything/search/{item}?pageNumber=' for item in product_categories]


def main(product_categories: list[str], driver):
    # contain full list details for woolies
    full_list = []
    # seller = {
    #     "seller":
    #     {"name": "Coles",
    #     "description": "Coles Supermarket",
    #     "url": "https://shop.coles.com.au/a/national/home",
    #     "added_datetime": None
    #     }
    # }
    # full_list.append(seller)
    arr = []  # used to store every object

    url_header = make_url_header(product_categories)

    # scrapping for each section selected in the list
    for category in product_categories:
        n_items = 1
        i = 1

        while (n_items != 0):
            header = f'https://shop.coles.com.au/a/national/everything/search/{category}?pageNumber='
            url = header + str(i)
            print('page ' + str(i) + ": " + url)
            driver.get(url)
            sleep(10)
            html = driver.page_source
            page_soup = soup(html, 'html.parser')

            with open("coles.html", "w") as f:
                f.write(str(page_soup))

            container_soup = page_soup.findAll(
                'header', {'class': 'product-header'})

            arrSinglePage, n_items = scrapping(container_soup, category)
            for obj in arrSinglePage:
                arr.append(obj)
            i += 1

    # add the products array to the full list
    products = {'products': arr}
    full_list.append(products)

    # write a json file on all items
    with open(str(DATA / "raw" / f'coles.json'), 'w') as outfile:
        json.dump(full_list, outfile, default=myconverter)

    return pd.DataFrame.from_dict(full_list[0]['products'])


if __name__ == "__main__":
    product_categories = ["milk", "eggs", "banana", "nappies"]
    driver = make_webdriver()
    main(product_categories, driver)
