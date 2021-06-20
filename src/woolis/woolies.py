from bs4 import BeautifulSoup as soup
from selenium import webdriver
from urllib.request import urlopen
from time import sleep
from woolies_helper import *
import json
from itertools import product
import re
# adding webdriver options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument('--no-sandbox')
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--profile-directory=Default')
options.add_argument('--user-data-dir=~/.config/google-chrome')
driver = webdriver.Chrome(options=options)

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

# list of url section
products_list = ["milk", "eggs", "banana", "nappies"]
url_header = [f'https://www.woolworths.com.au/shop/search/products?searchTerm={item}&pageNumber=' for item in products_list]


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
with open('wooliesData.json', 'w') as outfile:
    json.dump(full_list, outfile, default=myconverter)

print(len(arr))