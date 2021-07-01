import json

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import WebDriverException


class HTTPResponseError(WebDriverException):
    def __init__(self, message: str):
        super().__init__(message)


def make_webdriver(user_agent: str="Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"):
    # adding webdriver options
    options = webdriver.ChromeOptions()
    # Necessary to avoid bugs
    options.add_argument('--no-sandbox')
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--headless')
    options.add_argument('--profile-directory=Default')

    # Maybe Unnecessary
    # options.add_argument("--start-maximized") # Unnecessary?
    # options.add_argument('--disable-gpu') # Unnecessary ?
    # options.add_argument('--disable-dev-shm-usage') # Unnecessary ?
    # options.add_argument('--user-data-dir=.temp/config/google-chrome') # Unnecessary ?

    # Capabilities are necessary to get response code
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
    
    return webdriver.Chrome(options=options, desired_capabilities=capabilities)
    

def get_status(webdriver: webdriver) -> int:
    """Get HTTP status code

    Args:
        webdriver (webdriver): Selenium webdriver object

    Returns:
        (int): HTTP status code

    References:
        [1] https://stackoverflow.com/questions/5799228/how-to-get-status-code-by-using-selenium-py-python-code
    """
    logs = webdriver.get_log('performance')

    for log in logs:
        if log['message']:
            d = json.loads(log['message'])
            try:
                content_type = 'text/html' in d['message']['params']['response']['headers']['content-type']
                response_received = d['message']['method'] == 'Network.responseReceived'
                if content_type and response_received:
                    return d['message']['params']['response']['status']
            except:
                pass
