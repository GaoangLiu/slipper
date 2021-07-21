#!/bin/bash

python3 setup.py sdist bdist_wheel
# python3 -m twine upload --repository-url https://test.pypi.org/legacy/ --skip-existing dist/*
python3 -m twine upload -r formal --skip-existing dist/*
python3 -m twine upload -r test --skip-existing dist/*

bash clear_eggs.sh

rm -r dist/*