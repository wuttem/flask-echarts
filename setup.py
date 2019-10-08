#!/usr/bin/python
# coding: utf8

import os

from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))


TEST_REQS = [
    'pytest',
    'mock'
]


REQUIRED_PACKAGES = [
    'flask',
    'werkzeug'
]

config = {
    'description': 'Flask echarts',
    'author': 'Matthias Wutte',
    'url': '',
    'download_url': 'https://github.com/wuttem',
    'author_email': 'matthias.wutte@gmail.com',
    'version': '0.1',
    'install_requires': REQUIRED_PACKAGES,
    'tests_require': TEST_REQS,
    'packages': find_packages(),
    'scripts': [],
    'name': 'flask-echarts'
}

setup(**config)