import json

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import WebDriverException


class HTTPResponseError(WebDriverException):
    def __init__(self, message: str):
        super().__init__(message)


def make_webdriver(user_agent: str="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"):
    # adding webdriver options
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--no-sandbox')
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--user-data-dir=.temp/config/google-chrome')

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
