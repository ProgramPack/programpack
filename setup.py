#!/usr/bin/env python3
from setuptools import setup, find_packages
setup(
    name = 'programpack',
    version = '0.0.1',
    author = 'VBPROGER',
    py_modules = ['programpack'],
    install_requires = [open('requirements.txt', 'r+').read()],
    packages = find_packages(),
    python_requires = '>=3.10',
)
