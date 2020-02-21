#!/usr/bin/env bash
pipenv sync --dev
pipenv run coverage run run_tests.py
pipenv run coverage report -m