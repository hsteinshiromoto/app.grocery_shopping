#!/usr/bin/env python3
#-*- coding: utf8 -*-

"""Scrape products from Woolworths

Returns:
    (dict): Prices, product name, datetime

References:
    [1] https://github.com/nguyenhailong253/grosaleries-web-scrapers
"""

import argparse
import re
import subprocess
import sys
import traceback
import warnings
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from time import sleep

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as soup

PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
DATA = PROJECT_ROOT / "data"

sys.path.append(str(PROJECT_ROOT))

from src.base import SupermarketNames, str_supermarketnames_map
from src.api.web import HTTPResponseError, WebAPI


class Supermarket(ABC, WebAPI):
    quote = {
        "Availability": []
        ,"Brand": []
        ,"Category": []
        ,"Datetime": []
        ,"Name": []
        ,"Pic": []
        ,"Product Price": []
        ,"Product Quantity": []
        ,"Unit Price": []
        ,"Unit Quantity": []
    }

    @abstractmethod
    def product_info_container(self):
        pass

    @abstractmethod
    def url(self):
        pass

    @abstractmethod
    def get_products_list(self, container_soup, search_item: str):
        pass

    @abstractmethod
    def scrape_products(self):
        pass


class Woolworths(Supermarket):
    def __init__(self) -> None:
        super().__init__()
        self.name = SupermarketNames.woolworths

    def product_info_container(self):
        return ('div', {'class': 'shelfProductTile-information'})

    def url(self, search_item: str, page_number: int=1):
        return f"https://www.woolworths.com.au/shop/search/products?searchTerm={search_item}&pageNumber={page_number}"  

    def get_products_list(self, container_soup, search_item: str):
        return self.scrape_products(container_soup, search_item)

    def scrape_products(self, container_soup, category):
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
            price_dollar = container.find('span',{'class':'price-dollars'})
            price_cent = container.find('span', {'class': 'price-cents'})
            price = np.nan

            try:
                price = float(price_dollar.text + '.' + price_cent.text)

            except AttributeError:
                availability = False    

            unit_price = np.nan
            unit_quantity = np.nan

            try: 
                price_per_unit = container.find('div', {'class': 'shelfProductTile-cupPrice'}).text.strip().replace(" ", "").split("/")
                unit_price = float(price_per_unit[0].strip("$"))
                unit_quantity = price_per_unit[1]
                
            except AttributeError:
                pass

            self.quote["Availability"].append(availability)
            self.quote["Brand"].append(None)
            self.quote["Category"].append(category)
            self.quote["Datetime"].append(date_now)
            self.quote["Name"].append(product_name)
            self.quote["Pic"].append(None)
            self.quote["Product Price"].append(price)
            self.quote["Product Quantity"].append(np.nan)
            self.quote["Unit Price"].append(unit_price)
            self.quote["Unit Quantity"].append(unit_quantity)

        return pd.DataFrame.from_dict(self.quote)


class Coles(Supermarket):
    def __init__(self) -> None:
        super().__init__()
        self.name = SupermarketNames.coles

    def product_info_container(self):
        return ('header', {'class': 'product-header'})

    def url(self, search_item: str, page_number: int=1):
        search_item = search_item.replace(" ", "%20") 
        return f"https://shop.coles.com.au/a/national/everything/search/{search_item}?pageNumber={page_number}"
    
    def get_products_list(self, container_soup, search_item: str):
        return self.scrape_products(container_soup, search_item)

    def scrape_products(self, container_soup, category):
        
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
            date_now = datetime.now()        

            # check price and availability of each item
            if (container.find('span', {'class': 'dollar-value'})) :
                price = container.find('span', {'class': 'dollar-value'}).text.strip() + container.find('span', {'class': 'cent-value'}).text.strip()
                
            else:
                price = np.nan
                availability = False

            package_price = container.find('span', {'class': 'package-price'}).text.strip()
            if (package_price == '') | (not package_price):
                unit_price = np.nan
                unit_quantity = np.nan

            else:
                text = package_price.strip().split("per")
                unit_price = float(text[0].strip("$"))
                unit_quantity = text[1].strip()

            self.quote["Availability"].append(availability)
            self.quote["Brand"].append(product_brand)
            self.quote["Category"].append(category)
            self.quote["Datetime"].append(date_now)
            self.quote["Name"].append(product_name)
            self.quote["Pic"].append(None)
            self.quote["Product Price"].append(price)
            self.quote["Product Quantity"].append(product_quantity)
            self.quote["Unit Price"].append(unit_price)
            self.quote["Unit Quantity"].append(unit_quantity)

        return pd.DataFrame.from_dict(self.quote)


