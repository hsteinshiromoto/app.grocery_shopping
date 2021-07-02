import subprocess
from pathlib import Path
from time import sleep

PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
DATA = PROJECT_ROOT / "data"

from src.get_prices import make_url_header
from src.web_api import get_status, make_webdriver


def get_supermarket_response(browser, supermarket):
    for url in make_url_header(["milk"], supermarket):
        browser.get(str(url) + "1")
        
        print(f"Waiting 10 s ...")
        sleep(10)
        print("Done.")
    return get_status(browser)

def test_woolworths_response():
    browser = make_webdriver()
    assert get_supermarket_response(browser, "woolworths") == 200

def test_coles_response():
    browser = make_webdriver()
    assert get_supermarket_response(browser, "coles") == 200
