import argparse
from datetime import datetime
import re
import subprocess
import sys
from pathlib import Path
from time import sleep

PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))

from src.get_prices import Coles, Woolworths

def test_coles_url_response(supermarket=Coles(), product_category: str="milk"
                        ,page_number: int=1):

    url = supermarket.url(product_category, page_number)
    supermarket.get_page_source(url)
    
    assert True


def test_woolworths_url_response(supermarket=Woolworths(), product_category: str="milk"
                        ,page_number: int=1):

    url = supermarket.url(product_category, page_number)
    supermarket.get_page_source(url)
    
    assert True