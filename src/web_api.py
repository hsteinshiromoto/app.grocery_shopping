import json
import subprocess
from pathlib import Path
from abc import abstractmethod, ABC

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
DATA = PROJECT_ROOT / "data"


class HTTPResponseError(WebDriverException):
    def __init__(self, message: str):
        super().__init__(message)


class API(object):
    def __init__(self, user_agent: str="Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36") -> None:
        # adding webdriver options
        options = webdriver.ChromeOptions()
        # Necessary to avoid bugs
        options.add_argument('--no-sandbox')
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument('--headless')
        options.add_argument('--profile-directory=Default')

        # Avoid tab crashes
        options.add_argument("--start-maximized")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-data-dir=.temp/config/google-chrome')

        # Capabilities are necessary to get response code
        capabilities = DesiredCapabilities.CHROME.copy()
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
        
        self.driver = webdriver.Chrome(options=options, desired_capabilities=capabilities)


    def get_status(self) -> int:
        """Get HTTP status code

        References:
            [1] https://stackoverflow.com/questions/5799228/how-to-get-status-code-by-using-selenium-py-python-code
        """
        logs = self.driver.get_log('performance')

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


    def get_page_source(self, url: str):
        
        print(f"Reading {url} ...")
        self.driver.get(url)
        print("Done")
        status_code = self.get_status()

        output = self.driver.page_source

        if status_code != 200:
            with open(str(DATA / "raw" / f"{status_code}.html"), 'w') as f:
                f.write(str(output))
            
            msg = f"Expectes status = 200. Got {status_code}."
            raise HTTPResponseError(msg)

        return output