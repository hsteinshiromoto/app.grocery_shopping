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
├── Makefile
├── README.md
├── bin
│   ├── container.sh
│   ├── entrypoint.sh
│   ├── setup.py
│   ├── setup_python.sh
│   └── test_environment.py
├── data
│   ├── interim
│   ├── processed
│   └── raw
├── debian-requirements.txt
├── files
├── notebooks
│   ├── geckodriver.log
│   └── scrap.ipynb
├── poetry.lock
├── pyproject.toml
├── requirements.txt
├── src
│   ├── __main__.py
│   ├── api
│   │   └── web.py
│   ├── base.py
│   ├── data
│   │   ├── get_prices.py
│   │   └── make_dataset.py
│   ├── features
│   │   └── build_features.py
│   └── process.py
└── tests
    ├── test_get_prices.py
    └── test_web_api.py
```