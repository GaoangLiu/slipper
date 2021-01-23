#!/bin/bash

rm -r dist/*
python3 setup.py sdist bdist_wheel
# python3 -m twine upload --repository-url https://test.pypi.org/legacy/ --skip-existing dist/*
python3 -m twine upload --skip-existing dist/*



# To install, using the following command
# python3 -m pip install -i https://test.pypi.org/simple/ slipper==0.0.3

