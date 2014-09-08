# -*- coding: utf-8 -*-
import os
from setuptools import setup

import aqi


README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'python-aqi',
    version = aqi.__version__,
    author = aqi.__author__,
    author_email = aqi.__contact__,
    license = aqi.__license__,
    packages = ['aqi'],
    url = 'https://github.com/hrbonz/python-aqi',
    description='A library to convert between AQI value and pollutant '
    'concentration (µg/m³ or ppm)',
    long_description=README,
    classifiers=[
        'Development Status :: 6 - Mature',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
    ]
)
