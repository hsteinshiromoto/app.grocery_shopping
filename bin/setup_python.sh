#!/bin/bash

## Test python environment is setup correctly
if [[ $1 = "test_environment" ]]; then
	echo ">>> Testing Python Environment"
	/usr/local/bin/test_environment.py
fi

## Install Python Dependencies
if [[ $1 = "requirements" ]]; then
	echo ">>> Installing Required Modules .."
	cd /usr/local/bin/
	pip3 install -U pip setuptools wheel
	
	cd /usr/local/
	poetry install --no-interaction --no-ansi
	echo ">>> Done!"

	# echo ">>> Getting virtual environment path ..."
	# VENV=/home/vscode/.cache/pypoetry/virtualenvs/$(ls ~/.cache/pypoetry/virtualenvs/)
	# export ${VENV}
	# echo ">>> Got ${VENV}"
fi
