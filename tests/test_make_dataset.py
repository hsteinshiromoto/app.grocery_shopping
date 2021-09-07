import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml
import tempfile

PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
DATA = PROJECT_ROOT / "data"

sys.path.append(str(PROJECT_ROOT))

from src.data.make_dataset import *


@pytest.fixture(scope="module")
def make_shopping_list():
    test_list = {
        'soup': {'quantity': 2, 'unit': 'kg'},
        'milk': {'quantity': 1, 'unit': 'l'},
        'bread': {'quantity': 1, 'unit': 'kg'},
        'eggs': {'quantity': 1, 'unit': 'egg'},
        'cheese': {'quantity': 1, 'unit': 'kg'},
        'tomatoes': {'quantity': 1, 'unit': 'kg'},
        'potatoes': {'quantity': 1, 'unit': 'kg'},
        'onions': {'quantity': 1, 'unit': 'kg'},
        'chicken': {'quantity': 1, 'unit': 'kg'},
        'beef': {'quantity': 1, 'unit': 'kg'},
        'fish': {'quantity': 1, 'unit': 'kg'},
        'salt': {'quantity': 1, 'unit': 'kg'},
        'pepper': {'quantity': 1, 'unit': 'kg'},
        'oil': {'quantity': 1, 'unit': 'kg'},
        'sugar': {'quantity': 1, 'unit': 'kg'},
        'salt': {'quantity': 1, 'unit': 'kg'},
    }

    path = Path(tempfile.mkdtemp())
    basename = "test_shopping_list.yml"
    
    with open(str(path / basename), 'w') as outfile:
        yaml.dump(test_list, outfile, default_flow_style=False)

    return path

def teardown_function(make_shopping_list):
    basename = "test_shopping_list.yml"
    
    files = os.listdir(str(make_shopping_list))
    if basename in files:
        os.remove(basename)


def test_read_shopping_list(make_shopping_list):
    data = read_shopping_list(basename="test_shopping_list.yml", path=make_shopping_list)

    assert isinstance(data, pd.DataFrame)
