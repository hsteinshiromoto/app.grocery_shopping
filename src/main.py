import json
import pandas as pd

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], 
                                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8'))
DATA = PROJECT_ROOT / "data"

sys.path.append(str(PROJECT_ROOT))

with open(str(DATA / "raw" / "2021-06-20_coles.json")) as json_file:
    coles = json.load(json_file)

with open(str(DATA / "raw" / "2021-06-20_woolworths.json")) as json_file:
    woolies = json.load(json_file)


coles = pd.DataFrame.from_dict(coles[0]["products"])
coles["name"] = coles["brand"] + " " + coles["name"]
coles["supermarket"] = "Coles"
coles.drop(columns="brand", inplace=True)
coles.to_csv(str(DATA / "interim" / "coles.csv"))

woolies = pd.DataFrame.from_dict(woolies[1]["products"])
woolies["supermarket"] = "Woolworths"
woolies.to_csv(str(DATA / "interim" / "woolies.csv"))

data = pd.concat([coles, woolies])

sys.exit(0)