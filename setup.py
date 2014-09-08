# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

import aqi


here = os.path.abspath(os.path.dirname(__file__))

long_description = open(os.path.join(here, 'README.rst')).read()

# allow setup.py to be run from any path
#os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='python-aqi',
    version=aqi.__version__,
    author=aqi.__author__,
    author_email=aqi.__contact__,
    license=aqi.__license__,
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    url='https://github.com/hrbonz/python-aqi',
    description='A library to convert between AQI value and pollutant '
    'concentration (µg/m³ or ppm)',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    keywords='air quality pm2.5 EPA MEP',
)
