import subprocess
import sys
import traceback
import warnings
from pathlib import Path

import pandas as pd
from typeguard import typechecked

PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
DATA = PROJECT_ROOT / "data"

sys.path.append(str(PROJECT_ROOT))

import src.get_prices as gp
from src.base import SupermarketNames
from src.data.make_dataset import get_most_frequent, make_comparison
from src.features.build_features import measurement_cleaning, pre_process