class HarrisFarm(Supermarket):
    def __init__(self) -> None:
        super().__init__()
        self.name = SupermarketNames.coles

    def product_info_container(self):
        return ('div', {'class': 'product-item columns large-2'})

    def url(self, search_item: str, page_number: int=1):
        search_item = search_item.replace(" ", "%20") 
        return f"https://www.harrisfarm.com.au/search?q={search_item}&hPP=24&idx=shopify_products&p={page_number}&is_v=1"
    
    def get_products_list(self, container_soup, search_item: str):
        return self.scrape_products(container_soup, search_item)

    def scrape_products(self, container_soup, category):
        
        arr = []
        
        for container in container_soup:
            # get the product name
            product_name = container.find("p", {"class": "title"}).text.strip()
            product_brand = None
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
            date_now = datetime.now()        

            # check price and availability of each item
            price = container.find('span', {'class': 'from_price'})
            if (price == '') | (not price):
                price = np.nan
                availability = False
                
            else:
                try:
                    price = float(container.find('span', {'class': 'from_price'}).text.strip().strip("$"))

                except ValueError:
                    price = np.nan

                

            package_price = container.find('span', {'class': 'compare_at_price unit_price'}).text.strip()
            if (package_price == '') | (not package_price):
                unit_price = np.nan
                unit_quantity = np.nan

            else:
                text = package_price.strip()
                
                unit_price = re.findall("\d+.*\d*", text)[0]
                unit_quantity = re.findall("\s\w+\Z", text)[0].strip()

            self.quote["Availability"].append(availability)
            self.quote["Brand"].append(product_brand)
            self.quote["Category"].append(category)
            self.quote["Datetime"].append(date_now)
            self.quote["Name"].append(product_name)
            self.quote["Pic"].append(None)
            self.quote["Product Price"].append(price)
            self.quote["Product Quantity"].append(product_quantity)
            self.quote["Unit Price"].append(unit_price)
            self.quote["Unit Quantity"].append(unit_quantity)

        return pd.DataFrame.from_dict(self.quote)


def main(product_categories: list[str], supermarket_name: SupermarketNames
        ,iteration_wait_time: int=10):

    supermarket_map = {supermarket_name.woolworths: Woolworths()
                    ,supermarket_name.coles: Coles()
                    ,supermarket_name.harris_farm: HarrisFarm()
                    } 
    supermarket = supermarket_map[supermarket_name]
    
    # url_header = make_url_header(product_categories, supermarket)
    shopping_list = pd.DataFrame()

    # scrapping for each section selected in the list
    for product_category in product_categories:
        n_items = 1
        page_number = 1

        while(n_items > 0):
            url = supermarket.url(product_category, page_number)

            try:
                print(f"Reading page# {page_number}")
                html = supermarket.get_page_source(url)
                print("Done.")
            
            except HTTPResponseError:
                warnings.warn(str(traceback.print_exc()))
                break

            finally:
                print(f"Waiting {iteration_wait_time}s ...")
                sleep(iteration_wait_time)
                print("Done.")

            page_soup = soup(html, 'html.parser')
            container_soup = page_soup.findAll(*supermarket.product_info_container())
            n_items = len(container_soup)
            print(f'Total items in this page: {n_items}')
            print('')

            if (n_items != 0):
                products_list = supermarket.get_products_list(container_soup, product_category)                

            else:
                continue

            shopping_list = pd.concat([shopping_list, products_list])

            page_number = page_number + 1

    shopping_list["Supermarket"] = str_supermarketnames_map(supermarket_name, invert=True)

    if shopping_list.empty:
        msg = f"Expected {supermarket_name} shopping list to be filled. Got empty."
        raise ValueError(msg)

    shopping_list.drop_duplicates(inplace=True)
    shopping_list.to_csv(str(DATA / "raw" / f"{supermarket_name}.csv"), index=False)

    return shopping_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Runs script with arguments")
    parser.add_argument("-s", "--supermarket", dest="supermarket", type=str_supermarketnames_map
                        ,help="Supermarket of choice")

    args = parser.parse_args()

    product_categories = ["full cream milk", "eggs", "banana", "nappies"]
    main(product_categories, args.supermarket)
