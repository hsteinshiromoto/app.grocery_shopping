from time import sleep
import subprocess
import sys
from pathlib import Path
from time import sleep

PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
DATA = PROJECT_ROOT / "data"

from src.get_prices import make_url_header
from src.web_api import make_webdriver, get_status

def get_supermarket_response(supermarket):
    for url in make_url_header(["milk"], supermarket):
        driver = make_webdriver()
        driver.get(str(url) + "1")
        
        print(f"Waiting 10 s ...")
        sleep(10)
        print("Done.")
    return get_status(driver)

def test_woolworths_response():
    assert get_supermarket_response("woolworths") == 200

def test_coles_response():
    assert get_supermarket_response("coles") == 200
