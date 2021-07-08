import subprocess
from pathlib import Path

PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
DATA = PROJECT_ROOT / "data"

from src.web_api import WebAPI

def test_webapi():
    api = WebAPI()
    url = "https://www.google.com"
    _ = api.get_page_source(url)
    assert True
