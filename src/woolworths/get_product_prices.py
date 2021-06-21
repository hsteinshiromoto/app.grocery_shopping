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
            price = 'Unavailable at the momment'
            availability = False

        if(container.find('div', {'class': 'shelfProductTile-cupPrice'})):
            unit_price = container.find('div', {'class': 'shelfProductTile-cupPrice'}).text.strip()
        
        else:
            unit_price = 'Unavailable at the momment'
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
    return [f'https://www.woolworths.com.au/shop/search/products?searchTerm={item}&pageNumber=' for item in product_categories]


def main(product_categories: list[str], driver):
    # contain full list details for woolies
    full_list = []
    seller = {
        "seller":
        {"name": "Woolsworth",
        "description": "Woolsworth Supermarket",
        "url": "https://www.woolsworth.com.au",
        "added_datetime": None
        }
    }
    full_list.append(seller)
    arr = []  # used to store every object

    url_header = make_url_header(product_categories)

    # scrapping for each section selected in the list
    for header in url_header:
        n_items = 1
        i = 1

        while(n_items != 0):
            url = header + str(i)
            print('page ' + str(i) + ": " + url)
            driver.get(url)
            sleep(10)
            html = driver.page_source
            page_soup = soup(html, 'html.parser')

            with open("woolies.html", 'w') as f:
                f.write(str(page_soup))

            container_soup = page_soup.findAll(
                'div', {'class': 'shelfProductTile-information'})

            # for item in container_soup:
            #     print(f"product: {item.contents[2].text}, price: {item.contents[5].text}")

            if(len(container_soup) != 0):
                # category = page_soup.find(
                #     'h1', {'class': 'tileList-title'}).text.strip()
                pattern = '“([^"]*)”'
                category = page_soup.find(
                    'h1', {'class': 'searchContainer-title'}).text.strip()
            arrSinglePage, n_items = scrapping(container_soup, re.findall(pattern, category)[0])
            for obj in arrSinglePage:
                arr.append(obj)
            i = i + 1

    # add the products array to the full list
    products = {'products': arr}
    full_list.append(products)

    # write a json file on all items
    with open(str(DATA / "raw" / f'{datetime.datetime.now().date()}_woolworths.json'), 'w') as outfile:
        json.dump(full_list, outfile, default=myconverter)

if __name__ == "__main__":
    product_categories = ["milk", "eggs", "banana", "nappies"]
    driver = make_webdriver()
    main(product_categories, driver)