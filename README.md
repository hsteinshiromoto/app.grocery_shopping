# 1. Description
Scraps price for list of items

# 2. Table of Contents

- [1. Description](#1-description)
- [2. Table of Contents](#2-table-of-contents)
- [3. Repository Structure](#3-repository-structure)

# 3. Repository Structure
```
.
├── Dockerfile
├── LICENSE
├── Makefile                        <- Build container
├── README.md
├── bin
│   ├── container.sh                <- Run container
│   ├── entrypoint.sh
│   ├── setup.py
│   ├── setup_python.sh
│   └── test_environment.py
├── data
│   ├── interim
│   ├── processed
│   └── raw
├── debian-requirements.txt         <- Necessary Debian packages
├── files
├── notebooks
├── poetry.lock             
├── pyproject.toml                  <- Repository Python dependencies
├── src                             <- Source files
│   ├── __main__.py
│   ├── api
│   │   └── web.py                  <- WEB Scraping API
│   ├── base.py
│   ├── data                        <- Scripts used for data manipulation
│   │   ├── get_prices.py           <- Scrap prices using WEB API
│   │   └── make_dataset.py         <- Build prices dataset
│   └── features                    <- Process dataset
│   │   └── build_features.py       <- Analysis of price dataset
└── tests                           <- Test source files
    ├── test_get_prices.py
    └── test_web_api.py
```